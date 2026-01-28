"""
Arcus Gateway - Multi-Channel Control Plane

The central hub that connects all channel adapters to A2I2's memory and
intelligence layer. Inspired by Clawdbot's single WebSocket control plane,
adapted for A2I2's memory-aware, trust-gated architecture.

In standalone mode, this runs the full gateway server. When used as a
ClawdBot skill, only the ArcusMiddleware hooks are needed — the gateway
delegates all intelligence to memory_middleware.py.

Usage:
    from gateway import ArcusGateway

    gateway = ArcusGateway(config)
    gateway.register_adapter(whatsapp_adapter)
    gateway.register_adapter(discord_adapter)
    gateway.register_adapter(siri_adapter)
    await gateway.start()
"""

import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Coroutine, Dict, List, Optional

from channel_adapter import (
    ChannelAdapter,
    ChannelType,
    InboundMessage,
    OutboundMessage,
    SendResult,
    ChatContext,
    MessageContentType,
)
from memory_middleware import ArcusMiddleware, MiddlewareConfig

logger = logging.getLogger("arcus.gateway")


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class GatewayConfig:
    """Configuration for the Arcus Gateway."""
    # Server
    host: str = "127.0.0.1"
    ws_port: int = 18790  # Avoids Clawdbot's 18789
    http_port: int = 8080  # For webhook adapters (Siri)

    # Security
    gateway_auth_token: str = ""  # Required in production — rejects unauthenticated requests

    # Database
    supabase_url: str = ""
    supabase_key: str = ""

    # AI
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"

    # Memory
    max_context_tokens: int = 8000
    memory_injection_enabled: bool = True
    auto_learn_enabled: bool = True

    # Session
    session_timeout_minutes: int = 30
    max_sessions: int = 100

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("ARCUS_GATEWAY_HOST", "127.0.0.1"),
            ws_port=int(os.getenv("ARCUS_GATEWAY_WS_PORT", "18790")),
            http_port=int(os.getenv("ARCUS_GATEWAY_HTTP_PORT", "8080")),
            gateway_auth_token=os.getenv("GATEWAY_AUTH_TOKEN", ""),
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            default_model=os.getenv("ARCUS_DEFAULT_MODEL", "claude-sonnet-4-20250514"),
            max_context_tokens=int(os.getenv("ARCUS_MAX_CONTEXT_TOKENS", "8000")),
            memory_injection_enabled=os.getenv("ARCUS_MEMORY_INJECTION", "true").lower() == "true",
            auto_learn_enabled=os.getenv("ARCUS_AUTO_LEARN", "true").lower() == "true",
            session_timeout_minutes=int(os.getenv("ARCUS_SESSION_TIMEOUT", "30")),
            max_sessions=int(os.getenv("ARCUS_MAX_SESSIONS", "100")),
        )


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@dataclass
class GatewaySession:
    """Tracks a conversation session across channels."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    channel: ChannelType = ChannelType.WEB
    chat_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    memory_injected: bool = False
    timeout_minutes: int = 30

    @property
    def is_expired(self) -> bool:
        """Check if session has timed out."""
        return (datetime.now(timezone.utc) - self.last_activity) > timedelta(minutes=self.timeout_minutes)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1


class SessionManager:
    """Manages gateway sessions with automatic cleanup."""

    def __init__(self, max_sessions: int = 100, timeout_minutes: int = 30):
        self._sessions: Dict[str, GatewaySession] = {}
        self._user_sessions: Dict[str, str] = {}  # user_key -> session_id
        self.max_sessions = max_sessions
        self.timeout_minutes = timeout_minutes

    def _user_key(self, user_id: str, channel: ChannelType, chat_id: str) -> str:
        return f"{channel.value}:{user_id}:{chat_id}"

    def get_or_create(
        self, user_id: str, channel: ChannelType, chat_id: str
    ) -> GatewaySession:
        """Get existing session or create a new one."""
        key = self._user_key(user_id, channel, chat_id)

        # Return existing if active
        if key in self._user_sessions:
            session_id = self._user_sessions[key]
            session = self._sessions.get(session_id)
            if session and not session.is_expired:
                session.touch()
                return session
            # Clean up expired
            if session_id in self._sessions:
                del self._sessions[session_id]
            del self._user_sessions[key]

        # Enforce limit
        if len(self._sessions) >= self.max_sessions:
            self._cleanup_expired()

        # Create new
        session = GatewaySession(
            user_id=user_id,
            channel=channel,
            chat_id=chat_id,
            timeout_minutes=self.timeout_minutes,
        )
        self._sessions[session.id] = session
        self._user_sessions[key] = session.id
        logger.info(f"New session {session.id[:8]} for {key}")
        return session

    def end(self, session_id: str) -> Optional[GatewaySession]:
        """End a session and return it for cleanup."""
        session = self._sessions.pop(session_id, None)
        if session:
            key = self._user_key(session.user_id, session.channel, session.chat_id)
            self._user_sessions.pop(key, None)
            logger.info(f"Ended session {session_id[:8]}")
        return session

    def list_active(self) -> List[GatewaySession]:
        """List all active (non-expired) sessions."""
        self._cleanup_expired()
        return list(self._sessions.values())

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        expired = [sid for sid, s in self._sessions.items() if s.is_expired]
        for sid in expired:
            self.end(sid)
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


# =============================================================================
# EVENT SYSTEM
# =============================================================================

@dataclass
class GatewayEvent:
    """An event emitted by the gateway."""
    type: str               # e.g., "message.received", "session.created"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    channel: Optional[ChannelType] = None
    data: Dict[str, Any] = field(default_factory=dict)


EventListener = Callable[[GatewayEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Simple async event bus for gateway events."""

    def __init__(self):
        self._listeners: Dict[str, List[EventListener]] = {}

    def on(self, event_type: str, listener: EventListener) -> None:
        """Subscribe to an event type."""
        self._listeners.setdefault(event_type, []).append(listener)

    async def emit(self, event: GatewayEvent) -> None:
        """Emit an event to all subscribers."""
        listeners = self._listeners.get(event.type, []) + self._listeners.get("*", [])
        for listener in listeners:
            try:
                await listener(event)
            except Exception as e:
                logger.error(f"Event listener error for {event.type}: {e}", exc_info=True)


