"""
Arcus Memory Middleware — A2I2 Intelligence Layer for ClawdBot

The central integration point between ClawdBot's multi-channel runtime
and A2I2's memory/intelligence systems. Provides pre-message and
post-message hooks that inject memory context and extract learnings.

This module wires together ALL existing A2I2 modules:
  - knowledge_operations.py → LEARN, RECALL, RELATE, REFLECT
  - model_router.py         → Task-based model selection
  - trust_engine.py         → Autonomy Trust Ledger (ATL)
  - context_budget.py       → Context window management
  - digital_twin.py         → Cognitive pattern modeling

Usage (ClawdBot skill mode):
    from memory_middleware import ArcusMiddleware

    middleware = ArcusMiddleware.from_env()

    # Hook into ClawdBot's message pipeline
    @clawdbot.pre_message
    async def inject_context(message, session):
        return await middleware.pre_message(message.text, session.user_id, session.channel)

    @clawdbot.post_message
    async def extract_learnings(message, response, session):
        await middleware.post_message(message.text, response, session.user_id, session.channel)

Usage (standalone gateway mode):
    # See gateway.py — ArcusGateway uses this middleware internally
"""

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from knowledge_operations import (
    KnowledgeRepository,
    SemanticCategory,
    SemanticEntry,
    EpisodicEntry,
    EventType,
    KnowledgeSource,
    SourceType,
    ProcedureType,
    ProceduralEntry,
)
from context_budget import ContextBudgetManager
from trust_engine import TrustEngine, ActionCategory
from model_router import ModelRouter

logger = logging.getLogger("arcus.middleware")


# =============================================================================
# AUDIT LOGGER
# =============================================================================

class AuditLogger:
    """
    Structured audit logger for gateway events.

    Writes JSON-lines to a dedicated audit log file. Each entry includes
    timestamp, event type, user, channel, and event-specific data.

    The audit log captures:
    - Session start/end
    - Messages processed (text length only — NOT content, for privacy)
    - Commands executed
    - Learnings captured
    - Auth failures
    - Trust level changes
    """

    def __init__(self, log_dir: str = "", enabled: bool = True):
        self.enabled = enabled
        if not log_dir:
            log_dir = os.getenv("ARCUS_AUDIT_LOG_DIR", "logs")
        self._log_dir = Path(log_dir)
        self._log_file: Optional[Path] = None

        if self.enabled:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            self._log_file = self._log_dir / "audit.jsonl"

    def log(
        self,
        event_type: str,
        user_id: str = "",
        channel: str = "",
        **data: Any,
    ) -> None:
        """Write an audit entry."""
        if not self.enabled or not self._log_file:
            return

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "user": user_id,
            "channel": channel,
            **data,
        }

        try:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            logger.debug(f"Audit log write failed: {e}")

    def log_message(self, user_id: str, channel: str, text_length: int, response_length: int) -> None:
        """Log a message exchange (lengths only, not content)."""
        self.log("message", user_id=user_id, channel=channel,
                 text_len=text_length, response_len=response_length)

    def log_command(self, user_id: str, channel: str, command: str) -> None:
        """Log a slash command execution."""
        self.log("command", user_id=user_id, channel=channel, command=command)

    def log_learning(self, user_id: str, channel: str, learning_type: str, source: str) -> None:
        """Log a captured learning."""
        self.log("learning", user_id=user_id, channel=channel,
                 learning_type=learning_type, source=source)

    def log_session(self, event: str, user_id: str, channel: str, message_count: int = 0) -> None:
        """Log session start/end."""
        self.log(f"session.{event}", user_id=user_id, channel=channel,
                 message_count=message_count)

    def log_auth_failure(self, user_id: str, channel: str, reason: str = "") -> None:
        """Log an authentication failure."""
        self.log("auth_failure", user_id=user_id, channel=channel, reason=reason)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MiddlewareConfig:
    """Configuration for the memory middleware."""
    # Database
    supabase_url: str = ""
    supabase_key: str = ""

    # Memory injection
    memory_injection_enabled: bool = True
    max_context_tokens: int = 8000

    # Auto-learning
    auto_learn_enabled: bool = True
    correction_detection_enabled: bool = True

    # Trust
    trust_tracking_enabled: bool = True

    # Heartbeat (periodic REFLECT)
    heartbeat_interval_messages: int = 50

    # Conversation history
    max_history_turns: int = 10

    # Verbosity (0=concise, 1=normal, 2=detailed, 3=verbose)
    verbosity_level: int = 1

    # Audit logging
    audit_enabled: bool = True
    audit_log_dir: str = ""

    @classmethod
    def from_env(cls) -> "MiddlewareConfig":
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
            memory_injection_enabled=os.getenv("ARCUS_MEMORY_INJECTION", "true").lower() == "true",
            max_context_tokens=int(os.getenv("ARCUS_MAX_CONTEXT_TOKENS", "8000")),
            auto_learn_enabled=os.getenv("ARCUS_AUTO_LEARN", "true").lower() == "true",
            trust_tracking_enabled=os.getenv("ARCUS_TRUST_TRACKING", "true").lower() == "true",
            heartbeat_interval_messages=int(os.getenv("ARCUS_HEARTBEAT_INTERVAL", "50")),
            max_history_turns=int(os.getenv("ARCUS_MAX_HISTORY_TURNS", "10")),
            verbosity_level=int(os.getenv("ARCUS_VERBOSITY", "1")),
            audit_enabled=os.getenv("ARCUS_AUDIT_LOG", "true").lower() == "true",
            audit_log_dir=os.getenv("ARCUS_AUDIT_LOG_DIR", "logs"),
        )


