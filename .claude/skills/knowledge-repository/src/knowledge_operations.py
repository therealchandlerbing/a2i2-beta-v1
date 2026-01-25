"""
Arcus Knowledge Repository - Core Operations

This module provides the foundational LEARN, RECALL, RELATE, and REFLECT
operations for the knowledge repository. It serves as a reference implementation
that can be used by Claude or integrated into automation workflows.

Usage:
    from knowledge_operations import KnowledgeRepository

    repo = KnowledgeRepository(supabase_url, supabase_key)

    # Learn something
    repo.learn_preference("User prefers TypeScript", confidence=0.95)

    # Recall knowledge
    results = repo.recall("TypeScript preferences", memory_types=["procedural"])

    # Relate entities
    repo.relate("Sarah Chen", "works_at", "TechCorp", {"role": "CIO"})

    # Reflect on learnings
    insights = repo.reflect(days=30)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# =============================================================================
# ENUMS AND TYPES
# =============================================================================

class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    GRAPH = "graph"


class EventType(Enum):
    CONVERSATION = "conversation"
    DECISION = "decision"
    MEETING = "meeting"
    MILESTONE = "milestone"
    ERROR = "error"
    SUCCESS = "success"
    FEEDBACK = "feedback"
    CORRECTION = "correction"


class SemanticCategory(Enum):
    FACT = "fact"
    PATTERN = "pattern"
    FRAMEWORK = "framework"
    DEFINITION = "definition"
    BEST_PRACTICE = "best_practice"
    INSIGHT = "insight"
    PREFERENCE = "preference"


class ProcedureType(Enum):
    WORKFLOW = "workflow"
    PREFERENCE = "preference"
    STANDARD = "standard"
    TEMPLATE = "template"
    DECISION_TREE = "decision_tree"


class SourceType(Enum):
    USER_EXPLICIT = "user_explicit"
    USER_IMPLICIT = "user_implicit"
    EXTRACTION = "extraction"
    INFERENCE = "inference"
    INTEGRATION = "integration"
    SYSTEM = "system"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class KnowledgeSource:
    """Tracks where knowledge came from."""
    type: SourceType
    session_id: Optional[str] = None
    interaction_id: Optional[str] = None
    document_ref: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "session_id": self.session_id,
            "interaction_id": self.interaction_id,
            "document_ref": self.document_ref,
            "note": self.note
        }


@dataclass
class EpisodicEntry:
    """An episodic memory entry (what happened)."""
    event_type: EventType
    summary: str
    participants: List[str]
    outcome: Optional[str] = None
    learnings: Optional[List[str]] = None
    confidence: float = 0.8
    importance: str = "normal"
    source: Optional[KnowledgeSource] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "summary": self.summary,
            "participants": self.participants,
            "outcome": self.outcome,
            "learnings": self.learnings or [],
            "confidence": self.confidence,
            "importance": self.importance,
            "source": self.source.to_dict() if self.source else {},
            "event_timestamp": datetime.utcnow().isoformat()
        }


@dataclass
class SemanticEntry:
    """A semantic memory entry (what we know)."""
    category: SemanticCategory
    statement: str
    domain: Optional[str] = None
    evidence: Optional[List[str]] = None
    confidence: float = 0.8
    source: Optional[KnowledgeSource] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "statement": self.statement,
            "domain": self.domain,
            "evidence": self.evidence or [],
            "confidence": self.confidence,
            "source": self.source.to_dict() if self.source else {}
        }


@dataclass
class ProceduralEntry:
    """A procedural memory entry (how we work)."""
    procedure_type: ProcedureType
    name: str
    description: Optional[str] = None
    preference_value: Optional[Dict[str, Any]] = None
    trigger_conditions: Optional[List[str]] = None
    confidence: float = 0.8
    source: Optional[KnowledgeSource] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "procedure_type": self.procedure_type.value,
            "name": self.name,
            "description": self.description,
            "preference_value": self.preference_value,
            "trigger_conditions": self.trigger_conditions or [],
            "confidence": self.confidence,
            "source": self.source.to_dict() if self.source else {}
        }


@dataclass
class EntityEntry:
    """A knowledge graph entity."""
    entity_type: str
    name: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    aliases: Optional[List[str]] = None
    confidence: float = 0.8
    source: Optional[KnowledgeSource] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes or {},
            "aliases": self.aliases or [],
            "confidence": self.confidence,
            "source": self.source.to_dict() if self.source else {}
        }


@dataclass
class RelationshipEntry:
    """A knowledge graph relationship."""
    source_type: str
    source_name: str
    relationship: str
    target_type: str
    target_name: str
    properties: Optional[Dict[str, Any]] = None
    confidence: float = 0.8
    source: Optional[KnowledgeSource] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_name": self.source_name,
            "relationship": self.relationship,
            "target_type": self.target_type,
            "target_name": self.target_name,
            "properties": self.properties or {},
            "confidence": self.confidence,
            "source": self.source.to_dict() if self.source else {}
        }


# =============================================================================
# KNOWLEDGE REPOSITORY
# =============================================================================

class KnowledgeRepository:
    """
    Main interface for the Arcus Knowledge Repository.

    This class provides LEARN, RECALL, RELATE, and REFLECT operations
    for managing persistent knowledge across sessions.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        memory_file: str = "CLAUDE.memory.md"
    ):
        """
        Initialize the knowledge repository.

        Args:
            supabase_url: Supabase project URL (optional, for persistent storage)
            supabase_key: Supabase anon key (optional)
            memory_file: Path to CLAUDE.memory.md file
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_ANON_KEY")
        self.memory_file = memory_file
        self.supabase = None

        # Initialize Supabase client if credentials provided
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                print("Warning: supabase-py not installed. Using file-only storage.")

        # Local queue for batch operations
        self._pending_queue: List[Dict[str, Any]] = []

    # =========================================================================
    # LEARN OPERATIONS
    # =========================================================================

    def learn(
        self,
        memory_type: MemoryType,
        entry: Any,
        batch: bool = False
    ) -> Optional[str]:
        """
        Store new knowledge in the repository.

        Args:
            memory_type: Type of memory (episodic, semantic, procedural)
            entry: The entry to store (EpisodicEntry, SemanticEntry, etc.)
            batch: If True, queue for batch insert instead of immediate

        Returns:
            Entry ID if immediate insert, None if batched
        """
        data = entry.to_dict()

        if batch:
            self._pending_queue.append({
                "type": memory_type.value,
                "data": data
            })
            return None

        if self.supabase:
            table = f"arcus_{memory_type.value}_memory"
            result = self.supabase.table(table).insert(data).execute()
            return result.data[0]["id"] if result.data else None
        else:
            # Fallback to file-based storage
            self._append_to_memory_file(memory_type.value, data)
            return "file-based"

    def learn_preference(
        self,
        preference: str,
        value: Optional[Any] = None,
        confidence: float = 0.9,
        source_type: SourceType = SourceType.USER_EXPLICIT
    ) -> Optional[str]:
        """
        Convenience method to learn a user preference.

        Args:
            preference: Description of the preference
            value: Optional structured value
            confidence: Confidence score (0-1)
            source_type: How this was learned

        Returns:
            Entry ID
        """
        entry = ProceduralEntry(
            procedure_type=ProcedureType.PREFERENCE,
            name=preference[:50],  # Truncate for name field
            description=preference,
            preference_value={"value": value} if value else None,
            confidence=confidence,
            source=KnowledgeSource(type=source_type)
        )
        return self.learn(MemoryType.PROCEDURAL, entry)

    def learn_fact(
        self,
        statement: str,
        domain: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        confidence: float = 0.8
    ) -> Optional[str]:
        """
        Convenience method to learn a fact.

        Args:
            statement: The factual statement
            domain: Knowledge domain (e.g., "clients", "technology")
            evidence: Supporting evidence
            confidence: Confidence score (0-1)

        Returns:
            Entry ID
        """
        entry = SemanticEntry(
            category=SemanticCategory.FACT,
            statement=statement,
            domain=domain,
            evidence=evidence,
            confidence=confidence,
            source=KnowledgeSource(type=SourceType.USER_EXPLICIT)
        )
        return self.learn(MemoryType.SEMANTIC, entry)

    def learn_event(
        self,
        event_type: EventType,
        summary: str,
        participants: Optional[List[str]] = None,
        outcome: Optional[str] = None,
        learnings: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Convenience method to record an event.

        Args:
            event_type: Type of event
            summary: What happened
            participants: Who was involved
            outcome: What was the result
            learnings: What we learned

        Returns:
            Entry ID
        """
        entry = EpisodicEntry(
            event_type=event_type,
            summary=summary,
            participants=participants or [],
            outcome=outcome,
            learnings=learnings,
            source=KnowledgeSource(type=SourceType.USER_EXPLICIT)
        )
        return self.learn(MemoryType.EPISODIC, entry)

    # =========================================================================
    # RECALL OPERATIONS
    # =========================================================================

    def recall(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        min_confidence: float = 0.5,
        days_back: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve relevant knowledge from the repository.

        Args:
            query: Search query
            memory_types: Which memory types to search (default: all)
            limit: Maximum results per type
            min_confidence: Minimum confidence threshold
            days_back: Only search within this many days

        Returns:
            Dictionary of results keyed by memory type
        """
        if memory_types is None:
            memory_types = [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]

        results = {}

        for memory_type in memory_types:
            type_results = self._recall_by_type(
                query, memory_type, limit, min_confidence, days_back
            )
            results[memory_type.value] = type_results

        return results

    def _recall_by_type(
        self,
        query: str,
        memory_type: MemoryType,
        limit: int,
        min_confidence: float,
        days_back: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Recall from a specific memory type."""
        if not self.supabase:
            return self._recall_from_file(query, memory_type.value)

        table = f"arcus_{memory_type.value}_memory"

        # Build query
        q = self.supabase.table(table).select("*")
        q = q.gte("confidence", min_confidence)
        q = q.order("created_at", desc=True)
        q = q.limit(limit)

        if days_back:
            cutoff = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            q = q.gte("created_at", cutoff)

        result = q.execute()
        return result.data if result.data else []

    def recall_preferences(self) -> List[Dict[str, Any]]:
        """
        Recall all user preferences.

        Returns:
            List of preference entries
        """
        if self.supabase:
            result = self.supabase.table("arcus_procedural_memory") \
                .select("*") \
                .eq("procedure_type", "preference") \
                .order("created_at", desc=True) \
                .execute()
            return result.data if result.data else []
        return []

    def recall_recent_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Recall recent episodic events.

        Args:
            days: Number of days to look back

        Returns:
            List of recent events
        """
        return self.recall("", [MemoryType.EPISODIC], limit=50, days_back=days).get("episodic", [])

    # =========================================================================
    # RELATE OPERATIONS
    # =========================================================================

    def relate(
        self,
        source_name: str,
        relationship: str,
        target_name: str,
        properties: Optional[Dict[str, Any]] = None,
        source_type: str = "person",
        target_type: str = "organization",
        confidence: float = 0.8
    ) -> Optional[str]:
        """
        Create a relationship between two entities in the knowledge graph.

        Args:
            source_name: Name of the source entity
            relationship: Type of relationship
            target_name: Name of the target entity
            properties: Additional properties for the relationship
            source_type: Type of source entity
            target_type: Type of target entity
            confidence: Confidence score

        Returns:
            Relationship ID
        """
        # First, ensure entities exist
        self._ensure_entity(source_type, source_name)
        self._ensure_entity(target_type, target_name)

        # Create relationship
        entry = RelationshipEntry(
            source_type=source_type,
            source_name=source_name,
            relationship=relationship,
            target_type=target_type,
            target_name=target_name,
            properties=properties,
            confidence=confidence,
            source=KnowledgeSource(type=SourceType.USER_EXPLICIT)
        )

        if self.supabase:
            result = self.supabase.table("arcus_relationships").insert(entry.to_dict()).execute()
            return result.data[0]["id"] if result.data else None

        return "file-based"

    def _ensure_entity(self, entity_type: str, name: str) -> None:
        """Ensure an entity exists in the registry."""
        if not self.supabase:
            return

        # Check if exists
        result = self.supabase.table("arcus_entities") \
            .select("id") \
            .eq("entity_type", entity_type) \
            .eq("name", name) \
            .execute()

        if not result.data:
            # Create entity
            self.supabase.table("arcus_entities").insert({
                "entity_type": entity_type,
                "name": name,
                "source": {"type": "system", "note": "auto-created from relationship"}
            }).execute()

    def get_entity_relationships(
        self,
        entity_name: str,
        entity_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all relationships for an entity.

        Args:
            entity_name: Name of the entity
            entity_type: Optional type filter

        Returns:
            List of relationships
        """
        if not self.supabase:
            return []

        # Get relationships where entity is source
        q1 = self.supabase.table("arcus_relationships") \
            .select("*") \
            .eq("source_name", entity_name)
        if entity_type:
            q1 = q1.eq("source_type", entity_type)

        # Get relationships where entity is target
        q2 = self.supabase.table("arcus_relationships") \
            .select("*") \
            .eq("target_name", entity_name)
        if entity_type:
            q2 = q2.eq("target_type", entity_type)

        r1 = q1.execute()
        r2 = q2.execute()

        return (r1.data or []) + (r2.data or [])

    # =========================================================================
    # REFLECT OPERATIONS
    # =========================================================================

    def reflect(
        self,
        days: int = 30,
        focus_areas: Optional[List[str]] = None,
        min_evidence: int = 2
    ) -> Dict[str, Any]:
        """
        Synthesize insights from recent learnings.

        Args:
            days: Number of days to analyze
            focus_areas: Optional domains to focus on
            min_evidence: Minimum evidence count for patterns

        Returns:
            Dictionary with insights and recommendations
        """
        # Get recent data
        recent_events = self.recall_recent_events(days)
        preferences = self.recall_preferences()

        # Analyze patterns (simplified)
        patterns = []

        # Count event types
        event_counts: Dict[str, int] = {}
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        for event_type, count in event_counts.items():
            if count >= min_evidence:
                patterns.append({
                    "type": "event_frequency",
                    "pattern": f"{count} {event_type} events in last {days} days",
                    "evidence_count": count,
                    "confidence": min(0.9, 0.5 + (count * 0.1))
                })

        return {
            "period": {
                "days": days,
                "start": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "summary": {
                "total_events": len(recent_events),
                "total_preferences": len(preferences),
                "patterns_found": len(patterns)
            },
            "patterns": patterns,
            "recommendations": self._generate_recommendations(patterns, preferences)
        }

    def _generate_recommendations(
        self,
        patterns: List[Dict[str, Any]],
        preferences: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations from patterns and preferences."""
        recommendations = []

        # Add basic recommendations based on patterns
        for pattern in patterns:
            if pattern.get("type") == "event_frequency":
                if "error" in pattern.get("pattern", "").lower():
                    recommendations.append(
                        "Consider reviewing error patterns for common root causes"
                    )
                if "success" in pattern.get("pattern", "").lower():
                    recommendations.append(
                        "Document successful patterns as procedural memory"
                    )

        return recommendations

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def flush_pending(self) -> int:
        """
        Flush pending batch operations to storage.

        Returns:
            Number of items flushed
        """
        if not self._pending_queue:
            return 0

        count = len(self._pending_queue)

        for item in self._pending_queue:
            memory_type = MemoryType(item["type"])
            if self.supabase:
                table = f"arcus_{memory_type.value}_memory"
                self.supabase.table(table).insert(item["data"]).execute()
            else:
                self._append_to_memory_file(memory_type.value, item["data"])

        self._pending_queue = []
        return count

    def _append_to_memory_file(self, memory_type: str, data: Dict[str, Any]) -> None:
        """Append an entry to the memory file (fallback storage)."""
        # This is a simplified file-based storage
        timestamp = datetime.utcnow().isoformat()
        entry = f"\n| {timestamp} | {memory_type} | {data.get('summary', data.get('statement', data.get('name', 'unknown')))} | {data.get('confidence', 0.8)} |"

        if os.path.exists(self.memory_file):
            with open(self.memory_file, "a") as f:
                f.write(entry)

    def _recall_from_file(self, query: str, memory_type: str) -> List[Dict[str, Any]]:
        """Recall from file-based storage (simplified)."""
        # In a real implementation, this would parse the memory file
        return []

    def get_stats(self) -> Dict[str, Any]:
        """Get repository statistics."""
        stats = {
            "pending_queue_size": len(self._pending_queue),
            "supabase_connected": self.supabase is not None,
            "memory_file": self.memory_file,
            "memory_file_exists": os.path.exists(self.memory_file)
        }

        if self.supabase:
            # Get counts from each table
            for table in ["episodic", "semantic", "procedural"]:
                result = self.supabase.table(f"arcus_{table}_memory") \
                    .select("id", count="exact") \
                    .execute()
                stats[f"{table}_count"] = result.count if result.count else 0

        return stats


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_repository() -> KnowledgeRepository:
    """Create a repository instance using environment variables."""
    return KnowledgeRepository()


def learn_from_correction(correction: str, context: Optional[str] = None) -> Optional[str]:
    """
    Quick function to learn from a user correction.

    Args:
        correction: The correction or preference
        context: Optional context

    Returns:
        Entry ID
    """
    repo = create_repository()
    return repo.learn_preference(
        correction,
        value={"context": context} if context else None,
        confidence=0.95,
        source_type=SourceType.USER_EXPLICIT
    )


def record_decision(
    decision: str,
    rationale: Optional[str] = None,
    participants: Optional[List[str]] = None
) -> Optional[str]:
    """
    Quick function to record a decision.

    Args:
        decision: What was decided
        rationale: Why
        participants: Who was involved

    Returns:
        Entry ID
    """
    repo = create_repository()
    return repo.learn_event(
        event_type=EventType.DECISION,
        summary=decision,
        participants=participants,
        learnings=[rationale] if rationale else None
    )


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("Arcus Knowledge Repository - Test Run")
    print("=" * 50)

    repo = KnowledgeRepository()

    # Show stats
    stats = repo.get_stats()
    print(f"Repository Stats: {json.dumps(stats, indent=2)}")

    # Example: Learn a preference
    print("\nLearning a preference...")
    result = repo.learn_preference(
        "User prefers TypeScript for new projects",
        confidence=0.9
    )
    print(f"Learned: {result}")

    # Example: Learn a fact
    print("\nLearning a fact...")
    result = repo.learn_fact(
        "Arcus Innovation Studios focuses on AI innovation",
        domain="organization"
    )
    print(f"Learned: {result}")

    # Example: Record an event
    print("\nRecording an event...")
    result = repo.learn_event(
        EventType.DECISION,
        "Decided to build knowledge repository",
        participants=["Chandler", "Claude"],
        outcome="Architecture completed",
        learnings=["Modular architecture is preferred", "Future-proof design is important"]
    )
    print(f"Recorded: {result}")

    print("\nTest complete!")
