"""
Arcus Chat Commands - Memory-Aware Slash Commands

Handles slash commands across all channels. Inspired by Clawdbot's
/status, /think, /new commands, extended with A2I2's memory operations.

Supported Commands:
    /recall <query>     - Search knowledge graph
    /learn <statement>  - Capture explicit knowledge
    /forget <topic>     - Request knowledge removal
    /context            - Show current session memory state
    /preferences        - Display learned preferences
    /autonomy           - Show trust level and permissions
    /reflect            - Trigger pattern synthesis
    /status             - System health and memory stats
    /new                - Start fresh session (preserve memory)
    /compact            - Compress conversation context
    /verbose [0-3]      - Set response detail level
    /pair [code]        - Device pairing with codes
    /help               - List available commands

Usage:
    from chat_commands import ChatCommandHandler

    handler = ChatCommandHandler(middleware=middleware)
    gateway.set_command_handler(handler.handle)
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from channel_adapter import InboundMessage
from pairing_manager import PairingManager

logger = logging.getLogger("arcus.commands")


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

# Max length for any command argument (prevents abuse / memory exhaustion)
_MAX_ARG_LENGTH = 1000

# Patterns that should never appear in command arguments passed to queries.
# Blocks SQL injection fragments, shell metacharacters, and prompt-injection
# wrapper tags that could confuse downstream models.
_DANGEROUS_PATTERNS = [
    re.compile(r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER|EXEC)\b", re.IGNORECASE),
    re.compile(r"--\s*$", re.MULTILINE),  # SQL comment terminator at end of line
    re.compile(r"[`$]"),                   # shell interpolation characters
    re.compile(r"<\s*/?\s*(system|instruction|prompt|untrusted)\b", re.IGNORECASE),
]


def sanitize_input(text: str) -> str:
    """
    Sanitize user input for slash command arguments.

    - Truncates to _MAX_ARG_LENGTH
    - Strips leading/trailing whitespace
    - Rejects dangerous patterns by replacing matches with empty string
    - Logs warnings when dangerous content is stripped
    """
    text = text.strip()
    if len(text) > _MAX_ARG_LENGTH:
        logger.warning(f"Command arg truncated from {len(text)} to {_MAX_ARG_LENGTH} chars")
        text = text[:_MAX_ARG_LENGTH]

    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Stripped dangerous pattern from command input: {pattern.pattern}")
            text = pattern.sub("", text)

    return text.strip()


class ChatCommandHandler:
    """
    Handles slash commands from any channel.

    Commands are processed before the AI model, providing fast
    deterministic responses for memory and system operations.

    Uses ArcusMiddleware and KnowledgeRepository instead of raw
    Supabase queries — ensuring consistency with the core A2I2 modules.
    """

    def __init__(self, middleware=None, supabase_url: str = "", supabase_key: str = "", pairing_manager: Optional[PairingManager] = None):
        """
        Args:
            middleware: ArcusMiddleware instance (preferred — connects all A2I2 modules)
            supabase_url: Fallback direct Supabase URL (if no middleware)
            supabase_key: Fallback direct Supabase key (if no middleware)
            pairing_manager: PairingManager instance (optional)
        """
        self.middleware = middleware
        self._knowledge_repo = None
        self._trust_engine = None
        self.pairing_manager = pairing_manager or PairingManager()

        # Initialize from middleware if available
        if middleware:
            self._knowledge_repo = middleware.knowledge
            self._trust_engine = middleware.trust_engine
        else:
            # Fallback: create standalone KnowledgeRepository
            if supabase_url:
                try:
                    from knowledge_operations import KnowledgeRepository
                    self._knowledge_repo = KnowledgeRepository(supabase_url, supabase_key)
                except ImportError:
                    logger.warning("knowledge_operations not available")

        # Session end callback (set by gateway)
        self._session_end_callback = None

        # Command registry
        self._commands: Dict[str, Any] = {
            "/recall": self._cmd_recall,
            "/learn": self._cmd_learn,
            "/forget": self._cmd_forget,
            "/context": self._cmd_context,
            "/preferences": self._cmd_preferences,
            "/autonomy": self._cmd_autonomy,
            "/reflect": self._cmd_reflect,
            "/status": self._cmd_status,
            "/new": self._cmd_new,
            "/compact": self._cmd_compact,
            "/verbose": self._cmd_verbose,
            "/pair": self._cmd_pair,
            "/help": self._cmd_help,
        }

    def set_session_end_callback(self, callback) -> None:
        """Set the callback to end a gateway session (called by /new)."""
        self._session_end_callback = callback

    # -------------------------------------------------------------------------
    # Main handler (registered with gateway)
    # -------------------------------------------------------------------------

    async def handle(self, message: InboundMessage, session: Any) -> Optional[str]:
        """
        Handle a slash command message.

        Args:
            message: The inbound message starting with /
            session: The current GatewaySession

        Returns:
            Response text, or None if not a recognized command
        """
        text = message.text.strip()
        if not text.startswith("/"):
            return None

        # Parse command and args
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        args = sanitize_input(parts[1]) if len(parts) > 1 else ""

        handler = self._commands.get(command)
        if not handler:
            return None  # Not a command, let AI handle it

        try:
            return await handler(
                args=args,
                user_id=message.user.arcus_user_id or message.user.channel_user_id,
                session=session,
                message=message,
            )
        except Exception as e:
            logger.error(f"Command {command} error: {e}", exc_info=True)
            return f"Error executing {command}: {str(e)}"

    # -------------------------------------------------------------------------
    # Command implementations
    # -------------------------------------------------------------------------

    async def _cmd_recall(self, args: str, user_id: str, **kwargs) -> str:
        """Search knowledge graph for a topic."""
        if not args:
            return "Usage: `/recall <query>`\nExample: `/recall TypeScript preferences`"

        if not self._knowledge_repo:
            return "Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."

        # Use KnowledgeRepository.recall() instead of raw queries
        try:
            results = self._knowledge_repo.recall(
                args,
                memory_types=["semantic", "episodic", "graph"],
                limit=10,
            )
        except Exception as e:
            logger.error(f"Recall failed: {e}")
            results = []

        if not results:
            # Fallback: try direct Supabase query if recall returns empty
            if self._knowledge_repo and self._knowledge_repo.supabase:
                results = self._fallback_recall(args, user_id)

        if not results:
            return f"No knowledge found for: **{args}**\n\nTip: Use `/learn` to teach me something new."

        header = f"**Recall results for: {args}**\n"
        formatted = []
        for r in results[:10]:
            if isinstance(r, dict):
                mem_type = r.get("memory_type", r.get("category", r.get("event_type", "item")))
                content = r.get("content", r.get("summary", r.get("statement", r.get("name", str(r)))))
                conf = r.get("confidence", "")
                conf_str = f" ({conf:.0%})" if isinstance(conf, (int, float)) and conf else ""
                formatted.append(f"• [{mem_type}] {content}{conf_str}")
            else:
                formatted.append(f"• {r}")

        body = "\n".join(formatted)
        return f"{header}\n{body}"

    @staticmethod
    def _escape_like(value: str) -> str:
        """Escape LIKE/ILIKE wildcards (% and _) and backslash."""
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    def _fallback_recall(self, query: str, user_id: str) -> list:
        """Direct Supabase query fallback for recall."""
        results = []
        client = self._knowledge_repo.supabase
        escaped = self._escape_like(query[:100])

        try:
            semantic = client.table("arcus_semantic_memory").select(
                "category, content, confidence"
            ).ilike("content", f"%{escaped}%").order(
                "confidence", desc=True
            ).limit(5).execute()
            for item in semantic.data or []:
                item["memory_type"] = item.get("category", "semantic")
                results.append(item)
        except Exception as e:
            logger.debug(f"Fallback semantic recall failed: {e}")

        try:
            entities = client.table("arcus_entities").select(
                "name, entity_type, summary"
            ).ilike("name", f"%{escaped}%").limit(3).execute()
            for item in entities.data or []:
                item["memory_type"] = item.get("entity_type", "entity")
                item["content"] = f"{item['name']}: {item.get('summary', 'N/A')}"
                results.append(item)
        except Exception as e:
            logger.debug(f"Fallback entities recall failed: {e}")

        return results

    async def _cmd_learn(self, args: str, user_id: str, **kwargs) -> str:
        """Capture explicit knowledge."""
        if not args:
            return "Usage: `/learn <statement>`\nExample: `/learn We use TypeScript for all new projects`"

        if not self._knowledge_repo:
            return "Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."

        # Use KnowledgeRepository.learn_fact()
        try:
            self._knowledge_repo.learn_fact(
                statement=args,
                category="fact",
                confidence=0.9,
            )
        except Exception as e:
            logger.error(f"Learn failed: {e}")
            return f"Failed to learn: {str(e)}"

        return f"Learned: **{args}**\n\nThis has been stored with 0.9 confidence. Use `/recall` to retrieve it later."

    async def _cmd_forget(self, args: str, user_id: str, **kwargs) -> str:
        """Request knowledge removal."""
        if not args:
            return "Usage: `/forget <topic>`\nExample: `/forget old project name`"

        if not self._knowledge_repo or not self._knowledge_repo.supabase:
            return "Database not configured."

        client = self._knowledge_repo.supabase

        # Mark matching memories as low confidence (soft delete)
        escaped = self._escape_like(args[:100])
        semantic = client.table("arcus_semantic_memory").select("id").ilike(
            "content", f"%{escaped}%"
        ).execute()

        count = len(semantic.data or [])
        if count == 0:
            return f"No knowledge found matching: **{args}**"

        for item in semantic.data or []:
            client.table("arcus_semantic_memory").update(
                {"confidence": 0.0}
            ).eq("id", item["id"]).execute()

        return f"Marked {count} item(s) for removal matching: **{args}**\n\nThese will no longer appear in recall results."

    async def _cmd_context(self, args: str, session: Any = None, **kwargs) -> str:
        """Show current session memory state."""
        if not session:
            return "No active session."

        lines = [
            "**Current Session Context**",
            f"• Session ID: `{session.id[:8]}...`",
            f"• Channel: {session.channel.value}",
            f"• Messages: {session.message_count}",
            f"• Started: {session.created_at.strftime('%Y-%m-%d %H:%M UTC')}",
            f"• Last activity: {session.last_activity.strftime('%H:%M UTC')}",
        ]

        if session.context:
            lines.append(f"• Context keys: {', '.join(session.context.keys())}")

        # Show middleware session info if available
        if self.middleware:
            mw_status = self.middleware.status()
            lines.append(f"• Memory injection: {'enabled' if mw_status.get('memory_injection') else 'disabled'}")
            lines.append(f"• Auto-learn: {'enabled' if mw_status.get('auto_learn') else 'disabled'}")
            lines.append(f"• Verbosity: {mw_status.get('verbosity_level', 1)}")

        return "\n".join(lines)

    async def _cmd_preferences(self, args: str, user_id: str, **kwargs) -> str:
        """Display learned user preferences."""
        if not self._knowledge_repo:
            return "Database not configured."

        # Use KnowledgeRepository.recall_preferences()
        try:
            prefs = self._knowledge_repo.recall_preferences()
        except Exception:
            prefs = []

        if not prefs:
            return "No preferences learned yet.\n\nI learn your preferences automatically as we interact, or you can use `/learn` to teach me explicitly."

        lines = ["**Your Learned Preferences**\n"]
        for p in prefs[:15]:
            name = p.get("procedure_name", p.get("name", "Preference"))
            content = p.get("content", p.get("description", ""))
            conf = p.get("confidence")
            conf_str = f" ({conf:.0%})" if isinstance(conf, (int, float)) else ""
            lines.append(f"• **{name}**: {content}{conf_str}")

        return "\n".join(lines)

    async def _cmd_autonomy(self, args: str, user_id: str, **kwargs) -> str:
        """Show current trust level and permissions."""
        level_names = {
            0: "L0 Observer",
            1: "L1 Suggest",
            2: "L2 Act-with-Approval",
            3: "L3 Act-then-Report",
            4: "L4 Full Autonomy",
        }

        # Use TrustEngine if available
        if self._trust_engine:
            try:
                stats = self._trust_engine.get_trust_statistics()
                level = stats.get("current_level", 0)
                return (
                    f"**Autonomy Trust Ledger**\n\n"
                    f"• Level: **{level_names.get(level, f'L{level}')}**\n"
                    f"• Trust score: {stats.get('trust_score', 0):.2f}\n"
                    f"• Total actions: {stats.get('total_actions', 0)}\n"
                    f"• Successful: {stats.get('successful_actions', 0)}\n\n"
                    f"Levels: L0 Observer → L1 Suggest → L2 Act-with-Approval → L3 Act-then-Report → L4 Full Autonomy"
                )
            except Exception as e:
                logger.debug(f"TrustEngine query failed: {e}")

        # Fallback: direct Supabase query
        if self._knowledge_repo and self._knowledge_repo.supabase:
            try:
                state = self._knowledge_repo.supabase.table("arcus_autonomy_state").select(
                    "current_level, total_actions, successful_actions, trust_score"
                ).limit(1).execute()

                if state.data:
                    s = state.data[0]
                    level = s.get("current_level", 0)
                    return (
                        f"**Autonomy Trust Ledger**\n\n"
                        f"• Level: **{level_names.get(level, f'L{level}')}**\n"
                        f"• Trust score: {s.get('trust_score', 0):.2f}\n"
                        f"• Total actions: {s.get('total_actions', 0)}\n"
                        f"• Successful: {s.get('successful_actions', 0)}\n\n"
                        f"Levels: L0 Observer → L1 Suggest → L2 Act-with-Approval → L3 Act-then-Report → L4 Full Autonomy"
                    )
            except Exception:
                pass

        return (
            "**Autonomy Trust Ledger**\n\n"
            "Level: **L0 (Observer)**\n"
            "No actions recorded yet. As you interact with Arcus, trust is built progressively.\n\n"
            "Levels: L0 Observer → L1 Suggest → L2 Act-with-Approval → L3 Act-then-Report → L4 Full Autonomy"
        )

    async def _cmd_reflect(self, args: str, user_id: str, **kwargs) -> str:
        """Trigger pattern synthesis via KnowledgeRepository.reflect()."""
        if not self._knowledge_repo:
            return "Database not configured."

        # Use KnowledgeRepository.reflect()
        try:
            insights = self._knowledge_repo.reflect(days=7)
            if insights and isinstance(insights, list):
                lines = ["**Reflection Summary (Last 7 Days)**\n"]
                for insight in insights[:5]:
                    if isinstance(insight, dict):
                        lines.append(f"• {insight.get('summary', insight.get('pattern', str(insight)))}")
                    else:
                        lines.append(f"• {insight}")
                lines.append(f"\n{len(insights)} pattern(s) synthesized.")
                return "\n".join(lines)
            elif insights:
                return f"**Reflection Complete**\n\nSynthesis result: {insights}"
        except Exception as e:
            logger.debug(f"Reflect failed: {e}")

        # Fallback: count recent memories
        try:
            recent_events = self._knowledge_repo.recall_recent_events(days=7)
            ep_count = len(recent_events) if recent_events else 0
        except Exception:
            ep_count = 0

        return (
            f"**Reflection Summary (Last 7 Days)**\n\n"
            f"• Recent events: {ep_count}\n\n"
            f"Pattern synthesis runs automatically during sessions. "
            f"Use `/recall` to search for specific patterns."
        )

    async def _cmd_status(self, args: str, **kwargs) -> str:
        """System health and memory stats."""
        db_connected = bool(self._knowledge_repo and self._knowledge_repo.supabase)
        middleware_running = bool(self.middleware)

        lines = [
            "**Arcus System Status**\n",
            f"• Database: {'Connected' if db_connected else 'Not configured'}",
            f"• Middleware: {'Active' if middleware_running else 'Inactive'}",
            f"• Gateway: Running",
            f"• Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        ]

        if self.middleware:
            mw = self.middleware.status()
            lines.append(f"• Active sessions: {mw.get('active_sessions', 0)}")
            lines.append(f"• Memory injection: {'on' if mw.get('memory_injection') else 'off'}")
            lines.append(f"• Auto-learn: {'on' if mw.get('auto_learn') else 'off'}")
            lines.append(f"• Trust tracking: {'on' if mw.get('trust_tracking') else 'off'}")

        lines.append("\nUse `/context` for session info, `/autonomy` for trust level.")
        return "\n".join(lines)

    async def _cmd_new(self, args: str, session: Any = None, **kwargs) -> str:
        """Start a fresh session (memory is preserved)."""
        msg_count = 0
        session_id = ""

        if session:
            msg_count = session.message_count
            session_id = session.id[:8]

            # End both gateway and middleware sessions together
            try:
                if self._session_end_callback and hasattr(session, 'id'):
                    self._session_end_callback(session.id)
                if self.middleware and hasattr(session, 'user_id'):
                    self.middleware.end_session(
                        user_id=session.user_id,
                        channel=session.channel.value if hasattr(session.channel, 'value') else str(session.channel),
                        chat_id=session.chat_id if hasattr(session, 'chat_id') else "",
                    )
            except Exception as e:
                logger.error(f"Failed to end session cleanly: {e}", exc_info=True)

        return (
            f"Session `{session_id}...` ended.\n\n"
            f"Messages in this session: {msg_count}\n"
            "A new session will start with your next message.\n\n"
            "Your memory and preferences are preserved across sessions."
        )

    async def _cmd_compact(self, args: str, session: Any = None, **kwargs) -> str:
        """Compress conversation context."""
        if not self.middleware:
            return "Middleware not available. Context compression requires the memory middleware."

        if not session:
            return "No active session to compact."

        user_id = session.user_id if hasattr(session, 'user_id') else ""
        channel = session.channel.value if hasattr(session.channel, 'value') else str(session.channel)
        chat_id = session.chat_id if hasattr(session, 'chat_id') else ""

        mw_session = self.middleware.get_or_create_session(user_id, channel, chat_id)
        history_len = len(mw_session.history)

        if history_len <= 4:
            return f"Context is already compact ({history_len // 2} turns). Nothing to compress."

        # Keep only the last 2 turns (4 messages) + flush pending learnings
        mw_session.history = mw_session.history[-4:]
        self.middleware._flush_session(mw_session)

        removed = (history_len - 4) // 2
        return (
            f"**Context Compacted**\n\n"
            f"• Removed: {removed} older conversation turns\n"
            f"• Kept: 2 most recent turns\n"
            f"• Pending learnings flushed to persistent memory\n\n"
            "Your knowledge graph and preferences are unaffected."
        )

    async def _cmd_verbose(self, args: str, session: Any = None, **kwargs) -> str:
        """Set response detail level."""
        level_descriptions = {
            0: "Concise — short, direct answers",
            1: "Normal — balanced detail (default)",
            2: "Detailed — thorough explanations",
            3: "Verbose — maximum detail and context",
        }

        if not args.strip():
            # Show current level
            current = 1
            if self.middleware:
                current = self.middleware.config.verbosity_level
            return (
                "**Verbosity Levels**\n\n"
                + "\n".join(f"• `{k}` — {v}" for k, v in level_descriptions.items())
                + f"\n\nCurrent level: **{current}** ({level_descriptions.get(current, 'unknown')})\n"
                + "Usage: `/verbose 0` through `/verbose 3`"
            )

        try:
            level = int(args.strip())
            if level < 0 or level > 3:
                raise ValueError()
        except ValueError:
            return "Invalid level. Use `/verbose 0` through `/verbose 3`."

        if self.middleware:
            # Store per-session, not globally
            session = kwargs.get("session")
            user_id = kwargs.get("user_id", "")
            channel_val = ""
            chat_id_val = ""
            if session:
                user_id = getattr(session, "user_id", user_id)
                channel_val = session.channel.value if hasattr(session.channel, "value") else str(getattr(session, "channel", ""))
                chat_id_val = getattr(session, "chat_id", "")
            mw_session = self.middleware.get_or_create_session(user_id, channel_val, chat_id_val) if user_id else None
            if mw_session:
                mw_session.verbosity_level = level
            else:
                self.middleware.config.verbosity_level = level

        return f"Verbosity set to **{level}** — {level_descriptions[level]}"

    async def _cmd_pair(self, args: str, message: InboundMessage = None, **kwargs) -> str:
        """Handle device pairing with codes."""
        if not message:
            return "Pairing command requires message context."

        user_id = message.user.arcus_user_id or message.user.channel_user_id
        device_id = message.user.channel_user_id
        channel = message.channel.value

        # No args: check pairing status
        if not args:
            if self.pairing_manager.is_paired(device_id, channel):
                device = self.pairing_manager.get_paired_device(device_id)
                paired_since = device.paired_at.strftime("%Y-%m-%d %H:%M UTC") if device else "unknown"
                return (
                    f"**Device Paired** ✓\n\n"
                    f"• Device: `{device_id}`\n"
                    f"• User: `{user_id}`\n"
                    f"• Channel: {channel}\n"
                    f"• Since: {paired_since}\n\n"
                    "Use `/pair unpair` to unpair this device."
                )
            else:
                return (
                    "**Device Not Paired**\n\n"
                    "To pair this device:\n"
                    "1. Generate a code: `/pair generate`\n"
                    "2. Enter the code: `/pair <code>`\n\n"
                    "Pairing codes expire after 15 minutes."
                )

        # Parse subcommand
        parts = args.strip().split(maxsplit=1)
        subcommand = parts[0].lower()

        # Generate a new pairing code
        if subcommand == "generate":
            code = self.pairing_manager.generate_code(user_id=user_id, channel=channel)
            stats = self.pairing_manager.get_stats()
            return (
                f"**Pairing Code Generated** 🔑\n\n"
                f"Code: `{code}`\n"
                f"Valid for: 15 minutes\n"
                f"Channel: {channel}\n\n"
                f"To pair, enter: `/pair {code}`\n\n"
                f"_Active codes: {stats['active_codes']} | Paired devices: {stats['paired_devices']}_"
            )

        # Unpair current device
        elif subcommand == "unpair":
            if self.pairing_manager.unpair_device(device_id):
                return (
                    f"**Device Unpaired**\n\n"
                    f"Device `{device_id}` has been unpaired from user `{user_id}`.\n"
                    "Use `/pair generate` to create a new pairing code."
                )
            else:
                return "Device was not paired."

        # List all paired devices for this user
        elif subcommand == "list":
            devices = self.pairing_manager.get_user_devices(user_id)
            if not devices:
                return f"No devices paired to user `{user_id}`."

            lines = [f"**Paired Devices for {user_id}**\n"]
            for dev in devices:
                lines.append(
                    f"• `{dev.device_id}` on {dev.channel} — paired {dev.paired_at.strftime('%Y-%m-%d')}"
                )
            return "\n".join(lines)

        # Treat args as pairing code
        else:
            code = args.strip()
            result = self.pairing_manager.pair_device(
                code=code,
                device_id=device_id,
                channel=channel,
                nickname=message.user.display_name
            )

            if result.success:
                return (
                    f"**Device Paired Successfully** ✓\n\n"
                    f"• Device: `{result.device_id}`\n"
                    f"• User: `{result.user_id}`\n"
                    f"• Channel: {channel}\n\n"
                    "You now have full access to Arcus Intelligence."
                )
            else:
                return f"**Pairing Failed**\n\n{result.error}"

    async def _cmd_help(self, args: str = "", **kwargs) -> str:
        """List available commands."""
        return (
            "**Arcus Commands**\n\n"
            "**Memory**\n"
            "• `/recall <query>` — Search knowledge graph\n"
            "• `/learn <statement>` — Capture explicit knowledge\n"
            "• `/forget <topic>` — Request knowledge removal\n\n"
            "**Status**\n"
            "• `/context` — Show current session state\n"
            "• `/preferences` — Display learned preferences\n"
            "• `/autonomy` — Show trust level\n"
            "• `/status` — System health\n"
            "• `/pair [code]` — Pair device with code\n\n"
            "**Control**\n"
            "• `/reflect` — Trigger pattern synthesis\n"
            "• `/new` — Start fresh session (memory preserved)\n"
            "• `/compact` — Compress conversation context\n"
            "• `/verbose [0-3]` — Set response detail level\n"
            "• `/help` — This message"
        )
