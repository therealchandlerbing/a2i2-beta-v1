"""
Arcus WebSocket Channel Adapter

Provides a unified WebSocket API for Arcus Gateway. Allows web clients,
custom apps, or other services to connect via WebSocket for bi-directional
real-time communication.

Usage:
    from adapter_websocket import WebSocketAdapter

    adapter = WebSocketAdapter(
        host="0.0.0.0",
        port=18790,
        access_policy=AccessPolicy.PAIRING,
    )
    await adapter.connect()

Protocol:
    Client → Server:
    {
        "type": "message",
        "text": "Hello Arcus",
        "user_id": "user123",
        "metadata": {...}
    }

    Server → Client:
    {
        "type": "message",
        "text": "Response from Arcus",
        "message_id": "msg_abc123"
    }
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from channel_adapter import (
    AccessPolicy,
    AdapterType,
    ChannelAdapter,
    ChannelType,
    ChatContext,
    InboundMessage,
    MessageContentType,
    OutboundMessage,
    SendResult,
    UserIdentity,
)

logger = logging.getLogger("arcus.channel.websocket")


# =============================================================================
# CONNECTION METADATA
# =============================================================================

@dataclass
class ConnectionMetadata:
    """Metadata for a WebSocket connection."""
    connection_id: str
    websocket: Any
    user_id: Optional[str] = None
    authenticated: bool = False
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    rate_limit_tokens: float = 60.0  # Token bucket for rate limiting
    last_rate_limit_refill: float = field(default_factory=time.time)

    def touch(self) -> None:
        """Update last activity timestamp and increment message count."""
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1

    def check_rate_limit(self, max_rate: float = 60.0, refill_rate: float = 10.0) -> bool:
        """
        Token bucket rate limiting.

        Args:
            max_rate: Maximum tokens in bucket
            refill_rate: Tokens added per second

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        elapsed = now - self.last_rate_limit_refill

        # Refill tokens
        self.rate_limit_tokens = min(max_rate, self.rate_limit_tokens + elapsed * refill_rate)
        self.last_rate_limit_refill = now

        # Check if we have a token
        if self.rate_limit_tokens >= 1.0:
            self.rate_limit_tokens -= 1.0
            return True
        return False


