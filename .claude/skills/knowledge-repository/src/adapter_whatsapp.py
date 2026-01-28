"""
Arcus WhatsApp Channel Adapter

Connects A2I2 to WhatsApp via the Baileys library (WhatsApp Web API)
through a Node.js bridge process. Supports text messages, voice message
transcription, group chats, and media.

Architecture:
    WhatsApp Web ← Baileys (Node.js) ← WebSocket ← This adapter (Python)

Usage:
    from adapter_whatsapp import WhatsAppAdapter

    adapter = WhatsAppAdapter(
        bridge_url="ws://127.0.0.1:18791",
        allowlist=["+15551234567"],
    )
    adapter.on_message(my_handler)
    await adapter.connect()

Requirements:
    - Node.js bridge running Baileys (see gateway_server.py for setup)
    - websockets (pip install websockets)
    - WhatsApp account paired via QR code
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from channel_adapter import (
    AccessPolicy,
    AdapterType,
    Attachment,
    ChannelAdapter,
    ChannelType,
    ChatContext,
    InboundMessage,
    MessageContentType,
    OutboundMessage,
    SendResult,
    UserIdentity,
)

logger = logging.getLogger("arcus.channel.whatsapp")


class WhatsAppAdapter(ChannelAdapter):
    """
    WhatsApp channel adapter using Baileys Node.js bridge.

    Communicates with a Node.js process running Baileys over a local
    WebSocket. The bridge handles WhatsApp Web protocol details while
    this adapter translates messages into the A2I2 format.

    Features:
    - Text messages (1:1 and group)
    - Voice message detection (marks for transcription)
    - Read receipts and typing indicators
    - Media attachments (images, documents)
    - Phone-number-based access control
    """

    def __init__(
        self,
        bridge_url: str = "ws://127.0.0.1:18791",
        access_policy: AccessPolicy = AccessPolicy.ALLOWLIST,
        allowlist: Optional[List[str]] = None,
        send_read_receipts: bool = True,
        send_typing_indicator: bool = True,
    ):
        super().__init__(
            name="whatsapp",
            channel_type=ChannelType.WHATSAPP,
            adapter_type=AdapterType.MESSAGING,
            access_policy=access_policy,
            allowlist=allowlist,
        )
        self.bridge_url = bridge_url
        self.send_read_receipts = send_read_receipts
        self.send_typing_indicator = send_typing_indicator
        self._ws = None
        self._listen_task: Optional[asyncio.Task] = None

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def connect(self) -> None:
        """Connect to the Baileys Node.js bridge via WebSocket."""
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets package required: pip install websockets"
            )

        try:
            self._ws = await websockets.connect(self.bridge_url)
            self._connected = True
            self._listen_task = asyncio.create_task(self._listen_loop())
            logger.info(f"WhatsApp adapter connected to bridge at {self.bridge_url}")
        except Exception as e:
            self._connected = False
            logger.error(f"WhatsApp bridge connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the Baileys bridge."""
        self._connected = False
        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None
        if self._ws:
            await self._ws.close()
            self._ws = None
        logger.info("WhatsApp adapter disconnected")

    # -------------------------------------------------------------------------
    # Messaging
    # -------------------------------------------------------------------------

    async def send(self, message: OutboundMessage) -> SendResult:
        """Send a message via WhatsApp."""
        if not self._ws or not self._connected:
            return SendResult(success=False, error="Not connected to WhatsApp bridge")

        try:
            payload = {
                "action": "send",
                "jid": message.chat.chat_id,
                "text": message.text,
            }

            if message.reply_to_id:
                payload["quoted_id"] = message.reply_to_id

            if message.attachments:
                attachment = message.attachments[0]
                payload["media"] = {
                    "type": attachment.content_type,
                    "caption": attachment.caption or "",
                }
                if attachment.url:
                    payload["media"]["url"] = attachment.url

            await self._ws.send(json.dumps(payload))

            # Wait for send confirmation
            response = await asyncio.wait_for(self._ws.recv(), timeout=10.0)
            data = json.loads(response)

            if data.get("status") == "sent":
                return SendResult(success=True, message_id=data.get("message_id"))
            return SendResult(success=False, error=data.get("error", "Unknown send error"))

        except asyncio.TimeoutError:
            return SendResult(success=False, error="Send timeout")
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}", exc_info=True)
            return SendResult(success=False, error=str(e))

    # -------------------------------------------------------------------------
    # Inbound message processing
    # -------------------------------------------------------------------------

    async def _listen_loop(self) -> None:
        """Listen for inbound messages from the Baileys bridge."""
        try:
            while self._connected and self._ws:
                try:
                    raw = await self._ws.recv()
                    data = json.loads(raw)
                    event_type = data.get("type", "")

                    if event_type == "message":
                        message = self._parse_message(data)
                        if message:
                            await self._dispatch_message(message)

                    elif event_type == "reaction":
                        user = UserIdentity(
                            channel_user_id=data.get("sender", ""),
                            display_name=data.get("sender_name"),
                        )
                        await self._dispatch_reaction(
                            data.get("message_id", ""),
                            data.get("emoji", ""),
                            user,
                        )

                    elif event_type == "connection":
                        status = data.get("status")
                        if status == "close":
                            logger.warning("WhatsApp bridge connection closed")
                            self._connected = False
                            break

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from WhatsApp bridge: {e}")
                except Exception as e:
                    if self._connected:
                        logger.error(f"WhatsApp listen error: {e}", exc_info=True)
                        await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass

    def _parse_message(self, data: Dict[str, Any]) -> Optional[InboundMessage]:
        """Parse a Baileys message event into an InboundMessage."""
        msg = data.get("message", {})
        sender = data.get("sender", "")
        chat_id = data.get("chat_id", "")
        is_group = data.get("is_group", False)

        # Determine content type
        content_type = MessageContentType.TEXT
        text = ""
        attachments = []

        if "text" in msg:
            text = msg["text"]
        elif "caption" in msg:
            text = msg["caption"]
            content_type = MessageContentType.IMAGE
        elif "audio" in msg:
            content_type = MessageContentType.AUDIO
            text = "[Voice message — transcription pending]"
            attachments.append(Attachment(
                content_type="audio/ogg",
                url=msg["audio"].get("url"),
            ))
        elif "image" in msg:
            content_type = MessageContentType.IMAGE
            attachments.append(Attachment(
                content_type="image/jpeg",
                url=msg["image"].get("url"),
                caption=msg["image"].get("caption"),
            ))
        elif "document" in msg:
            content_type = MessageContentType.DOCUMENT
            attachments.append(Attachment(
                content_type=msg["document"].get("mimetype", "application/octet-stream"),
                url=msg["document"].get("url"),
                filename=msg["document"].get("filename"),
            ))

        if not text and not attachments:
            return None

        # Send read receipt
        if self.send_read_receipts and self._ws:
            asyncio.create_task(self._send_read_receipt(data.get("message_id", ""), chat_id))

        return InboundMessage(
            id=data.get("message_id", ""),
            channel=ChannelType.WHATSAPP,
            content_type=content_type,
            text=text,
            user=UserIdentity(
                channel_user_id=sender,
                display_name=data.get("sender_name"),
            ),
            chat=ChatContext(
                chat_id=chat_id,
                is_group=is_group,
                group_name=data.get("group_name"),
            ),
            attachments=attachments,
            reply_to_id=data.get("quoted_id"),
            raw_event=data,
        )

    async def _send_read_receipt(self, message_id: str, chat_id: str) -> None:
        """Send a read receipt for a message."""
        if self._ws and self._connected:
            try:
                await self._ws.send(json.dumps({
                    "action": "read_receipt",
                    "message_id": message_id,
                    "jid": chat_id,
                }))
            except Exception:
                pass

    async def _send_typing(self, chat_id: str, duration: float = 2.0) -> None:
        """Send a typing indicator."""
        if self._ws and self._connected and self.send_typing_indicator:
            try:
                await self._ws.send(json.dumps({
                    "action": "typing",
                    "jid": chat_id,
                    "duration": duration,
                }))
            except Exception:
                pass