# =============================================================================
# SESSION WITH CONVERSATION HISTORY
# =============================================================================

@dataclass
class MiddlewareSession:
    """Extended session with conversation history and middleware state."""
    user_id: str = ""
    channel: str = ""
    chat_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    history: List[Dict[str, str]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    verbosity_level: int = 1
    memory_injected_at: Optional[datetime] = None
    pending_learnings: List[Dict[str, Any]] = field(default_factory=list)

    def add_turn(self, user_message: str, assistant_response: str, max_turns: int = 10) -> None:
        """Add a conversation turn, maintaining max history size."""
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": assistant_response})
        # Trim to max turns (each turn = 2 messages)
        if len(self.history) > max_turns * 2:
            self.history = self.history[-(max_turns * 2):]

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)
        self.message_count += 1


# =============================================================================
# CORRECTION DETECTOR
# =============================================================================

# Patterns that indicate user is correcting the AI
_CORRECTION_PATTERNS = [
    re.compile(r"^(actually|no,?\s)", re.IGNORECASE),
    re.compile(r"^(that'?s\s+(not|wrong|incorrect))", re.IGNORECASE),
    re.compile(r"^(i\s+(prefer|want|need|use|like)\s)", re.IGNORECASE),
    re.compile(r"(don'?t\s+(do|use|say|add)\s)", re.IGNORECASE),
    re.compile(r"(always|never)\s+(use|do|include|add)", re.IGNORECASE),
    re.compile(r"(from now on|going forward|in the future)", re.IGNORECASE),
    re.compile(r"^(please\s+)?(remember|note)\s+that", re.IGNORECASE),
]

# Patterns that indicate a decision was made
_DECISION_PATTERNS = [
    re.compile(r"(let'?s\s+(go with|use|pick|choose))", re.IGNORECASE),
    re.compile(r"(we'?ll\s+(use|go with|adopt))", re.IGNORECASE),
    re.compile(r"(decided?\s+to\s)", re.IGNORECASE),
    re.compile(r"(approved?|confirmed?|agreed?)\b", re.IGNORECASE),
]


def detect_correction(text: str) -> bool:
    """Detect if a message contains a user correction."""
    return any(p.search(text) for p in _CORRECTION_PATTERNS)


def detect_decision(text: str) -> bool:
    """Detect if a message contains a decision."""
    return any(p.search(text) for p in _DECISION_PATTERNS)


# =============================================================================
# ARCUS MIDDLEWARE — MAIN CLASS
# =============================================================================

