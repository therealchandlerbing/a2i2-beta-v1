"""
Arcus Multi-Channel Gateway - Base Channel Adapter & Message Types

Provides the abstract base class for all channel adapters (WhatsApp, Discord,
Siri, etc.) and shared message types. Inspired by Clawdbot's channel adapter
pattern, adapted for A2I2's memory-aware architecture.

Usage:
    from channel_adapter import ChannelAdapter, InboundMessage, OutboundMessage

    class MyAdapter(ChannelAdapter):
        ...
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional


logger = logging.getLogger("arcus.channel")


# =============================================================================
# ENUMS
# =============================================================================

class ChannelType(Enum):
    """Supported channel types."""
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    SIRI = "siri"
    TELEGRAM = "telegram"
    WEB = "web"
    VOICE = "voice"


class AdapterType(Enum):
    """How the adapter communicates."""
    MESSAGING = "messaging"  # Persistent connection (WhatsApp, Discord)
    WEBHOOK = "webhook"      # HTTP request/response (Siri Shortcuts)


class AccessPolicy(Enum):
    """Channel access control policy."""
    OPEN = "open"            # Anyone can interact
    ALLOWLIST = "allowlist"  # Only pre-approved users
    PAIRING = "pairing"     # Users must pair with a code


class MessageContentType(Enum):
    """Types of message content."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    REACTION = "reaction"
    COMMAND = "command"


# =============================================================================
# DATA CLASSES - MESSAGE TYPES
# =============================================================================

@dataclass
class Attachment:
    """A media attachment on a message."""
    content_type: str          # MIME type
    url: Optional[str] = None  # Remote URL
    data: Optional[bytes] = None  # Raw bytes
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    caption: Optional[str] = None


