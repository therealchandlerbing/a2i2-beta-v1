"""
Arcus Siri Webhook Adapter

Provides an HTTP webhook endpoint for Apple Siri Shortcuts. Users create
an iOS Shortcut that captures voice input, POSTs to this webhook, and
speaks the response — enabling "Hey Siri, ask Arcus..." hands-free.

Architecture:
    "Hey Siri, ask Arcus..." → iOS Shortcut → HTTP POST → This adapter → AI → JSON response → Siri speaks

Usage:
    from adapter_siri import SiriWebhookAdapter

    adapter = SiriWebhookAdapter(
        api_secret="your-secret-key",
        host="0.0.0.0",
        port=8080,
    )
    adapter.on_message(my_handler)
    await adapter.connect()

Requirements:
    - pip install aiohttp
    - iOS Shortcut configured with "Get Contents of URL" action
    - API key shared with the Shortcut for auth

Shortcut Setup:
    1. Create new Shortcut named "Ask Arcus"
    2. Add "Dictate Text" action
    3. Add "Get Contents of URL":
       - URL: https://your-server.com/webhook/siri
       - Method: POST
       - Headers: Authorization: Bearer <your-key>
       - Body: JSON {"query": "<dictated text>", "device_id": "<device name>"}
    4. Add "Get Dictionary Value" for key "response"
    5. Add "Speak Text" with the response value
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict, List, Optional

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

logger = logging.getLogger("arcus.channel.siri")


class SiriWebhookAdapter(ChannelAdapter):
    """
    Siri Shortcuts webhook adapter.

    Runs an HTTP server that accepts POST requests from iOS Shortcuts.
    Each request contains transcribed voice input, and the response is
    JSON that the Shortcut reads back via Siri text-to-speech.

    Features:
    - Bearer token authentication
    - Device-based user identification
    - Voice-optimized concise responses
    - Timeout handling (iOS Shortcuts have ~30s limit)
    - Rate limiting per device
    """

    def __init__(
        self,
        api_secret: str = "",
        host: str = "0.0.0.0",
        port: int = 8080,
        path: str = "/webhook/siri",
        access_policy: AccessPolicy = AccessPolicy.ALLOWLIST,
        allowed_device_ids: Optional[List[str]] = None,
        max_response_length: int = 500,
    ):
        super().__init__(
            name="siri",
            channel_type=ChannelType.SIRI,
            adapter_type=AdapterType.WEBHOOK,
            access_policy=access_policy,
            allowlist=allowed_device_ids,
        )
        self.api_secret = api_secret
        self.host = host
        self.port = port
        self.path = path
        self.max_response_length = max_response_length
        self._app = None
        self._runner = None
        self._site = None
        self._pending_responses: Dict[str, asyncio.Future] = {}
        self._rate_limits: Dict[str, float] = {}  # device_id -> last_request_time
        self._rate_limit_seconds = 2.0

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def connect(self) -> None:
        """Start the HTTP webhook server."""
        try:
            from aiohttp import web
        except ImportError:
            raise ImportError(
                "aiohttp package required: pip install aiohttp"
            )

        self._app = web.Application()
        self._app.router.add_post(self.path, self._handle_webhook)
        self._app.router.add_get("/health", self._handle_health)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()

        self._connected = True
        logger.info(f"Siri webhook listening at http://{self.host}:{self.port}{self.path}")

    async def disconnect(self) -> None:
        """Stop the HTTP server."""
        self._connected = False
        if self._site:
            await self._site.stop()
        if self._runner:
            await self._runner.cleanup()
        # Cancel pending responses
        for future in self._pending_responses.values():
            if not future.done():
                future.set_result("Service shutting down.")
        self._pending_responses.clear()
        logger.info("Siri webhook adapter stopped")

    # -------------------------------------------------------------------------
    # Webhook handler
    # -------------------------------------------------------------------------

    async def _handle_webhook(self, request) -> Any:
        """Handle incoming POST from Siri Shortcuts."""
        from aiohttp import web

        # Authenticate
        if self.api_secret:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return web.json_response(
                    {"error": "Missing or invalid Authorization header"},
                    status=401,
                )
            token = auth_header[7:]
            if not hmac.compare_digest(token, self.api_secret):
                return web.json_response(
                    {"error": "Invalid API key"},
                    status=403,
                )

        # Parse body
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON body"},
                status=400,
            )

        query = body.get("query", "").strip()
        device_id = body.get("device_id", "unknown-device")
        shortcut_name = body.get("shortcut_name", "Ask Arcus")

        if not query:
            return web.json_response(
                {"error": "Missing 'query' field"},
                status=400,
            )

        # Rate limit
        now = time.time()
        last_request = self._rate_limits.get(device_id, 0)
        if now - last_request < self._rate_limit_seconds:
            return web.json_response(
                {"error": "Rate limited. Please wait a moment."},
                status=429,
            )
        self._rate_limits[device_id] = now

        # Access check
        if self.access_policy != AccessPolicy.OPEN:
            access = self.check_access(device_id)
            if not access.allowed:
                return web.json_response(
                    {"error": "Device not authorized. Contact admin for access."},
                    status=403,
                )

        # Create inbound message
        message = InboundMessage(
            channel=ChannelType.SIRI,
            content_type=MessageContentType.TEXT,
            text=query,
            user=UserIdentity(
                channel_user_id=device_id,
                display_name=device_id,
                metadata={"shortcut_name": shortcut_name},
            ),
            chat=ChatContext(
                chat_id=f"siri:{device_id}",
            ),
        )

        # Create a future for the response
        response_future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_responses[message.id] = response_future

        # Dispatch to gateway (handlers will call send() which resolves the future)
        await self._dispatch_message(message)

        # Wait for response (timeout at 25s to stay under Shortcuts' 30s limit)
        try:
            response_text = await asyncio.wait_for(response_future, timeout=25.0)
        except asyncio.TimeoutError:
            response_text = "I'm still thinking about that. Please try again in a moment."
        finally:
            self._pending_responses.pop(message.id, None)

        # Truncate for voice (Siri shouldn't read a novel)
        if len(response_text) > self.max_response_length:
            response_text = response_text[:self.max_response_length - 3] + "..."

        return web.json_response({
            "response": response_text,
            "query": query,
            "device_id": device_id,
            "timestamp": message.timestamp.isoformat(),
        })

    async def _handle_health(self, request) -> Any:
        """Health check endpoint."""
        from aiohttp import web
        return web.json_response({
            "status": "ok",
            "adapter": "siri",
            "connected": self._connected,
        })

    # -------------------------------------------------------------------------
    # Messaging (resolves webhook response)
    # -------------------------------------------------------------------------

    async def send(self, message: OutboundMessage) -> SendResult:
        """
        Send a response — resolves the pending webhook future.

        Unlike messaging adapters, the Siri adapter doesn't push messages.
        Instead, send() resolves the HTTP response that the Shortcut is
        waiting for.
        """
        # Find the pending response by reply_to_id or chat_id
        future = None
        if message.reply_to_id and message.reply_to_id in self._pending_responses:
            future = self._pending_responses.get(message.reply_to_id)

        if not future:
            logger.warning(f"Siri send called but no pending webhook response found for reply_to_id {message.reply_to_id}")
            return SendResult(success=False, error="No pending webhook request for the given message ID")