# =============================================================================
# AI MESSAGE PROCESSOR (uses ArcusMiddleware)
# =============================================================================

class MessageProcessor:
    """
    Processes inbound messages through the AI model with memory context.

    Delegates to ArcusMiddleware for:
    1. Memory context injection (pre-message hook)
    2. Model routing via ModelRouter
    3. Learning extraction (post-message hook)
    4. Trust ledger logging
    """

    def __init__(self, config: GatewayConfig, middleware: ArcusMiddleware):
        self.config = config
        self.middleware = middleware

    async def process(
        self, message: InboundMessage, session: GatewaySession
    ) -> str:
        """
        Process an inbound message and return a text response.

        Flow:
        1. Pre-message hook (memory injection, model routing)
        2. Build prompt with conversation history
        3. Call AI model
        4. Post-message hook (learning extraction, trust logging)
        """
        user_id = message.user.arcus_user_id or message.user.channel_user_id
        channel = message.channel.value

        # 1. Pre-message hook — memory injection + model routing
        pre_result = await self.middleware.pre_message(
            text=message.text,
            user_id=user_id,
            channel=channel,
            chat_id=message.chat.chat_id,
        )

        # 2. Build system prompt with memory context
        system_prompt = self._build_system_prompt(session, pre_result.get("system_context", ""))

        # 3. Build messages with conversation history
        messages = list(pre_result.get("history", []))
        messages.append({"role": "user", "content": message.text})

        # 4. Call AI model
        try:
            response = await self._call_model(system_prompt, messages)
        except Exception as e:
            logger.error(f"Model call failed: {e}", exc_info=True)
            response = "I'm having trouble processing that right now. Please try again."

        # 5. Post-message hook — learning extraction + trust logging
        try:
            await self.middleware.post_message(
                user_text=message.text,
                ai_response=response,
                user_id=user_id,
                channel=channel,
                chat_id=message.chat.chat_id,
            )
        except Exception as e:
            logger.error(f"Post-message hook failed: {e}", exc_info=True)

        return response

    def _build_system_prompt(self, session: GatewaySession, context_block: str) -> str:
        """Build the system prompt with memory context."""
        parts = [
            "You are Arcus, an AI Chief of Staff built by Arcus Innovation Studios.",
            "You remember context across sessions and learn from every interaction.",
            f"Channel: {session.channel.value}",
            f"Session messages: {session.message_count}",
        ]

        if context_block:
            parts.append(context_block)

        return "\n".join(parts)

    async def _call_model(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """
        Call the AI model with full conversation history.

        Tries Claude first, falls back to Gemini.
        """
        # Try Claude
        if self.config.anthropic_api_key:
            try:
                return await self._call_claude(system_prompt, messages)
            except Exception as e:
                logger.warning(f"Claude call failed, trying Gemini: {e}")

        # Try Gemini
        if self.config.gemini_api_key:
            try:
                return await self._call_gemini(system_prompt, messages)
            except Exception as e:
                logger.error(f"Gemini call also failed: {e}")

        return "I'm unable to process your request right now. Please check API configuration."

    async def _call_claude(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Call Anthropic Claude API with conversation history."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.config.anthropic_api_key)
        response = await client.messages.create(
            model=self.config.default_model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    async def _call_gemini(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """Call Google Gemini API with conversation history."""
        from google import genai

        # Format history for Gemini
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in messages
        )
        full_prompt = f"{system_prompt}\n\n{history_text}"

        client = genai.Client(api_key=self.config.gemini_api_key)
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        return response.text


# =============================================================================
# ARCUS GATEWAY - MAIN CLASS
# =============================================================================

class ArcusGateway:
    """
    The Arcus Multi-Channel Gateway.

    Central control plane that connects channel adapters to A2I2's intelligence
    layer via ArcusMiddleware. Manages sessions, routes messages, and
    coordinates AI responses across all channels.

    The gateway can run in two modes:
    1. Standalone: Full server with adapters and AI processing
    2. ClawdBot skill: Only the middleware hooks are used

    Architecture (inspired by Clawdbot):
        Channels → Gateway → Middleware (pre-hook) → AI → Middleware (post-hook) → Channel

    Usage:
        config = GatewayConfig.from_env()
        gateway = ArcusGateway(config)

        gateway.register_adapter(WhatsAppAdapter(...))
        gateway.register_adapter(DiscordAdapter(...))
        gateway.register_adapter(SiriWebhookAdapter(...))

        await gateway.start()
    """

    def __init__(self, config: Optional[GatewayConfig] = None):
        self.config = config or GatewayConfig.from_env()
        self.sessions = SessionManager(
            max_sessions=self.config.max_sessions,
            timeout_minutes=self.config.session_timeout_minutes,
        )
        self.events = EventBus()

        # Security: warn if no auth token in production
        if not self.config.gateway_auth_token:
            env = os.getenv("NODE_ENV", "development")
            if env == "production":
                logger.warning(
                    "GATEWAY_AUTH_TOKEN is not set. The gateway will reject all "
                    "authenticated requests. Set GATEWAY_AUTH_TOKEN in your environment."
                )
            else:
                logger.info("GATEWAY_AUTH_TOKEN not set (dev mode — auth disabled)")

        # Initialize middleware (connects all A2I2 modules)
        self.middleware = ArcusMiddleware(MiddlewareConfig(
            supabase_url=self.config.supabase_url,
            supabase_key=self.config.supabase_key,
            memory_injection_enabled=self.config.memory_injection_enabled,
            max_context_tokens=self.config.max_context_tokens,
            auto_learn_enabled=self.config.auto_learn_enabled,
        ))

        self.processor = MessageProcessor(self.config, self.middleware)
        self._adapters: Dict[str, ChannelAdapter] = {}
        self._running = False
        self._command_handler: Optional[Callable] = None

    # -------------------------------------------------------------------------
    # Adapter registration
    # -------------------------------------------------------------------------

    def register_adapter(self, adapter: ChannelAdapter) -> None:
        """Register a channel adapter with the gateway."""
        self._adapters[adapter.name] = adapter
        adapter.on_message(self._handle_inbound)
        # Wire reaction handlers to middleware
        adapter.on_reaction(self._handle_reaction)
        logger.info(f"Registered adapter: {adapter.name} ({adapter.channel_type.value})")

    def set_command_handler(self, handler: Callable) -> None:
        """Set the handler for slash commands (from chat_commands module)."""
        self._command_handler = handler

    def get_adapter(self, name: str) -> Optional[ChannelAdapter]:
        """Get a registered adapter by name."""
        return self._adapters.get(name)

    def verify_auth_token(self, token: str) -> bool:
        """
        Verify a gateway auth token.

        Returns True if:
        - No GATEWAY_AUTH_TOKEN is configured (dev mode), OR
        - The provided token matches the configured token (constant-time comparison)
        """
        if not self.config.gateway_auth_token:
            return True  # Auth disabled (dev mode)
        import hmac
        return hmac.compare_digest(token, self.config.gateway_auth_token)

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def start(self) -> None:
        """Start the gateway and connect all adapters."""
        logger.info(f"Starting Arcus Gateway on {self.config.host}")
        logger.info(f"  WebSocket: ws://{self.config.host}:{self.config.ws_port}")
        logger.info(f"  HTTP:      http://{self.config.host}:{self.config.http_port}")

        self._running = True

        # Connect all adapters
        for name, adapter in self._adapters.items():
            try:
                await adapter.connect()
                logger.info(f"  ✓ {name} connected")
            except Exception as e:
                logger.error(f"  ✗ {name} failed to connect: {e}", exc_info=True)

        await self.events.emit(GatewayEvent(
            type="gateway.started",
            data={"adapters": list(self._adapters.keys())},
        ))

        logger.info(f"Gateway running with {len(self._adapters)} adapter(s)")

    async def stop(self) -> None:
        """Stop the gateway and disconnect all adapters."""
        logger.info("Stopping Arcus Gateway...")
        self._running = False

        # Flush all middleware sessions
        for key in list(self.middleware._sessions.keys()):
            session = self.middleware._sessions.get(key)
            if session:
                self.middleware._flush_session(session)

        for name, adapter in self._adapters.items():
            try:
                await adapter.disconnect()
                logger.info(f"  ✓ {name} disconnected")
            except Exception as e:
                logger.error(f"  ✗ {name} disconnect error: {e}")

        await self.events.emit(GatewayEvent(type="gateway.stopped"))
        logger.info("Gateway stopped")

    # -------------------------------------------------------------------------
    # Message handling
    # -------------------------------------------------------------------------

    async def _handle_inbound(self, message: InboundMessage) -> None:
        """
        Central message handler — called by all adapters.

        Flow:
        1. Resolve cross-channel identity
        2. Get or create session
        3. Emit event
        4. Send typing indicator
        5. Check for commands
        6. Process through AI with middleware hooks
        7. Send response back through adapter
        """
        if not self._running:
            return

        # Verify auth token if present in message metadata
        if self.config.gateway_auth_token:
            msg_token = message.metadata.get("auth_token", "") if hasattr(message, 'metadata') and message.metadata else ""
            if not self.verify_auth_token(msg_token):
                logger.warning(
                    f"Rejected unauthenticated message from {message.user.channel_user_id} "
                    f"on {message.channel.value}"
                )
                self.middleware.audit.log_auth_failure(
                    user_id=message.user.channel_user_id,
                    channel=message.channel.value,
                    reason="invalid_or_missing_token",
                )
                return

        # Resolve cross-channel identity
        user_id = message.user.arcus_user_id or message.user.channel_user_id
        resolved = self.middleware.resolve_identity(user_id, message.channel.value)
        if resolved:
            message.user.arcus_user_id = resolved

        # Get session
        session = self.sessions.get_or_create(
            user_id=message.user.arcus_user_id or user_id,
            channel=message.channel,
            chat_id=message.chat.chat_id,
        )

        # Emit event
        await self.events.emit(GatewayEvent(
            type="message.received",
            session_id=session.id,
            channel=message.channel,
            data={
                "user": user_id,
                "text_length": len(message.text),
                "content_type": message.content_type.value,
            },
        ))

        # Send typing indicator (non-blocking)
        self._send_typing_indicator(message)

        # Check for slash commands
        if message.text.startswith("/") and self._command_handler:
            try:
                response_text = await self._command_handler(message, session)
                if response_text:
                    await self._send_response(message, response_text)
                    return
            except Exception as e:
                logger.error(f"Command handler error: {e}", exc_info=True)

        # Process through AI with middleware hooks
        response_text = await self.processor.process(message, session)

        # Send response
        await self._send_response(message, response_text)

        # Emit response event
        await self.events.emit(GatewayEvent(
            type="message.responded",
            session_id=session.id,
            channel=message.channel,
            data={"response_length": len(response_text)},
        ))

    async def _handle_reaction(self, message_id: str, emoji: str, user: "UserIdentity", channel: ChannelType) -> None:
        """Handle reactions — delegate to middleware for reward signals."""
        try:
            await self.middleware.on_reaction(
                message_id=message_id,
                emoji=emoji,
                user_id=user.channel_user_id,
                channel=channel.value,
            )
        except Exception as e:
            logger.error(f"Reaction handling failed: {e}", exc_info=True)

    def _send_typing_indicator(self, message: InboundMessage) -> None:
        """Send a typing indicator (fire-and-forget)."""
        adapter = self._adapters.get(message.channel.value)
        if not adapter:
            for a in self._adapters.values():
                if a.channel_type == message.channel:
                    adapter = a
                    break

        if adapter and hasattr(adapter, '_send_typing'):
            asyncio.create_task(adapter._send_typing(message.chat.chat_id))

    async def _send_response(self, original: InboundMessage, text: str) -> None:
        """Send a response back through the originating channel, chunking if needed."""
        adapter = self._adapters.get(original.channel.value)
        if not adapter:
            for a in self._adapters.values():
                if a.channel_type == original.channel:
                    adapter = a
                    break

        if not adapter:
            logger.error(f"No adapter found for channel {original.channel.value}")
            return

        # Chunk long messages for WhatsApp (2000 char limit)
        max_len = 2000 if original.channel == ChannelType.WHATSAPP else 0
        if max_len and len(text) > max_len:
            chunks = [text[i:i + max_len] for i in range(0, len(text), max_len)]
            for chunk in chunks:
                result = await adapter.send(OutboundMessage(
                    text=chunk,
                    chat=original.chat,
                    reply_to_id=original.id,
                ))
                if not result.success:
                    logger.error(f"Failed to send chunk: {result.error}")
                    break
        else:
            result = await adapter.send(OutboundMessage(
                text=text,
                chat=original.chat,
                reply_to_id=original.id,
            ))
            if not result.success:
                logger.error(f"Failed to send response: {result.error}")

    # -------------------------------------------------------------------------
    # Status & info
    # -------------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Get gateway status summary."""
        middleware_status = self.middleware.status()
        return {
            "running": self._running,
            "adapters": {
                name: {
                    "connected": adapter.is_connected(),
                    "channel": adapter.channel_type.value,
                    "type": adapter.adapter_type.value,
                }
                for name, adapter in self._adapters.items()
            },
            "sessions": {
                "active": len(self.sessions.list_active()),
                "max": self.config.max_sessions,
            },
            "middleware": middleware_status,
            "config": {
                "memory_injection": self.config.memory_injection_enabled,
                "auto_learn": self.config.auto_learn_enabled,
                "default_model": self.config.default_model,
            },
        }
