"""
Arcus Discord Channel Adapter

Connects A2I2 to Discord using discord.py. Supports text messages,
slash commands, reaction-based feedback, threads, and rich embeds.

Usage:
    from adapter_discord import DiscordAdapter

    adapter = DiscordAdapter(
        bot_token="your-discord-bot-token",
        allowlist_guild_ids=["123456789"],
    )
    adapter.on_message(my_handler)
    await adapter.connect()

Requirements:
    - pip install discord.py
    - Discord bot token from https://discord.com/developers/applications
    - Bot invited to server with MESSAGE_CONTENT intent
"""

import asyncio
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

logger = logging.getLogger("arcus.channel.discord")


class DiscordAdapter(ChannelAdapter):
    """
    Discord channel adapter using discord.py.

    Features:
    - Text messages in channels and DMs
    - Slash commands for memory operations (/recall, /learn, /status)
    - Reaction-based feedback capture (thumbs up/down → reward signals)
    - Rich embed responses for formatted output
    - Thread support for context continuity
    - Guild-based access control
    - Mention-triggered responses (optional)

    Access control modes:
    - ALLOWLIST: Only whitelisted guild IDs
    - OPEN: Respond in any guild the bot is in
    """

    def __init__(
        self,
        bot_token: str,
        access_policy: AccessPolicy = AccessPolicy.ALLOWLIST,
        allowlist_guild_ids: Optional[List[str]] = None,
        require_mention: bool = False,
        respond_to_dms: bool = True,
    ):
        super().__init__(
            name="discord",
            channel_type=ChannelType.DISCORD,
            adapter_type=AdapterType.MESSAGING,
            access_policy=access_policy,
            allowlist=allowlist_guild_ids,
        )
        self.bot_token = bot_token
        self.require_mention = require_mention
        self.respond_to_dms = respond_to_dms
        self._client = None
        self._bot_user_id: Optional[int] = None
        self._run_task: Optional[asyncio.Task] = None
        self._ready_event: asyncio.Event = asyncio.Event()

    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------

    async def connect(self) -> None:
        """Start the Discord bot client."""
        try:
            import discord
        except ImportError:
            raise ImportError(
                "discord.py package required: pip install discord.py"
            )

        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True

        self._client = discord.Client(intents=intents)
        self._setup_event_handlers()

        # Run client in background
        self._ready_event.clear()
        self._run_task = asyncio.create_task(self._start_client())
        # Wait for on_ready with timeout instead of fixed sleep
        try:
            await asyncio.wait_for(self._ready_event.wait(), timeout=15.0)
        except asyncio.TimeoutError:
            logger.warning("Discord client did not become ready within 15s — continuing anyway")
        logger.info("Discord adapter started")

    async def _start_client(self) -> None:
        """Run the Discord client (blocks until disconnected)."""
        try:
            await self._client.start(self.bot_token)
        except Exception as e:
            logger.error(f"Discord client error: {e}", exc_info=True)
            self._connected = False

    async def disconnect(self) -> None:
        """Stop the Discord bot."""
        self._connected = False
        if self._client:
            await self._client.close()
        if self._run_task:
            self._run_task.cancel()
            self._run_task = None
        logger.info("Discord adapter disconnected")

    # -------------------------------------------------------------------------
    # Event handlers
    # -------------------------------------------------------------------------

    def _setup_event_handlers(self) -> None:
        """Wire up discord.py event handlers."""
        import discord

        @self._client.event
        async def on_ready():
            self._connected = True
            self._bot_user_id = self._client.user.id
            self._ready_event.set()
            logger.info(f"Discord bot ready as {self._client.user.name} ({self._bot_user_id})")

        @self._client.event
        async def on_message(msg: discord.Message):
            # Ignore own messages
            if msg.author.id == self._bot_user_id:
                return

            # DM handling
            is_dm = isinstance(msg.channel, discord.DMChannel)
            if is_dm and not self.respond_to_dms:
                return

            # Guild access check (for non-DM)
            if not is_dm:
                guild_id = str(msg.guild.id)
                access = self.check_access(guild_id)
                if not access.allowed:
                    return

                # Mention requirement
                if self.require_mention and self._client.user not in msg.mentions:
                    return

            # Build inbound message
            inbound = self._parse_discord_message(msg, is_dm)
            await self._dispatch_message(inbound)

        @self._client.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
            if user.id == self._bot_user_id:
                return
            await self._dispatch_reaction(
                str(reaction.message.id),
                str(reaction.emoji),
                UserIdentity(
                    channel_user_id=str(user.id),
                    display_name=user.display_name,
                ),
            )

    def _parse_discord_message(self, msg: Any, is_dm: bool) -> InboundMessage:
        """Convert a discord.py Message into an InboundMessage."""
        import discord

        # Parse attachments
        attachments = []
        content_type = MessageContentType.TEXT
        for att in msg.attachments:
            ct = att.content_type or "application/octet-stream"
            attachments.append(Attachment(
                content_type=ct,
                url=att.url,
                filename=att.filename,
                size_bytes=att.size,
            ))
            if ct.startswith("image/"):
                content_type = MessageContentType.IMAGE
            elif ct.startswith("audio/"):
                content_type = MessageContentType.AUDIO

        # Strip bot mention from text
        text = msg.content
        if self._client and self._client.user:
            text = text.replace(f"<@{self._bot_user_id}>", "").replace(
                f"<@!{self._bot_user_id}>", ""
            ).strip()

        # Check for slash command
        if text.startswith("/"):
            content_type = MessageContentType.COMMAND

        # Detect if message is in a thread
        is_thread = isinstance(msg.channel, discord.Thread)
        thread_name = msg.channel.name if is_thread else None
        parent_channel_id = str(msg.channel.parent_id) if is_thread and hasattr(msg.channel, 'parent_id') else None

        # Use thread ID as chat_id to maintain separate conversation state per thread
        chat_id = str(msg.channel.id)

        return InboundMessage(
            id=str(msg.id),
            channel=ChannelType.DISCORD,
            content_type=content_type,
            text=text,
            user=UserIdentity(
                channel_user_id=str(msg.author.id),
                display_name=msg.author.display_name,
            ),
            chat=ChatContext(
                chat_id=chat_id,
                is_group=not is_dm,
                group_name=thread_name if is_thread else (msg.guild.name if msg.guild else None),
                metadata={
                    "is_thread": is_thread,
                    "thread_name": thread_name,
                    "parent_channel_id": parent_channel_id,
                    "guild_id": str(msg.guild.id) if msg.guild else None,
                },
            ),
            attachments=attachments,
            reply_to_id=str(msg.reference.message_id) if msg.reference else None,
            raw_event=msg,
        )

    # -------------------------------------------------------------------------
    # Messaging
    # -------------------------------------------------------------------------

    async def send(self, message: OutboundMessage) -> SendResult:
        """Send a message to a Discord channel or thread."""
        if not self._client or not self._connected:
            return SendResult(success=False, error="Discord client not connected")

        try:
            import discord

            channel = self._client.get_channel(int(message.chat.chat_id))
            if not channel:
                channel = await self._client.fetch_channel(int(message.chat.chat_id))

            # Handle archived threads - unarchive before sending
            if isinstance(channel, discord.Thread) and channel.archived:
                try:
                    await channel.edit(archived=False)
                    logger.info(f"Unarchived thread {channel.id} to send message")
                except discord.Forbidden:
                    return SendResult(
                        success=False,
                        error="Cannot send to archived thread (insufficient permissions)"
                    )
                except Exception as e:
                    logger.warning(f"Failed to unarchive thread: {e}")

            # Check if response should be an embed
            if message.metadata.get("embed"):
                embed_data = message.metadata["embed"]
                embed = discord.Embed(
                    title=embed_data.get("title", ""),
                    description=embed_data.get("description", message.text),
                    color=embed_data.get("color", 0x7C3AED),  # Arcus purple
                )
                for field in embed_data.get("fields", []):
                    embed.add_field(
                        name=field["name"],
                        value=field["value"],
                        inline=field.get("inline", False),
                    )
                sent = await channel.send(embed=embed)
            else:
                # Split long messages (Discord 2000 char limit)
                text = message.text
                if len(text) > 2000:
                    chunks = [text[i:i + 1990] for i in range(0, len(text), 1990)]
                    sent = None
                    for chunk in chunks:
                        sent = await channel.send(chunk)
                else:
                    # Reply to original if available
                    reference = None
                    if message.reply_to_id:
                        try:
                            reference = discord.MessageReference(
                                message_id=int(message.reply_to_id),
                                channel_id=int(message.chat.chat_id),
                            )
                        except (ValueError, TypeError):
                            pass
                    sent = await channel.send(text, reference=reference)

            return SendResult(
                success=True,
                message_id=str(sent.id) if sent else None,
            )

        except Exception as e:
            logger.error(f"Discord send error: {e}", exc_info=True)
            return SendResult(success=False, error=str(e))

    async def send_embed(
        self,
        channel_id: str,
        title: str,
        description: str,
        fields: Optional[List[Dict[str, Any]]] = None,
        color: int = 0x7C3AED,
    ) -> SendResult:
        """Convenience: send a rich embed message."""
        return await self.send(OutboundMessage(
            text=description,
            chat=ChatContext(chat_id=channel_id),
            metadata={
                "embed": {
                    "title": title,
                    "description": description,
                    "fields": fields or [],
                    "color": color,
                }
            },
        ))