class WebSocketAdapter(ChannelAdapter):
    """
    WebSocket channel adapter for unified API access.

    Features:
    - Bi-directional real-time messaging
    - JSON message protocol
    - Per-connection authentication
    - Broadcast capability
    - Connection management
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 18790,
        access_policy: AccessPolicy = AccessPolicy.OPEN,
        allowlist: Optional[list] = None,
        max_message_size: int = 1024 * 1024,  # 1MB
        heartbeat_interval: int = 30,  # seconds
        connection_timeout: int = 300,  # 5 minutes
        max_rate_per_minute: float = 60.0,
    ):
        super().__init__(
            name="websocket",
            channel_type=ChannelType.WEB,
            adapter_type=AdapterType.MESSAGING,
            access_policy=access_policy,
            allowlist=allowlist,
        )
        self.host = host
        self.port = port
        self.max_message_size = max_message_size
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        self.max_rate_per_minute = max_rate_per_minute

        self._server = None
        self._connections: Dict[str, ConnectionMetadata] = {}  # connection_id -> metadata
        self._user_connections: Dict[str, str] = {}  # user_id -> connection_id
        self._heartbeat_task: Optional[asyncio.Task] = None

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def connect(self) -> None:
        """Start the WebSocket server."""
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets package required: pip install websockets"
            )

        try:
            self._server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port,
                max_size=self.max_message_size,
            )
            self._connected = True

            # Start heartbeat task
            if self._heartbeat_task is None or self._heartbeat_task.done():
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            logger.info(f"WebSocket adapter listening on ws://{self.host}:{self.port}")
        except Exception as e:
            self._connected = False
            logger.error(f"WebSocket server start failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Stop the WebSocket server."""
        self._connected = False

        # Stop heartbeat
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

        # Close all connections gracefully
        for conn_meta in list(self._connections.values()):
            try:
                await conn_meta.websocket.close(code=1000, reason="Server shutting down")
            except Exception:
                pass

        self._connections.clear()
        self._user_connections.clear()

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        logger.info("WebSocket adapter disconnected")

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats and check for timeouts."""
        try:
            while self._connected:
                await asyncio.sleep(self.heartbeat_interval)

                # Send pings and check timeouts
                now = datetime.now(timezone.utc)
                to_close = []

                for conn_id, conn_meta in list(self._connections.items()):
                    # Check timeout
                    idle_seconds = (now - conn_meta.last_activity).total_seconds()
                    if idle_seconds > self.connection_timeout:
                        logger.info(f"Connection {conn_id[:8]} timed out after {idle_seconds}s")
                        to_close.append(conn_id)
                        continue

                    # Send heartbeat ping
                    try:
                        await conn_meta.websocket.ping()
                    except Exception as e:
                        logger.debug(f"Ping failed for {conn_id[:8]}: {e}")
                        to_close.append(conn_id)

                # Close timed out connections
                for conn_id in to_close:
                    conn_meta = self._connections.get(conn_id)
                    if conn_meta:
                        try:
                            await conn_meta.websocket.close(code=1001, reason="Connection timeout")
                        except Exception:
                            pass
                        del self._connections[conn_id]

                        # Remove from user mapping
                        if conn_meta.user_id and conn_meta.user_id in self._user_connections:
                            del self._user_connections[conn_meta.user_id]

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat loop error: {e}", exc_info=True)

    # -------------------------------------------------------------------------
    # Connection handling
    # -------------------------------------------------------------------------

    async def _handle_connection(self, websocket, path: str) -> None:
        """Handle a new WebSocket connection."""
        connection_id = str(uuid.uuid4())
        conn_meta = ConnectionMetadata(
            connection_id=connection_id,
            websocket=websocket,
        )
        self._connections[connection_id] = conn_meta
        logger.info(f"WebSocket connection {connection_id[:8]} from {websocket.remote_address}")

        try:
            async for raw_message in websocket:
                # Validate message size
                if len(raw_message) > self.max_message_size:
                    await self._send_error(websocket, f"Message too large (max {self.max_message_size} bytes)")
                    continue

                # Rate limiting check
                if not conn_meta.check_rate_limit(self.max_rate_per_minute):
                    await self._send_error(websocket, "Rate limit exceeded. Please slow down.")
                    logger.warning(f"Rate limit exceeded for connection {connection_id[:8]}")
                    continue

                try:
                    data = json.loads(raw_message)
                    await self._handle_message(connection_id, conn_meta, data)
                except json.JSONDecodeError as e:
                    await self._send_error(websocket, f"Invalid JSON: {str(e)}")
                except Exception as e:
                    logger.error(f"Message handling error: {e}", exc_info=True)
                    await self._send_error(websocket, "Internal server error")

        except Exception as e:
            logger.debug(f"Connection {connection_id[:8]} closed: {e}")
        finally:
            # Cleanup
            if connection_id in self._connections:
                del self._connections[connection_id]
            # Remove from user mapping
            if conn_meta.user_id and conn_meta.user_id in self._user_connections:
                del self._user_connections[conn_meta.user_id]
            logger.info(f"WebSocket connection {connection_id[:8]} cleaned up ({conn_meta.message_count} messages)")

    async def _handle_message(
        self,
        connection_id: str,
        conn_meta: ConnectionMetadata,
        data: Dict[str, Any]
    ) -> None:
        """Handle an inbound message from a WebSocket client."""
        # Update activity
        conn_meta.touch()

        msg_type = data.get("type", "message")
        websocket = conn_meta.websocket

        if msg_type == "auth":
            # Handle authentication
            user_id = data.get("user_id", "")
            access = self.check_access(user_id)
            if access.allowed:
                conn_meta.user_id = user_id
                conn_meta.authenticated = True
                self._user_connections[user_id] = connection_id
                await self._send_json(websocket, {
                    "type": "auth_success",
                    "user_id": user_id,
                    "connection_id": connection_id,
                })
                logger.info(f"Connection {connection_id[:8]} authenticated as user {user_id}")
            else:
                await self._send_json(websocket, {
                    "type": "auth_failed",
                    "reason": access.reason,
                })
                logger.warning(f"Auth failed for connection {connection_id[:8]}: {access.reason}")

        elif msg_type == "message":
            # Handle chat message
            user_id = conn_meta.user_id or data.get("user_id", f"ws-{connection_id[:8]}")
            text = data.get("text", "")

            if not text:
                await self._send_error(websocket, "Empty message")
                return

            # Create inbound message
            inbound = InboundMessage(
                id=data.get("message_id", str(uuid.uuid4())),
                channel=ChannelType.WEB,
                content_type=MessageContentType.TEXT,
                text=text,
                user=UserIdentity(
                    channel_user_id=user_id,
                    display_name=data.get("display_name", user_id),
                    arcus_user_id=data.get("arcus_user_id"),
                ),
                chat=ChatContext(
                    chat_id=connection_id,
                    is_group=False,
                    metadata={
                        "connection_id": connection_id,
                        "authenticated": conn_meta.authenticated,
                    },
                ),
                metadata=data.get("metadata", {}),
                raw_event=data,
            )

            # Dispatch to gateway
            await self._dispatch_message(inbound)

        elif msg_type == "ping":
            # Handle ping/pong for keepalive
            await self._send_json(websocket, {"type": "pong"})

        else:
            await self._send_error(websocket, f"Unknown message type: {msg_type}")

    # -------------------------------------------------------------------------
    # Messaging
    # -------------------------------------------------------------------------

    async def send(self, message: OutboundMessage) -> SendResult:
        """Send a message to a WebSocket client."""
        # Find the connection by chat_id (which is connection_id)
        connection_id = message.chat.chat_id
        conn_meta = self._connections.get(connection_id)

        if not conn_meta:
            return SendResult(success=False, error="Connection not found")

        try:
            await self._send_json(conn_meta.websocket, {
                "type": "message",
                "text": message.text,
                "message_id": str(uuid.uuid4()),
                "reply_to_id": message.reply_to_id,
                "metadata": message.metadata,
            })
            return SendResult(success=True, message_id=str(uuid.uuid4()))
        except Exception as e:
            logger.error(f"WebSocket send error: {e}", exc_info=True)
            return SendResult(success=False, error=str(e))

    async def _send_json(self, websocket: Any, data: Dict[str, Any]) -> None:
        """Send JSON data to a websocket."""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.debug(f"Failed to send to websocket: {e}")

    async def _send_error(self, websocket: Any, error: str) -> None:
        """Send an error message to a websocket."""
        await self._send_json(websocket, {
            "type": "error",
            "error": error,
        })

    # -------------------------------------------------------------------------
    # Broadcasting
    # -------------------------------------------------------------------------

    async def broadcast(self, message: str, exclude_connection: Optional[str] = None) -> int:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message text to broadcast
            exclude_connection: Optional connection ID to exclude

        Returns:
            Number of clients reached
        """
        count = 0
        for connection_id, conn_meta in list(self._connections.items()):
            if exclude_connection and connection_id == exclude_connection:
                continue
            try:
                await self._send_json(conn_meta.websocket, {
                    "type": "broadcast",
                    "text": message,
                })
                count += 1
            except Exception:
                pass
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_messages = sum(conn.message_count for conn in self._connections.values())
        authenticated = sum(1 for conn in self._connections.values() if conn.authenticated)

        return {
            "total_connections": len(self._connections),
            "authenticated_connections": authenticated,
            "authenticated_users": len(self._user_connections),
            "total_messages_handled": total_messages,
            "host": self.host,
            "port": self.port,
            "max_message_size": self.max_message_size,
            "heartbeat_interval": self.heartbeat_interval,
            "connection_timeout": self.connection_timeout,
        }
