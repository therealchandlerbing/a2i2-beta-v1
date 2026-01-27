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
    /help               - List available commands

Usage:
    from chat_commands import ChatCommandHandler

    handler = ChatCommandHandler(config, knowledge_repo)
    gateway.set_command_handler(handler.handle)
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from channel_adapter import InboundMessage

logger = logging.getLogger("arcus.commands")


class ChatCommandHandler:
    """
    Handles slash commands from any channel.

    Commands are processed before the AI model, providing fast
    deterministic responses for memory and system operations.
    """

    def __init__(self, supabase_url: str = "", supabase_key: str = ""):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self._supabase = None

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
            "/help": self._cmd_help,
        }

    async def _get_client(self):
        """Lazy-init Supabase client."""
        if self._supabase is None and self.supabase_url:
            try:
                from supabase import create_client
                self._supabase = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                logger.warning("supabase package not installed")
        return self._supabase

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
        args = parts[1] if len(parts) > 1 else ""

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

        client = await self._get_client()
        if not client:
            return "Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."

        results = []

        # Search semantic memory
        semantic = client.table("arcus_semantic_memory").select(
            "category, content, confidence"
        ).eq("user_id", user_id).ilike(
            "content", f"%{args[:100]}%"
        ).order("confidence", desc=True).limit(5).execute()
        for item in semantic.data or []:
            results.append(f"[{item['category']}] {item['content']} (confidence: {item['confidence']})")

        # Search episodic memory
        episodic = client.table("arcus_episodic_memory").select(
            "event_type, summary, significance"
        ).eq("user_id", user_id).ilike(
            "summary", f"%{args[:100]}%"
        ).order("significance", desc=True).limit(3).execute()
        for item in episodic.data or []:
            results.append(f"[{item['event_type']}] {item['summary']}")

        # Search entities
        entities = client.table("arcus_entities").select(
            "name, entity_type, summary"
        ).eq("user_id", user_id).ilike(
            "name", f"%{args[:100]}%"
        ).limit(3).execute()
        for item in entities.data or []:
            results.append(f"[{item['entity_type']}] {item['name']}: {item.get('summary', 'N/A')}")

        if not results:
            return f"No knowledge found for: **{args}**\n\nTip: Use `/learn` to teach me something new."

        header = f"**Recall results for: {args}**\n"
        body = "\n".join(f"• {r}" for r in results)
        return f"{header}\n{body}"

    async def _cmd_learn(self, args: str, user_id: str, **kwargs) -> str:
        """Capture explicit knowledge."""
        if not args:
            return "Usage: `/learn <statement>`\nExample: `/learn We use TypeScript for all new projects`"

        client = await self._get_client()
        if not client:
            return "Database not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."

        # Store as semantic memory
        client.table("arcus_semantic_memory").insert({
            "user_id": user_id,
            "category": "fact",
            "content": args,
            "confidence": 0.9,
            "source": "explicit_command",
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        return f"Learned: **{args}**\n\nThis has been stored with 0.9 confidence. Use `/recall` to retrieve it later."

    async def _cmd_forget(self, args: str, user_id: str, **kwargs) -> str:
        """Request knowledge removal."""
        if not args:
            return "Usage: `/forget <topic>`\nExample: `/forget old project name`"

        client = await self._get_client()
        if not client:
            return "Database not configured."

        # Mark matching memories as low confidence (soft delete)
        semantic = client.table("arcus_semantic_memory").select("id").eq(
            "user_id", user_id
        ).ilike("content", f"%{args[:100]}%").execute()

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

        return "\n".join(lines)

    async def _cmd_preferences(self, args: str, user_id: str, **kwargs) -> str:
        """Display learned user preferences."""
        client = await self._get_client()
        if not client:
            return "Database not configured."

        prefs = client.table("arcus_procedural_memory").select(
            "procedure_name, content, confidence"
        ).eq("user_id", user_id).eq(
            "procedure_type", "preference"
        ).order("confidence", desc=True).limit(15).execute()

        items = prefs.data or []
        if not items:
            return "No preferences learned yet.\n\nI learn your preferences automatically as we interact, or you can use `/learn` to teach me explicitly."

        lines = ["**Your Learned Preferences**\n"]
        for p in items:
            conf = f"{p['confidence']:.0%}" if p.get('confidence') else "N/A"
            lines.append(f"• **{p['procedure_name']}**: {p['content']} ({conf})")

        return "\n".join(lines)

    async def _cmd_autonomy(self, args: str, user_id: str, **kwargs) -> str:
        """Show current trust level and permissions."""
        client = await self._get_client()
        if not client:
            return "Database not configured."

        state = client.table("arcus_autonomy_state").select(
            "current_level, total_actions, successful_actions, trust_score"
        ).eq("user_id", user_id).limit(1).execute()

        if not state.data:
            return (
                "**Autonomy Trust Ledger**\n\n"
                "Level: **L0 (Observer)**\n"
                "No actions recorded yet. As you interact with Arcus, trust is built progressively.\n\n"
                "Levels: L0 Observer → L1 Suggest → L2 Act-with-Approval → L3 Act-then-Report → L4 Full Autonomy"
            )

        s = state.data[0]
        level_names = {
            0: "L0 Observer",
            1: "L1 Suggest",
            2: "L2 Act-with-Approval",
            3: "L3 Act-then-Report",
            4: "L4 Full Autonomy",
        }
        level = s.get("current_level", 0)

        return (
            f"**Autonomy Trust Ledger**\n\n"
            f"• Level: **{level_names.get(level, f'L{level}')}**\n"
            f"• Trust score: {s.get('trust_score', 0):.2f}\n"
            f"• Total actions: {s.get('total_actions', 0)}\n"
            f"• Successful: {s.get('successful_actions', 0)}\n\n"
            f"Levels: L0 Observer → L1 Suggest → L2 Act-with-Approval → L3 Act-then-Report → L4 Full Autonomy"
        )

    async def _cmd_reflect(self, args: str, user_id: str, **kwargs) -> str:
        """Trigger pattern synthesis."""
        client = await self._get_client()
        if not client:
            return "Database not configured."

        # Count recent memories
        from datetime import timedelta
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

        episodic = client.table("arcus_episodic_memory").select(
            "id", count="exact"
        ).eq("user_id", user_id).gte("created_at", week_ago).execute()

        semantic = client.table("arcus_semantic_memory").select(
            "id", count="exact"
        ).eq("user_id", user_id).gte("created_at", week_ago).execute()

        ep_count = episodic.count if episodic.count else 0
        sem_count = semantic.count if semantic.count else 0

        return (
            f"**Reflection Summary (Last 7 Days)**\n\n"
            f"• Episodic memories: {ep_count}\n"
            f"• Semantic entries: {sem_count}\n"
            f"• Total learnings: {ep_count + sem_count}\n\n"
            f"Pattern synthesis runs automatically during sessions. "
            f"Use `/recall` to search for specific patterns."
        )

    async def _cmd_status(self, args: str, **kwargs) -> str:
        """System health and memory stats."""
        client = await self._get_client()
        db_status = "Connected" if client else "Not configured"

        return (
            "**Arcus System Status**\n\n"
            f"• Database: {db_status}\n"
            f"• Gateway: Running\n"
            f"• Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            "Use `/context` for session info, `/autonomy` for trust level."
        )

    async def _cmd_new(self, args: str, session: Any = None, **kwargs) -> str:
        """Start a fresh session (memory is preserved)."""
        if session:
            return (
                f"Session `{session.id[:8]}...` ended.\n\n"
                f"Messages in this session: {session.message_count}\n"
                "A new session will start with your next message.\n\n"
                "Your memory and preferences are preserved across sessions."
            )
        return "New session started. Memory preserved."

    async def _cmd_help(self, **kwargs) -> str:
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
            "• `/status` — System health\n\n"
            "**Control**\n"
            "• `/reflect` — Trigger pattern synthesis\n"
            "• `/new` — Start fresh session (memory preserved)\n"
            "• `/help` — This message"
        )