class ArcusMiddleware:
    """
    The core intelligence middleware that bridges ClawdBot and A2I2.

    Provides:
    - pre_message():  Inject memory context before AI processing
    - post_message(): Extract learnings after AI responds
    - on_session_start(): Load user state
    - on_session_end(): Flush pending learnings
    - on_reaction(): Capture feedback signals
    - on_heartbeat(): Periodic REFLECT

    Wires together:
    - KnowledgeRepository  (memory operations)
    - ContextBudgetManager (context window management)
    - TrustEngine          (autonomy trust ledger)
    - ModelRouter          (task-based model selection)
    """

    def __init__(self, config: Optional[MiddlewareConfig] = None):
        self.config = config or MiddlewareConfig.from_env()

        # Core A2I2 modules
        self.knowledge = KnowledgeRepository(
            supabase_url=self.config.supabase_url,
            supabase_key=self.config.supabase_key,
        )
        self.budget_manager = ContextBudgetManager(
            max_context=self.config.max_context_tokens,
        )
        self.trust_engine = TrustEngine(
            supabase_url=self.config.supabase_url,
            supabase_key=self.config.supabase_key,
        )
        self.model_router = ModelRouter()

        # Audit logger
        self.audit = AuditLogger(
            log_dir=self.config.audit_log_dir,
            enabled=self.config.audit_enabled,
        )

        # Session store
        self._sessions: Dict[str, MiddlewareSession] = {}

    @classmethod
    def from_env(cls) -> "ArcusMiddleware":
        """Create middleware from environment variables."""
        return cls(MiddlewareConfig.from_env())

    # -------------------------------------------------------------------------
    # Session management
    # -------------------------------------------------------------------------

    def _session_key(self, user_id: str, channel: str, chat_id: str = "") -> str:
        return f"{channel}:{user_id}:{chat_id}"

    def get_or_create_session(
        self, user_id: str, channel: str, chat_id: str = ""
    ) -> MiddlewareSession:
        """Get existing session or create a new one."""
        key = self._session_key(user_id, channel, chat_id)
        session = self._sessions.get(key)

        if session:
            timeout = timedelta(minutes=30)
            if (datetime.now(timezone.utc) - session.last_activity) > timeout:
                # Session expired — flush and create new
                self._flush_session(session)
                del self._sessions[key]
                session = None

        if not session:
            session = MiddlewareSession(
                user_id=user_id,
                channel=channel,
                chat_id=chat_id,
                verbosity_level=self.config.verbosity_level,
            )
            self._sessions[key] = session
            logger.info(f"New middleware session for {key}")
            self.audit.log_session("start", user_id=user_id, channel=channel)

        return session

    def end_session(self, user_id: str, channel: str, chat_id: str = "") -> Optional[MiddlewareSession]:
        """End a session, flush learnings, return the session."""
        key = self._session_key(user_id, channel, chat_id)
        session = self._sessions.pop(key, None)
        if session:
            self._flush_session(session)
            logger.info(f"Ended session for {key} ({session.message_count} messages)")
            self.audit.log_session("end", user_id=user_id, channel=channel,
                                   message_count=session.message_count)
        return session

    def _flush_session(self, session: MiddlewareSession) -> None:
        """Flush pending learnings from a session. Failed learnings are retained."""
        if not session.pending_learnings:
            return

        failed: List[Dict[str, Any]] = []
        flushed = 0

        for learning in session.pending_learnings:
            try:
                learning_type = learning.get("type", "fact")
                if learning_type == "preference":
                    self.knowledge.learn_preference(
                        learning["content"],
                        confidence=learning.get("confidence", 0.8),
                    )
                elif learning_type == "fact":
                    self.knowledge.learn_fact(
                        learning["content"],
                        category=learning.get("category", "fact"),
                        confidence=learning.get("confidence", 0.8),
                    )
                elif learning_type == "event":
                    self.knowledge.learn_event(
                        event_type=learning.get("event_type", "conversation"),
                        summary=learning["content"],
                        participants=learning.get("participants", [session.user_id]),
                    )
                flushed += 1
            except Exception as e:
                logger.error(f"Failed to flush learning: {e}")
                failed.append(learning)

        session.pending_learnings = failed
        if failed:
            logger.warning(f"Flushed {flushed} learnings for {session.user_id}, {len(failed)} failed and retained")
        else:
            logger.info(f"Flushed {flushed} learnings for {session.user_id}")

    # -------------------------------------------------------------------------
    # PRE-MESSAGE HOOK
    # -------------------------------------------------------------------------

    async def pre_message(
        self,
        text: str,
        user_id: str,
        channel: str,
        chat_id: str = "",
    ) -> Dict[str, Any]:
        """
        Pre-message hook: called before the AI model sees the message.

        Returns a dict with:
          - system_context: str to inject into system prompt
          - history: list of prior conversation turns
          - model_recommendation: suggested model for this task
          - trust_level: current autonomy level
          - session: the MiddlewareSession object
        """
        session = self.get_or_create_session(user_id, channel, chat_id)
        session.touch()

        result: Dict[str, Any] = {
            "system_context": "",
            "history": session.history,
            "model_recommendation": None,
            "trust_level": 0,
            "session": session,
        }

        # Memory context injection
        if self.config.memory_injection_enabled:
            try:
                context_block = await self._build_memory_context(user_id, text, session)
                result["system_context"] = context_block
            except Exception as e:
                logger.error(f"Memory injection failed: {e}", exc_info=True)

        # Model routing recommendation
        try:
            routing = self.model_router.route(
                task=text,
                context=channel,
                preference_context="default",
            )
            result["model_recommendation"] = routing
        except Exception as e:
            logger.debug(f"Model routing failed (using default): {e}")

        # Trust level check
        if self.config.trust_tracking_enabled:
            try:
                level = self.trust_engine.get_autonomy_level()
                result["trust_level"] = level.value if hasattr(level, 'value') else level
            except Exception as e:
                logger.debug(f"Trust check failed: {e}")

        return result

    async def _build_memory_context(
        self, user_id: str, query: str, session: MiddlewareSession
    ) -> str:
        """Build a formatted memory context block using KnowledgeRepository and ContextBudgetManager."""
        parts = []

        # Recall relevant knowledge
        try:
            recall_results = self.knowledge.recall(
                query,
                memory_types=["semantic", "procedural", "episodic"],
                limit=10,
            )
            if recall_results:
                # Use context budget manager to allocate and pack
                allocation = self.budget_manager.allocate_budget(
                    task_context="conversation",
                    base_prompt_tokens=len(query.split()) * 2,  # rough estimate
                )

                # Separate by type
                episodic_items = [r for r in recall_results if r.get("memory_type") == "episodic"]
                semantic_items = [r for r in recall_results if r.get("memory_type") == "semantic"]
                procedural_items = [r for r in recall_results if r.get("memory_type") == "procedural"]

                packed = self.budget_manager.pack_knowledge(
                    allocation=allocation,
                    episodic_items=episodic_items,
                    semantic_items=semantic_items,
                    procedural_items=procedural_items,
                    graph_items=[],
                )

                context_payload = self.budget_manager.assemble_context(packed)
                if context_payload:
                    parts.append(context_payload)

        except Exception as e:
            logger.debug(f"Recall failed, falling back to direct query: {e}")
            # Fallback: direct preference query
            try:
                prefs = self.knowledge.recall_preferences()
                if prefs:
                    prefs_text = "\n".join(
                        f"- {p.get('procedure_name', 'Preference')}: {p.get('content', p.get('description', ''))}"
                        for p in prefs[:5]
                    )
                    parts.append(f"**User Preferences:**\n{prefs_text}")
            except Exception:
                pass

        # Recent events
        try:
            recent = self.knowledge.recall_recent_events(days=7)
            if recent:
                events_text = "\n".join(
                    f"- [{e.get('event_type', 'event')}] {e.get('summary', '')}"
                    for e in recent[:3]
                )
                parts.append(f"**Recent Activity:**\n{events_text}")
        except Exception:
            pass

        if not parts:
            return ""

        return "\n--- Memory Context ---\n" + "\n\n".join(parts) + "\n--- End Context ---"

    # -------------------------------------------------------------------------
    # POST-MESSAGE HOOK
    # -------------------------------------------------------------------------

    async def post_message(
        self,
        user_text: str,
        ai_response: str,
        user_id: str,
        channel: str,
        chat_id: str = "",
    ) -> None:
        """
        Post-message hook: called after the AI model responds.

        Extracts learnings, logs to trust ledger, updates conversation history.
        """
        session = self.get_or_create_session(user_id, channel, chat_id)

        # Audit log (lengths only — not content, for privacy)
        self.audit.log_message(user_id, channel, len(user_text), len(ai_response))

        # Update conversation history
        session.add_turn(user_text, ai_response, max_turns=self.config.max_history_turns)

        # Auto-learn from corrections
        if self.config.auto_learn_enabled and self.config.correction_detection_enabled:
            if detect_correction(user_text):
                session.pending_learnings.append({
                    "type": "preference",
                    "content": user_text,
                    "confidence": 0.85,
                    "source": "auto_correction_detection",
                })
                logger.info(f"Auto-captured correction: {user_text[:80]}...")
                self.audit.log_learning(user_id, channel, "preference", "auto_correction")

            if detect_decision(user_text):
                session.pending_learnings.append({
                    "type": "event",
                    "event_type": "decision",
                    "content": user_text,
                    "participants": [user_id],
                    "confidence": 0.75,
                    "source": "auto_decision_detection",
                })
                logger.info(f"Auto-captured decision: {user_text[:80]}...")
                self.audit.log_learning(user_id, channel, "event", "auto_decision")

        # Log to Trust Ledger
        if self.config.trust_tracking_enabled:
            try:
                record_kwargs = {
                    "action": f"respond_on_{channel}",
                    "success": True,
                    "details": {"channel": channel, "message_length": len(user_text)},
                }
                if hasattr(ActionCategory, "COMMUNICATION"):
                    record_kwargs["category"] = ActionCategory.COMMUNICATION
                self.trust_engine.record_outcome(**record_kwargs)
            except Exception as e:
                logger.debug(f"Trust logging failed: {e}")

        # Heartbeat — periodic REFLECT
        if (
            session.message_count > 0
            and session.message_count % self.config.heartbeat_interval_messages == 0
        ):
            await self._heartbeat_reflect(session)

        # Flush pending learnings if we have enough
        if len(session.pending_learnings) >= 5:
            self._flush_session(session)

    # -------------------------------------------------------------------------
    # REACTION HOOK
    # -------------------------------------------------------------------------

    async def on_reaction(
        self,
        message_id: str,
        emoji: str,
        user_id: str,
        channel: str,
    ) -> None:
        """
        Capture reactions as reward signals.

        Positive reactions (thumbs up, heart, etc.) increase confidence.
        Negative reactions (thumbs down) decrease confidence.
        """
        positive_emojis = {"👍", "❤️", "🎉", "✅", "💯", "🔥", "⭐"}
        negative_emojis = {"👎", "❌", "😕", "🤔"}

        if emoji in positive_emojis:
            signal = 1.0
            logger.info(f"Positive feedback from {user_id} on {channel}")
        elif emoji in negative_emojis:
            signal = -1.0
            logger.info(f"Negative feedback from {user_id} on {channel}")
        else:
            return  # Ignore other reactions

        # Record as episodic event
        try:
            self.knowledge.learn_event(
                event_type="feedback",
                summary=f"User reacted with {emoji} (signal: {signal})",
                participants=[user_id],
            )
        except Exception as e:
            logger.debug(f"Failed to record reaction: {e}")

    # -------------------------------------------------------------------------
    # HEARTBEAT — Periodic REFLECT
    # -------------------------------------------------------------------------

    async def _heartbeat_reflect(self, session: MiddlewareSession) -> None:
        """Trigger periodic REFLECT synthesis."""
        try:
            insights = self.knowledge.reflect(days=7)
            if insights:
                logger.info(
                    f"Heartbeat REFLECT for {session.user_id}: "
                    f"{len(insights) if isinstance(insights, list) else 'completed'}"
                )
        except Exception as e:
            logger.debug(f"Heartbeat reflect failed: {e}")

    # -------------------------------------------------------------------------
    # CROSS-CHANNEL IDENTITY LINKING
    # -------------------------------------------------------------------------

    def link_identity(
        self,
        primary_user_id: str,
        channel_user_id: str,
        channel: str,
    ) -> None:
        """
        Link a channel-specific user ID to a primary A2I2 user ID.

        Enables cross-channel memory: a user on WhatsApp and Discord
        shares the same knowledge graph.
        """
        try:
            self.knowledge.relate(
                source_type="user",
                source_name=primary_user_id,
                relationship="has_channel_identity",
                target_type="channel_identity",
                target_name=f"{channel}:{channel_user_id}",
                properties={"channel": channel, "linked_at": datetime.now(timezone.utc).isoformat()},
            )
            logger.info(f"Linked identity: {primary_user_id} ↔ {channel}:{channel_user_id}")
        except Exception as e:
            logger.error(f"Identity linking failed: {e}")

    def resolve_identity(self, channel_user_id: str, channel: str) -> Optional[str]:
        """
        Resolve a channel-specific user ID to their primary A2I2 user ID.

        Returns the primary user ID if found, None otherwise.
        """
        if not self.knowledge.supabase:
            return None

        try:
            result = self.knowledge.supabase.table("arcus_relationships").select(
                "source_name"
            ).eq(
                "relationship", "has_channel_identity"
            ).eq(
                "target_name", f"{channel}:{channel_user_id}"
            ).limit(1).execute()

            if result.data:
                return result.data[0]["source_name"]
        except Exception as e:
            logger.debug(f"Identity resolution failed: {e}")

        return None

    # -------------------------------------------------------------------------
    # STATUS
    # -------------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Get middleware status."""
        active_sessions = len(self._sessions)
        db_connected = self.knowledge.supabase is not None

        trust_info = {}
        try:
            trust_info = self.trust_engine.get_trust_statistics()
        except Exception:
            pass

        return {
            "active_sessions": active_sessions,
            "database_connected": db_connected,
            "memory_injection": self.config.memory_injection_enabled,
            "auto_learn": self.config.auto_learn_enabled,
            "trust_tracking": self.config.trust_tracking_enabled,
            "trust_info": trust_info,
            "verbosity_level": self.config.verbosity_level,
        }
