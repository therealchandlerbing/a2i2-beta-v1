"""
Arcus Context Budget Manager - Dynamic Context Budgeting

This module provides intelligent context management for LLM prompts:
1. Token counting and estimation
2. Dynamic budget allocation across memory types
3. Quality-based ranking and selection of knowledge
4. Token-efficient packing within model context limits

Implements the "Context Budgeting" enhancement from Phase 2.

Usage:
    from context_budget import ContextBudgetManager

    manager = ContextBudgetManager(max_context=200000)

    # Allocate budget for a task
    allocation = manager.allocate_budget(
        task_context="code_review",
        base_prompt_tokens=5000,
        priority_weights={"procedural": 0.4, "semantic": 0.3, "episodic": 0.2, "graph": 0.1}
    )

    # Select and pack knowledge within budget
    packed = manager.pack_knowledge(
        allocation=allocation,
        episodic_items=recent_events,
        semantic_items=relevant_facts,
        procedural_items=workflows,
        graph_items=relationships
    )

    # Get the assembled context
    context_payload = manager.assemble_context(packed)
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import math


# =============================================================================
# CONSTANTS
# =============================================================================

# Average characters per token (approximate for GPT/Claude tokenizers)
CHARS_PER_TOKEN = 4.0

# Model context limits
MODEL_CONTEXT_LIMITS = {
    "claude-opus": 200000,
    "claude-sonnet": 200000,
    "claude-haiku": 200000,
    "gemini-3-pro": 1048576,
    "gemini-3-flash": 1048576,
    "gemini-2.5-flash": 1048576,
    "personaplex": 32000,
    "deep-research": 1048576,
    "default": 128000
}

# Default allocation weights by memory type
DEFAULT_ALLOCATION_WEIGHTS = {
    "procedural": 0.35,  # Highest priority - how we work
    "semantic": 0.30,    # Facts and patterns
    "episodic": 0.25,    # Recent events
    "graph": 0.10        # Relationships (usually compact)
}

# Minimum tokens per memory type (ensure some context from each)
MIN_TOKENS_PER_TYPE = {
    "procedural": 500,
    "semantic": 500,
    "episodic": 300,
    "graph": 200
}

# Context overhead (system prompt, formatting, safety margin)
CONTEXT_OVERHEAD_RATIO = 0.15  # Reserve 15% for overhead
MAX_SINGLE_ITEM_RATIO = 0.20   # No single item can take more than 20% of budget


# =============================================================================
# ENUMS
# =============================================================================

class RankingStrategy(Enum):
    RECENCY = "recency"           # Prefer recent items
    CONFIDENCE = "confidence"     # Prefer high confidence items
    RELEVANCE = "relevance"       # Prefer relevant items (requires query)
    BALANCED = "balanced"         # Balance all factors
    IMPORTANCE = "importance"     # Prefer high importance items


class PackingStrategy(Enum):
    GREEDY = "greedy"             # Fill highest-ranked items first
    DIVERSE = "diverse"           # Ensure diversity across categories
    DENSE = "dense"               # Maximize information density


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TokenEstimate:
    """Token count estimate for a piece of content."""
    content_tokens: int
    metadata_tokens: int
    total_tokens: int
    char_count: int
    confidence: float  # 0-1, how confident we are in the estimate


@dataclass
class BudgetAllocation:
    """Budget allocation result."""
    total_available: int
    reserved_for_prompt: int
    reserved_for_response: int
    reserved_for_overhead: int
    available_for_context: int
    allocation_by_type: Dict[str, int]
    priority_weights: Dict[str, float]


@dataclass
class RankedItem:
    """A knowledge item with ranking score."""
    item: Dict[str, Any]
    memory_type: str
    token_estimate: int
    rank_score: float
    recency_score: float
    confidence_score: float
    relevance_score: float
    importance_score: float
    selected: bool = False


@dataclass
class PackedContext:
    """Result of packing knowledge into context."""
    items_by_type: Dict[str, List[Dict[str, Any]]]
    tokens_by_type: Dict[str, int]
    total_tokens: int
    total_items: int
    dropped_items: int
    coverage_by_type: Dict[str, float]  # What % of allocation was used
    packing_strategy: PackingStrategy
    ranking_strategy: RankingStrategy


@dataclass
class ContextPayload:
    """Final assembled context ready for injection."""
    formatted_context: str
    total_tokens: int
    sections: Dict[str, str]
    metadata: Dict[str, Any]


# =============================================================================
# TOKEN ESTIMATION
# =============================================================================

class TokenEstimator:
    """
    Estimates token counts for various content types.

    Uses character-based estimation with adjustments for:
    - Code (more tokens per char)
    - JSON/structured data
    - Markdown formatting
    """

    def __init__(self, chars_per_token: float = CHARS_PER_TOKEN):
        self.chars_per_token = chars_per_token

    def estimate(self, content: Any, include_metadata: bool = True) -> TokenEstimate:
        """
        Estimate tokens for content.

        Args:
            content: The content to estimate (str, dict, list, etc.)
            include_metadata: Whether to include metadata overhead

        Returns:
            Token estimate with breakdown
        """
        if isinstance(content, str):
            text = content
        elif isinstance(content, dict):
            text = self._dict_to_text(content)
        elif isinstance(content, list):
            text = "\n".join(self._dict_to_text(item) if isinstance(item, dict) else str(item) for item in content)
        else:
            text = str(content)

        char_count = len(text)

        # Adjust for content type
        multiplier = self._get_content_multiplier(text)

        content_tokens = int(char_count / self.chars_per_token * multiplier)

        # Add metadata overhead (roughly 10-20 tokens for typical metadata)
        metadata_tokens = 15 if include_metadata else 0

        total_tokens = content_tokens + metadata_tokens

        # Confidence based on content length (longer = more accurate estimate)
        confidence = min(0.95, 0.5 + (char_count / 10000) * 0.45)

        return TokenEstimate(
            content_tokens=content_tokens,
            metadata_tokens=metadata_tokens,
            total_tokens=total_tokens,
            char_count=char_count,
            confidence=confidence
        )

    def estimate_batch(self, items: List[Any]) -> List[TokenEstimate]:
        """Estimate tokens for a batch of items."""
        return [self.estimate(item) for item in items]

    def _dict_to_text(self, d: Dict[str, Any]) -> str:
        """Convert dict to readable text for estimation."""
        parts = []
        for key, value in d.items():
            if value is not None and value != "" and value != []:
                if isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value)
                elif isinstance(value, dict):
                    value_str = str(value)
                else:
                    value_str = str(value)
                parts.append(f"{key}: {value_str}")
        return "\n".join(parts)

    def _get_content_multiplier(self, text: str) -> float:
        """
        Get multiplier based on content type.
        Code and structured data tend to have more tokens per character.
        """
        # Check for code indicators
        code_indicators = [
            "def ", "class ", "function ", "const ", "let ", "var ",
            "import ", "from ", "export ", "return ", "async ", "await "
        ]
        code_count = sum(1 for indicator in code_indicators if indicator in text)

        # Check for JSON/structured data
        json_indicators = ["{", "}", "[", "]", '": ', "': "]
        json_count = sum(text.count(indicator) for indicator in json_indicators)

        # Base multiplier
        multiplier = 1.0

        # Adjust for code (more tokens)
        if code_count > 3:
            multiplier *= 1.2
        elif code_count > 0:
            multiplier *= 1.1

        # Adjust for structured data
        if json_count > 10:
            multiplier *= 1.15

        return multiplier


# =============================================================================
# CONTEXT BUDGET MANAGER
# =============================================================================

class ContextBudgetManager:
    """
    Manages context budget allocation and knowledge packing.

    Core responsibilities:
    1. Calculate available context budget based on model limits
    2. Allocate budget across memory types
    3. Rank and select knowledge items
    4. Pack selected items efficiently
    5. Format context for injection
    """

    def __init__(
        self,
        model_id: str = "default",
        max_context: Optional[int] = None,
        estimator: Optional[TokenEstimator] = None
    ):
        """
        Initialize the context budget manager.

        Args:
            model_id: Model identifier for context limits
            max_context: Override maximum context (if None, use model default)
            estimator: Token estimator instance
        """
        self.model_id = model_id
        self.max_context = max_context or MODEL_CONTEXT_LIMITS.get(model_id, MODEL_CONTEXT_LIMITS["default"])
        self.estimator = estimator or TokenEstimator()

    # =========================================================================
    # BUDGET ALLOCATION
    # =========================================================================

    def allocate_budget(
        self,
        base_prompt_tokens: int = 0,
        expected_response_tokens: int = 4000,
        task_context: Optional[str] = None,
        priority_weights: Optional[Dict[str, float]] = None
    ) -> BudgetAllocation:
        """
        Allocate context budget across memory types.

        Args:
            base_prompt_tokens: Tokens already used by system prompt
            expected_response_tokens: Expected output token count
            task_context: Optional task context for weight adjustment
            priority_weights: Custom weights for memory types

        Returns:
            Budget allocation with per-type limits
        """
        # Calculate total available
        overhead = int(self.max_context * CONTEXT_OVERHEAD_RATIO)
        total_for_context = self.max_context - base_prompt_tokens - expected_response_tokens - overhead

        # Ensure positive budget
        total_for_context = max(total_for_context, 1000)

        # Get weights (custom or adjusted for task context)
        weights = priority_weights or self._get_task_weights(task_context)

        # Normalize weights
        weight_sum = sum(weights.values())
        normalized_weights = {k: v / weight_sum for k, v in weights.items()}

        # Allocate based on weights, respecting minimums
        allocation_by_type = {}
        remaining = total_for_context

        # First, ensure minimums
        for mem_type, min_tokens in MIN_TOKENS_PER_TYPE.items():
            if mem_type in normalized_weights:
                allocation_by_type[mem_type] = min(min_tokens, remaining)
                remaining -= allocation_by_type[mem_type]

        # Distribute remaining based on weights
        if remaining > 0:
            for mem_type, weight in normalized_weights.items():
                extra = int(remaining * weight)
                allocation_by_type[mem_type] = allocation_by_type.get(mem_type, 0) + extra

        return BudgetAllocation(
            total_available=self.max_context,
            reserved_for_prompt=base_prompt_tokens,
            reserved_for_response=expected_response_tokens,
            reserved_for_overhead=overhead,
            available_for_context=total_for_context,
            allocation_by_type=allocation_by_type,
            priority_weights=normalized_weights
        )

    def _get_task_weights(self, task_context: Optional[str]) -> Dict[str, float]:
        """Get allocation weights based on task context."""
        # Task-specific weight adjustments
        task_weights = {
            "code_review": {"procedural": 0.4, "semantic": 0.35, "episodic": 0.15, "graph": 0.1},
            "document_analysis": {"semantic": 0.45, "procedural": 0.25, "episodic": 0.2, "graph": 0.1},
            "conversation": {"episodic": 0.4, "procedural": 0.3, "semantic": 0.2, "graph": 0.1},
            "research": {"semantic": 0.5, "episodic": 0.2, "procedural": 0.2, "graph": 0.1},
            "voice_response": {"procedural": 0.5, "semantic": 0.25, "episodic": 0.2, "graph": 0.05},
            "relationship_query": {"graph": 0.5, "semantic": 0.25, "episodic": 0.15, "procedural": 0.1},
        }

        return task_weights.get(task_context, DEFAULT_ALLOCATION_WEIGHTS)

    # =========================================================================
    # RANKING
    # =========================================================================

    def rank_items(
        self,
        items: List[Dict[str, Any]],
        memory_type: str,
        strategy: RankingStrategy = RankingStrategy.BALANCED,
        query: Optional[str] = None,
        reference_time: Optional[datetime] = None
    ) -> List[RankedItem]:
        """
        Rank knowledge items for selection.

        Args:
            items: List of knowledge items
            memory_type: Type of memory (episodic, semantic, etc.)
            strategy: Ranking strategy to use
            query: Optional query for relevance scoring
            reference_time: Reference time for recency scoring

        Returns:
            Sorted list of ranked items (highest rank first)
        """
        if not items:
            return []

        reference_time = reference_time or datetime.utcnow()
        ranked = []

        for item in items:
            # Estimate tokens
            token_estimate = self.estimator.estimate(item).total_tokens

            # Calculate component scores
            recency_score = self._score_recency(item, reference_time)
            confidence_score = self._score_confidence(item)
            relevance_score = self._score_relevance(item, query) if query else 0.5
            importance_score = self._score_importance(item, memory_type)

            # Combine based on strategy
            rank_score = self._combine_scores(
                strategy=strategy,
                recency=recency_score,
                confidence=confidence_score,
                relevance=relevance_score,
                importance=importance_score
            )

            ranked.append(RankedItem(
                item=item,
                memory_type=memory_type,
                token_estimate=token_estimate,
                rank_score=rank_score,
                recency_score=recency_score,
                confidence_score=confidence_score,
                relevance_score=relevance_score,
                importance_score=importance_score
            ))

        # Sort by rank score (descending)
        ranked.sort(key=lambda x: x.rank_score, reverse=True)

        return ranked

    def _score_recency(self, item: Dict[str, Any], reference_time: datetime) -> float:
        """Score item based on recency (0-1, higher is more recent)."""
        # Try different timestamp fields
        timestamp_fields = ["event_timestamp", "created_at", "updated_at", "last_used", "last_observed"]

        timestamp = None
        for field in timestamp_fields:
            if field in item and item[field]:
                timestamp = item[field]
                break

        if not timestamp:
            return 0.5  # Default if no timestamp

        # Parse timestamp
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return 0.5

        # Calculate age in days
        age = (reference_time - timestamp.replace(tzinfo=None)).total_seconds() / 86400

        # Exponential decay: score = e^(-age/decay_days)
        decay_days = 30  # Half-life of ~21 days
        score = math.exp(-age / decay_days)

        return max(0.01, min(1.0, score))

    def _score_confidence(self, item: Dict[str, Any]) -> float:
        """Score item based on confidence (0-1)."""
        confidence = item.get("confidence", 0.5)
        if isinstance(confidence, (int, float)):
            return max(0.0, min(1.0, float(confidence)))
        return 0.5

    def _score_relevance(self, item: Dict[str, Any], query: str) -> float:
        """
        Score item based on relevance to query.
        Uses simple keyword matching (for full semantic search, use embeddings).
        """
        if not query:
            return 0.5

        # Normalize query
        query_words = set(query.lower().split())

        # Get searchable text from item
        searchable = []
        for key in ["summary", "statement", "name", "description", "content"]:
            if key in item and item[key]:
                searchable.append(str(item[key]).lower())

        if not searchable:
            return 0.5

        text = " ".join(searchable)
        text_words = set(text.split())

        # Calculate overlap
        overlap = len(query_words & text_words)
        if not query_words:
            return 0.5

        # Normalize by query length
        score = overlap / len(query_words)

        # Boost for exact phrase match
        if query.lower() in text:
            score = min(1.0, score + 0.3)

        return max(0.0, min(1.0, score))

    def _score_importance(self, item: Dict[str, Any], memory_type: str) -> float:
        """Score item based on importance indicators."""
        score = 0.5

        # Check explicit importance field
        importance = item.get("importance", "normal")
        importance_map = {"critical": 1.0, "high": 0.8, "normal": 0.5, "low": 0.2}
        score = importance_map.get(importance, 0.5)

        # Boost for frequently accessed/used
        access_count = item.get("access_count", 0) or item.get("usage_count", 0) or 0
        if access_count > 10:
            score = min(1.0, score + 0.2)
        elif access_count > 5:
            score = min(1.0, score + 0.1)

        # Boost for high success rate (procedural)
        if memory_type == "procedural":
            success_rate = item.get("success_rate", 0)
            if success_rate > 0.8:
                score = min(1.0, score + 0.2)

        # Boost for verified entities
        if item.get("verified"):
            score = min(1.0, score + 0.15)

        return score

    def _combine_scores(
        self,
        strategy: RankingStrategy,
        recency: float,
        confidence: float,
        relevance: float,
        importance: float
    ) -> float:
        """Combine component scores based on strategy."""
        if strategy == RankingStrategy.RECENCY:
            return recency * 0.6 + confidence * 0.2 + relevance * 0.1 + importance * 0.1
        elif strategy == RankingStrategy.CONFIDENCE:
            return confidence * 0.6 + recency * 0.2 + relevance * 0.1 + importance * 0.1
        elif strategy == RankingStrategy.RELEVANCE:
            return relevance * 0.6 + recency * 0.15 + confidence * 0.15 + importance * 0.1
        elif strategy == RankingStrategy.IMPORTANCE:
            return importance * 0.6 + confidence * 0.2 + recency * 0.1 + relevance * 0.1
        else:  # BALANCED
            return recency * 0.25 + confidence * 0.25 + relevance * 0.25 + importance * 0.25

    # =========================================================================
    # PACKING
    # =========================================================================

    def pack_knowledge(
        self,
        allocation: BudgetAllocation,
        episodic_items: Optional[List[Dict[str, Any]]] = None,
        semantic_items: Optional[List[Dict[str, Any]]] = None,
        procedural_items: Optional[List[Dict[str, Any]]] = None,
        graph_items: Optional[List[Dict[str, Any]]] = None,
        ranking_strategy: RankingStrategy = RankingStrategy.BALANCED,
        packing_strategy: PackingStrategy = PackingStrategy.GREEDY,
        query: Optional[str] = None
    ) -> PackedContext:
        """
        Pack knowledge items within budget allocation.

        Args:
            allocation: Budget allocation to use
            episodic_items: Episodic memory items
            semantic_items: Semantic memory items
            procedural_items: Procedural memory items
            graph_items: Knowledge graph items
            ranking_strategy: How to rank items
            packing_strategy: How to pack items
            query: Optional query for relevance ranking

        Returns:
            Packed context with selected items
        """
        # Prepare items by type
        items_by_type = {
            "episodic": episodic_items or [],
            "semantic": semantic_items or [],
            "procedural": procedural_items or [],
            "graph": graph_items or []
        }

        # Rank items for each type
        ranked_by_type = {}
        for mem_type, items in items_by_type.items():
            ranked_by_type[mem_type] = self.rank_items(
                items=items,
                memory_type=mem_type,
                strategy=ranking_strategy,
                query=query
            )

        # Pack based on strategy
        if packing_strategy == PackingStrategy.GREEDY:
            selected = self._pack_greedy(allocation, ranked_by_type)
        elif packing_strategy == PackingStrategy.DIVERSE:
            selected = self._pack_diverse(allocation, ranked_by_type)
        else:
            selected = self._pack_greedy(allocation, ranked_by_type)

        # Calculate metrics
        tokens_by_type = {}
        items_count_by_type = {}
        dropped_count = 0

        for mem_type, ranked_items in ranked_by_type.items():
            selected_items = [r for r in ranked_items if r.selected]
            tokens_by_type[mem_type] = sum(r.token_estimate for r in selected_items)
            items_count_by_type[mem_type] = len(selected_items)
            dropped_count += len(ranked_items) - len(selected_items)

        total_tokens = sum(tokens_by_type.values())
        total_items = sum(items_count_by_type.values())

        # Calculate coverage
        coverage_by_type = {}
        for mem_type, alloc in allocation.allocation_by_type.items():
            if alloc > 0:
                coverage_by_type[mem_type] = tokens_by_type.get(mem_type, 0) / alloc
            else:
                coverage_by_type[mem_type] = 0.0

        return PackedContext(
            items_by_type={mt: [r.item for r in ranked_by_type[mt] if r.selected] for mt in ranked_by_type},
            tokens_by_type=tokens_by_type,
            total_tokens=total_tokens,
            total_items=total_items,
            dropped_items=dropped_count,
            coverage_by_type=coverage_by_type,
            packing_strategy=packing_strategy,
            ranking_strategy=ranking_strategy
        )

    def _pack_greedy(
        self,
        allocation: BudgetAllocation,
        ranked_by_type: Dict[str, List[RankedItem]]
    ) -> Dict[str, List[RankedItem]]:
        """
        Greedy packing: fill each type's allocation with highest-ranked items.
        """
        for mem_type, ranked_items in ranked_by_type.items():
            budget = allocation.allocation_by_type.get(mem_type, 0)
            max_single_item = int(budget * MAX_SINGLE_ITEM_RATIO)
            used = 0

            for item in ranked_items:
                # Check single item size limit
                if item.token_estimate > max_single_item and max_single_item > 0:
                    continue

                if used + item.token_estimate <= budget:
                    item.selected = True
                    used += item.token_estimate

        return ranked_by_type

    def _pack_diverse(
        self,
        allocation: BudgetAllocation,
        ranked_by_type: Dict[str, List[RankedItem]]
    ) -> Dict[str, List[RankedItem]]:
        """
        Diverse packing: round-robin across types to ensure variety.
        """
        remaining_budget = {mt: allocation.allocation_by_type.get(mt, 0) for mt in ranked_by_type}
        pointers = {mt: 0 for mt in ranked_by_type}

        # Round-robin until we can't add more
        changed = True
        while changed:
            changed = False
            for mem_type, ranked_items in ranked_by_type.items():
                ptr = pointers[mem_type]
                if ptr >= len(ranked_items):
                    continue

                item = ranked_items[ptr]
                budget = remaining_budget[mem_type]
                max_single_item = int(allocation.allocation_by_type.get(mem_type, 0) * MAX_SINGLE_ITEM_RATIO)

                if item.token_estimate <= max_single_item or max_single_item == 0:
                    if item.token_estimate <= budget:
                        item.selected = True
                        remaining_budget[mem_type] -= item.token_estimate
                        changed = True

                pointers[mem_type] = ptr + 1

        return ranked_by_type

    # =========================================================================
    # CONTEXT ASSEMBLY
    # =========================================================================

    def assemble_context(
        self,
        packed: PackedContext,
        include_metadata: bool = False,
        format_style: str = "markdown"
    ) -> ContextPayload:
        """
        Assemble packed knowledge into a formatted context string.

        Args:
            packed: Packed context result
            include_metadata: Whether to include item metadata
            format_style: Output format ("markdown", "xml", "plain")

        Returns:
            Context payload ready for injection
        """
        sections = {}

        # Format each section
        if packed.items_by_type.get("procedural"):
            sections["procedural"] = self._format_section(
                items=packed.items_by_type["procedural"],
                title="Preferences & Workflows",
                memory_type="procedural",
                include_metadata=include_metadata,
                format_style=format_style
            )

        if packed.items_by_type.get("semantic"):
            sections["semantic"] = self._format_section(
                items=packed.items_by_type["semantic"],
                title="Known Facts & Patterns",
                memory_type="semantic",
                include_metadata=include_metadata,
                format_style=format_style
            )

        if packed.items_by_type.get("episodic"):
            sections["episodic"] = self._format_section(
                items=packed.items_by_type["episodic"],
                title="Recent Events",
                memory_type="episodic",
                include_metadata=include_metadata,
                format_style=format_style
            )

        if packed.items_by_type.get("graph"):
            sections["graph"] = self._format_section(
                items=packed.items_by_type["graph"],
                title="Relationships",
                memory_type="graph",
                include_metadata=include_metadata,
                format_style=format_style
            )

        # Combine sections
        if format_style == "markdown":
            separator = "\n\n---\n\n"
        elif format_style == "xml":
            separator = "\n"
        else:
            separator = "\n\n"

        formatted_context = separator.join(sections.values())

        return ContextPayload(
            formatted_context=formatted_context,
            total_tokens=packed.total_tokens,
            sections=sections,
            metadata={
                "total_items": packed.total_items,
                "dropped_items": packed.dropped_items,
                "coverage_by_type": packed.coverage_by_type,
                "packing_strategy": packed.packing_strategy.value,
                "ranking_strategy": packed.ranking_strategy.value
            }
        )

    def _format_section(
        self,
        items: List[Dict[str, Any]],
        title: str,
        memory_type: str,
        include_metadata: bool,
        format_style: str
    ) -> str:
        """Format a section of knowledge items."""
        if not items:
            return ""

        if format_style == "markdown":
            return self._format_markdown(items, title, memory_type, include_metadata)
        elif format_style == "xml":
            return self._format_xml(items, title, memory_type, include_metadata)
        else:
            return self._format_plain(items, title, memory_type, include_metadata)

    def _format_markdown(
        self,
        items: List[Dict[str, Any]],
        title: str,
        memory_type: str,
        include_metadata: bool
    ) -> str:
        """Format items as markdown."""
        lines = [f"## {title}"]

        for item in items:
            # Format based on memory type
            if memory_type == "procedural":
                name = item.get("name", "Unknown")
                desc = item.get("description", "")
                lines.append(f"- **{name}**: {desc}")
            elif memory_type == "semantic":
                statement = item.get("statement", "")
                confidence = item.get("confidence", 0)
                lines.append(f"- {statement} (confidence: {confidence:.0%})")
            elif memory_type == "episodic":
                summary = item.get("summary", "")
                timestamp = item.get("event_timestamp", "")
                lines.append(f"- [{timestamp[:10]}] {summary}")
            elif memory_type == "graph":
                source = item.get("source_name", item.get("name", ""))
                rel = item.get("relationship", "")
                target = item.get("target_name", "")
                if rel and target:
                    lines.append(f"- {source} **{rel}** {target}")
                else:
                    lines.append(f"- {source}")

            if include_metadata:
                meta_parts = []
                for key in ["confidence", "importance", "source"]:
                    if key in item:
                        meta_parts.append(f"{key}={item[key]}")
                if meta_parts:
                    lines.append(f"  _({', '.join(meta_parts)})_")

        return "\n".join(lines)

    def _format_xml(
        self,
        items: List[Dict[str, Any]],
        title: str,
        memory_type: str,
        include_metadata: bool
    ) -> str:
        """Format items as XML."""
        lines = [f"<{memory_type}>"]

        for i, item in enumerate(items):
            lines.append(f"  <item id=\"{i}\">")

            if memory_type == "procedural":
                lines.append(f"    <name>{item.get('name', '')}</name>")
                lines.append(f"    <description>{item.get('description', '')}</description>")
            elif memory_type == "semantic":
                lines.append(f"    <statement>{item.get('statement', '')}</statement>")
            elif memory_type == "episodic":
                lines.append(f"    <summary>{item.get('summary', '')}</summary>")
                lines.append(f"    <timestamp>{item.get('event_timestamp', '')}</timestamp>")
            elif memory_type == "graph":
                lines.append(f"    <source>{item.get('source_name', item.get('name', ''))}</source>")
                lines.append(f"    <relationship>{item.get('relationship', '')}</relationship>")
                lines.append(f"    <target>{item.get('target_name', '')}</target>")

            if include_metadata:
                lines.append(f"    <confidence>{item.get('confidence', 0.5)}</confidence>")

            lines.append("  </item>")

        lines.append(f"</{memory_type}>")
        return "\n".join(lines)

    def _format_plain(
        self,
        items: List[Dict[str, Any]],
        title: str,
        memory_type: str,
        include_metadata: bool
    ) -> str:
        """Format items as plain text."""
        lines = [f"=== {title} ==="]

        for item in items:
            if memory_type == "procedural":
                lines.append(f"  {item.get('name', '')}: {item.get('description', '')}")
            elif memory_type == "semantic":
                lines.append(f"  {item.get('statement', '')}")
            elif memory_type == "episodic":
                lines.append(f"  [{item.get('event_timestamp', '')[:10]}] {item.get('summary', '')}")
            elif memory_type == "graph":
                source = item.get("source_name", item.get("name", ""))
                rel = item.get("relationship", "")
                target = item.get("target_name", "")
                if rel and target:
                    lines.append(f"  {source} -> {rel} -> {target}")
                else:
                    lines.append(f"  {source}")

        return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def estimate_tokens(content: Any) -> int:
    """Quick token estimation for content."""
    estimator = TokenEstimator()
    return estimator.estimate(content).total_tokens


def get_model_context_limit(model_id: str) -> int:
    """Get context limit for a model."""
    return MODEL_CONTEXT_LIMITS.get(model_id, MODEL_CONTEXT_LIMITS["default"])


def create_context_manager(model_id: str = "default") -> ContextBudgetManager:
    """Create a context budget manager for a model."""
    return ContextBudgetManager(model_id=model_id)


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Arcus Context Budget Manager - Test Run")
    print("=" * 50)

    # Create manager
    manager = ContextBudgetManager(model_id="claude-sonnet")

    # Test budget allocation
    print("\n1. Budget Allocation Test:")
    allocation = manager.allocate_budget(
        base_prompt_tokens=5000,
        expected_response_tokens=4000,
        task_context="code_review"
    )
    print(f"   Total available: {allocation.total_available:,}")
    print(f"   Available for context: {allocation.available_for_context:,}")
    print(f"   Allocation by type: {allocation.allocation_by_type}")

    # Test token estimation
    print("\n2. Token Estimation Test:")
    test_content = {
        "name": "Response Style Preference",
        "description": "User prefers concise, technical responses without emoji",
        "confidence": 0.95
    }
    estimate = manager.estimator.estimate(test_content)
    print(f"   Content tokens: {estimate.content_tokens}")
    print(f"   Total tokens: {estimate.total_tokens}")

    # Test ranking
    print("\n3. Ranking Test:")
    test_items = [
        {"statement": "User prefers TypeScript", "confidence": 0.95, "created_at": "2026-01-25T10:00:00"},
        {"statement": "User likes Python", "confidence": 0.7, "created_at": "2026-01-20T10:00:00"},
        {"statement": "User knows JavaScript", "confidence": 0.8, "created_at": "2026-01-22T10:00:00"},
    ]
    ranked = manager.rank_items(test_items, "semantic", query="TypeScript preferences")
    for i, item in enumerate(ranked[:3]):
        print(f"   {i+1}. Score: {item.rank_score:.2f} - {item.item['statement']}")

    # Test packing
    print("\n4. Packing Test:")
    packed = manager.pack_knowledge(
        allocation=allocation,
        semantic_items=test_items,
        procedural_items=[test_content],
        query="programming preferences"
    )
    print(f"   Total tokens used: {packed.total_tokens}")
    print(f"   Items selected: {packed.total_items}")
    print(f"   Items dropped: {packed.dropped_items}")

    # Test context assembly
    print("\n5. Context Assembly Test:")
    payload = manager.assemble_context(packed, format_style="markdown")
    print(f"   Context length: {len(payload.formatted_context)} chars")
    print(f"   Sections: {list(payload.sections.keys())}")

    print("\nTest complete!")