@dataclass
class UserIdentity:
    """Identifies a user across channels."""
    channel_user_id: str       # Platform-specific ID (phone, Discord ID, etc.)
    display_name: Optional[str] = None
    arcus_user_id: Optional[str] = None  # Mapped A2I2 user ID
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatContext:
    """Identifies a chat/conversation context."""
    chat_id: str               # Platform-specific chat/channel ID
    is_group: bool = False
    group_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InboundMessage:
    """A message received from any channel."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    channel: ChannelType = ChannelType.WEB
    content_type: MessageContentType = MessageContentType.TEXT
    text: str = ""
    user: UserIdentity = field(default_factory=lambda: UserIdentity(channel_user_id="unknown"))
    chat: ChatContext = field(default_factory=lambda: ChatContext(chat_id="default"))
    attachments: List[Attachment] = field(default_factory=list)
    reply_to_id: Optional[str] = None
    raw_event: Optional[Any] = None  # Original platform event


@dataclass
class OutboundMessage:
    """A message to send to a channel."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    text: str = ""
    chat: ChatContext = field(default_factory=lambda: ChatContext(chat_id="default"))
    attachments: List[Attachment] = field(default_factory=list)
    reply_to_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SendResult:
    """Result of sending a message."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AccessDecision:
    """Result of an access check."""
    allowed: bool
    reason: str = ""
    user_id: Optional[str] = None  # Resolved A2I2 user ID


# Type alias for message handlers
MessageHandler = Callable[[InboundMessage], Coroutine[Any, Any, None]]
ReactionHandler = Callable[["str", "str", "UserIdentity", "ChannelType"], Coroutine[Any, Any, None]]


# =============================================================================
# ABSTRACT BASE CLASS
# =============================================================================

class ChannelAdapter(ABC):
    """
    Abstract base class for all channel adapters.

    Each adapter handles platform-specific connection management, message
    translation, and access control. The gateway core calls adapters through
    this uniform interface.

    Lifecycle:
        adapter = MyAdapter(config)
        await adapter.connect()
        adapter.on_message(my_handler)
        ...
        await adapter.disconnect()
    """

    def __init__(
        self,
        name: str,
        channel_type: ChannelType,
        adapter_type: AdapterType,
        access_policy: AccessPolicy = AccessPolicy.ALLOWLIST,
        allowlist: Optional[List[str]] = None,
    ):
        self.name = name
        self.channel_type = channel_type
        self.adapter_type = adapter_type
        self.access_policy = access_policy
        self.allowlist: List[str] = allowlist or []
        self._connected = False
        self._message_handlers: List[MessageHandler] = []
        self._reaction_handlers: List[ReactionHandler] = []
        self._logger = logging.getLogger(f"arcus.channel.{name}")

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the channel platform."""
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully disconnect from the channel platform."""
        ...

    def is_connected(self) -> bool:
        """Check if the adapter is currently connected."""
        return self._connected

    # -------------------------------------------------------------------------
    # Messaging
    # -------------------------------------------------------------------------

    def on_message(self, handler: MessageHandler) -> None:
        """Register a handler for inbound messages."""
        self._message_handlers.append(handler)

    def on_reaction(self, handler: ReactionHandler) -> None:
        """Register a handler for reactions (feedback signals)."""
        self._reaction_handlers.append(handler)

    @abstractmethod
    async def send(self, message: OutboundMessage) -> SendResult:
        """Send a message to the channel."""
        ...

    async def send_text(self, chat_id: str, text: str, reply_to: Optional[str] = None) -> SendResult:
        """Convenience: send a text message."""
        return await self.send(OutboundMessage(
            text=text,
            chat=ChatContext(chat_id=chat_id),
            reply_to_id=reply_to,
        ))

    # -------------------------------------------------------------------------
    # Access Control
    # -------------------------------------------------------------------------

    def check_access(self, user_id: str, chat_id: str = "") -> AccessDecision:
        """
        Check if a user is allowed to interact via this channel.

        Args:
            user_id: Platform-specific user identifier
            chat_id: Platform-specific chat identifier

        Returns:
            AccessDecision with allowed flag and reason
        """
        if self.access_policy == AccessPolicy.OPEN:
            return AccessDecision(allowed=True, reason="open access")

        if self.access_policy == AccessPolicy.ALLOWLIST:
            if user_id in self.allowlist:
                return AccessDecision(allowed=True, reason="allowlisted", user_id=user_id)
            return AccessDecision(allowed=False, reason=f"user {user_id} not in allowlist")

        if self.access_policy == AccessPolicy.PAIRING:
            # Pairing is handled by subclass-specific logic
            if user_id in self.allowlist:
                return AccessDecision(allowed=True, reason="paired", user_id=user_id)
            return AccessDecision(allowed=False, reason="pairing required")

        return AccessDecision(allowed=False, reason="unknown policy")

    def add_to_allowlist(self, user_id: str) -> None:
        """Add a user to the allowlist (e.g., after pairing)."""
        if user_id not in self.allowlist:
            self.allowlist.append(user_id)
            self._logger.info(f"Added {user_id} to {self.name} allowlist")

    def remove_from_allowlist(self, user_id: str) -> None:
        """Remove a user from the allowlist."""
        if user_id in self.allowlist:
            self.allowlist.remove(user_id)
            self._logger.info(f"Removed {user_id} from {self.name} allowlist")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    async def _dispatch_message(self, message: InboundMessage) -> None:
        """Dispatch an inbound message to all registered handlers."""
        # Access check
        access = self.check_access(message.user.channel_user_id, message.chat.chat_id)
        if not access.allowed:
            self._logger.warning(
                f"Access denied for {message.user.channel_user_id} on {self.name}: {access.reason}"
            )
            return

        # Map to A2I2 user if resolved
        if access.user_id:
            message.user.arcus_user_id = access.user_id

        for handler in self._message_handlers:
            try:
                await handler(message)
            except Exception as e:
                self._logger.error(f"Handler error on {self.name}: {e}", exc_info=True)

    async def _dispatch_reaction(self, message_id: str, emoji: str, user: UserIdentity) -> None:
        """Dispatch a reaction event to all registered handlers."""
        for handler in self._reaction_handlers:
            try:
                await handler(message_id, emoji, user, self.channel_type)
            except Exception as e:
                self._logger.error(f"Reaction handler error on {self.name}: {e}", exc_info=True)
