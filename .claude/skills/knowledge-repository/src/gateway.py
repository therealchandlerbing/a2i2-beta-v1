"""
Arcus Gateway - Multi-Channel Control Plane

The central hub that connects all channel adapters to A2I2's memory and
intelligence layer. Inspired by Clawdbot's single WebSocket control plane,
adapted for A2I2's memory-aware, trust-gated architecture.

Usage:
    from gateway import ArcusGateway

    gateway = ArcusGateway(config)
    gateway.register_adapter(whatsapp_adapter)
    gateway.register_adapter(discord_adapter)
    gateway.register_adapter(siri_adapter)
    await gateway.start()
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    memory_injected: bool = False

    @property
    def is_expired(self) -> bool:
        """Check if session has timed out (default 30 min)."""
        return (datetime.utcnow() - self.last_activity) > timedelta(minutes=30)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
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
    timestamp: datetime = field(default_factory=datetime.utcnow)
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
# MEMORY CONTEXT INJECTOR
# =============================================================================

class MemoryContextInjector:
    """
    Injects relevant A2I2 memory context into messages before AI processing.

    Queries episodic, semantic, and relational memory to provide the AI with
    context about the user, their preferences, and relevant history.
    """

    def __init__(self, config: GatewayConfig):
        self.config = config
        self._supabase = None

    async def _get_client(self):
        """Lazy-init Supabase client."""
        if self._supabase is None and self.config.supabase_url:
            try:
                from supabase import create_client
                self._supabase = create_client(
                    self.config.supabase_url,
                    self.config.supabase_key,
                )
            except ImportError:
                logger.warning("supabase package not installed, memory injection disabled")
        return self._supabase

    async def get_context(self, user_id: str, query: str = "") -> Dict[str, Any]:
        """
        Retrieve relevant memory context for a user and query.

        Returns:
            Dict with keys: preferences, recent_episodes, relevant_entities, relationships
        """
        client = await self._get_client()
        if not client:
            return {"preferences": [], "recent_episodes": [], "relevant_entities": [], "relationships": []}

        context: Dict[str, Any] = {
            "preferences": [],
            "recent_episodes": [],
            "relevant_entities": [],
            "relationships": [],
        }

        try:
            # Fetch user preferences (procedural memory)
            prefs = client.table("arcus_procedural_memory").select(
                "procedure_name, content, confidence"
            ).eq("user_id", user_id).eq(
                "procedure_type", "preference"
            ).order("confidence", desc=True).limit(10).execute()
            context["preferences"] = prefs.data or []

            # Fetch recent episodic memories
            episodes = client.table("arcus_episodic_memory").select(
                "event_type, summary, significance"
            ).eq("user_id", user_id).order(
                "created_at", desc=True
            ).limit(5).execute()
            context["recent_episodes"] = episodes.data or []

            # Fetch relevant entities if query provided
            if query:
                entities = client.table("arcus_entities").select(
                    "name, entity_type, summary"
                ).eq("user_id", user_id).ilike(
                    "name", f"%{query[:50]}%"
                ).limit(5).execute()
                context["relevant_entities"] = entities.data or []

        except Exception as e:
            logger.error(f"Memory context fetch error: {e}", exc_info=True)

        return context

    def format_context_block(self, context: Dict[str, Any]) -> str:
        """Format memory context as a text block for AI injection."""
        parts = []

        if context.get("preferences"):
            prefs_text = "\n".join(
                f"- {p['procedure_name']}: {p['content']}"
                for p in context["preferences"][:5]
            )
            parts.append(f"**User Preferences:**\n{prefs_text}")

        if context.get("recent_episodes"):
            eps_text = "\n".join(
                f"- [{e['event_type']}] {e['summary']}"
                for e in context["recent_episodes"][:3]
            )
            parts.append(f"**Recent Activity:**\n{eps_text}")

        if context.get("relevant_entities"):
            ents_text = "\n".join(
                f"- {e['name']} ({e['entity_type']}): {e.get('summary', 'N/A')}"
                for e in context["relevant_entities"][:3]
            )
            parts.append(f"**Related Entities:**\n{ents_text}")

        return "\n\n".join(parts) if parts else ""


# =============================================================================
# AI MESSAGE PROCESSOR
# =============================================================================

class MessageProcessor:
    """
    Processes inbound messages through the AI model with memory context.

    Handles:
    1. Memory context injection
    2. Model routing (Claude/Gemini based on task)
    3. Response generation
    4. Auto-learning from interactions
    """

    def __init__(self, config: GatewayConfig, memory: MemoryContextInjector):
        self.config = config
        self.memory = memory

    async def process(
        self, message: InboundMessage, session: GatewaySession
    ) -> str:
        """
        Process an inbound message and return a text response.

        Args:
            message: The inbound message from any channel
            session: The active session for context

        Returns:
            Response text string
        """
        # Build context
        memory_context = {}
        if self.config.memory_injection_enabled:
            memory_context = await self.memory.get_context(
                user_id=message.user.arcus_user_id or message.user.channel_user_id,
                query=message.text,
            )

        context_block = self.memory.format_context_block(memory_context)

        # Build prompt
        system_prompt = self._build_system_prompt(session, context_block)

        # Route to model
        try:
            response = await self._call_model(system_prompt, message.text)
        except Exception as e:
            logger.error(f"Model call failed: {e}", exc_info=True)
            response = "I'm having trouble processing that right now. Please try again."

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
            parts.append(f"\n--- Memory Context ---\n{context_block}\n--- End Context ---")

        return "\n".join(parts)

    async def _call_model(self, system_prompt: str, user_message: str) -> str:
        """
        Call the AI model (Claude or Gemini) and return the response.

        Tries Claude first, falls back to Gemini.
        """
        # Try Claude
        if self.config.anthropic_api_key:
            try:
                return await self._call_claude(system_prompt, user_message)
            except Exception as e:
                logger.warning(f"Claude call failed, trying Gemini: {e}")

        # Try Gemini
        if self.config.gemini_api_key:
            try:
                return await self._call_gemini(system_prompt, user_message)
            except Exception as e:
                logger.error(f"Gemini call also failed: {e}")

        return "I'm unable to process your request right now. Please check API configuration."

    async def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """Call Anthropic Claude API."""
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.config.anthropic_api_key)
        response = await client.messages.create(
            model=self.config.default_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    async def _call_gemini(self, system_prompt: str, user_message: str) -> str:
        """Call Google Gemini API."""
        from google import genai

        client = genai.Client(api_key=self.config.gemini_api_key)
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nUser: {user_message}",
        )
        return response.text


# =============================================================================
# ARCUS GATEWAY - MAIN CLASS
# =============================================================================

class ArcusGateway:
    """
    The Arcus Multi-Channel Gateway.

    Central control plane that connects channel adapters to A2I2's intelligence
    layer. Manages sessions, routes messages, injects memory context, and
    coordinates AI responses across all channels.

    Architecture (inspired by Clawdbot):
        Channels → Gateway → Memory + AI → Response → Channel

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
        self.memory = MemoryContextInjector(self.config)
        self.processor = MessageProcessor(self.config, self.memory)
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
        logger.info(f"Registered adapter: {adapter.name} ({adapter.channel_type.value})")

    def set_command_handler(self, handler: Callable) -> None:
        """Set the handler for slash commands (from chat_commands module)."""
        self._command_handler = handler

    def get_adapter(self, name: str) -> Optional[ChannelAdapter]:
        """Get a registered adapter by name."""
        return self._adapters.get(name)

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
        1. Get or create session
        2. Emit event
        3. Check for commands
        4. Process through AI with memory context
        5. Send response back through adapter
        """
        if not self._running:
            return

        # Get session
        session = self.sessions.get_or_create(
            user_id=message.user.arcus_user_id or message.user.channel_user_id,
            channel=message.channel,
            chat_id=message.chat.chat_id,
        )

        # Emit event
        await self.events.emit(GatewayEvent(
            type="message.received",
            session_id=session.id,
            channel=message.channel,
            data={
                "user": message.user.channel_user_id,
                "text_length": len(message.text),
                "content_type": message.content_type.value,
            },
        ))

        # Check for slash commands
        if message.text.startswith("/") and self._command_handler:
            try:
                response_text = await self._command_handler(message, session)
                if response_text:
                    await self._send_response(message, response_text)
                    return
            except Exception as e:
                logger.error(f"Command handler error: {e}", exc_info=True)

        # Process through AI
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

    async def _send_response(self, original: InboundMessage, text: str) -> None:
        """Send a response back through the originating channel."""
        adapter = self._adapters.get(original.channel.value)
        if not adapter:
            # Try to find by channel type
            for a in self._adapters.values():
                if a.channel_type == original.channel:
                    adapter = a
                    break

        if not adapter:
            logger.error(f"No adapter found for channel {original.channel.value}")
            return

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
            "config": {
                "memory_injection": self.config.memory_injection_enabled,
                "auto_learn": self.config.auto_learn_enabled,
                "default_model": self.config.default_model,
            },
        }
