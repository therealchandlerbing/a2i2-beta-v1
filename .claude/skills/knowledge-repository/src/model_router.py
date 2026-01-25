"""
Arcus Model Router - Intelligent Model Selection

This module provides model routing based on:
1. Task requirements (context, complexity)
2. User preference vectors
3. Historical performance patterns
4. Cost/latency constraints

Inspired by NVIDIA's ToolOrchestra orchestration paradigm.

Usage:
    from model_router import ModelRouter

    router = ModelRouter()

    # Get best model for a task
    decision = router.route(
        task="Analyze this financial document",
        context="document_analysis",
        preference_context="cost_sensitive"
    )

    # Record the outcome
    router.record_outcome(
        decision=decision,
        success=True,
        actual_cost=0.003,
        actual_latency=1200
    )
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum

from knowledge_operations import (
    KnowledgeRepository,
    UserPreferenceVectorEntry,
    PatternOutcome,
    TaskComplexity,
    ToolInvocation,
    SourceType,
    KnowledgeSource
)


# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for a model."""
    id: str
    name: str
    provider: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_latency_ms: int
    max_context: int
    capabilities: List[str]
    thinking_levels: List[str]
    best_for: List[str]


# Model registry - matches gemini-config.json
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "claude-opus": ModelConfig(
        id="claude-opus",
        name="Claude Opus",
        provider="anthropic",
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        avg_latency_ms=2000,
        max_context=200000,
        capabilities=["reasoning", "coding", "analysis", "creative", "empathy"],
        thinking_levels=[],
        best_for=["complex_reasoning", "nuanced_conversation"]
    ),
    "claude-sonnet": ModelConfig(
        id="claude-sonnet",
        name="Claude Sonnet",
        provider="anthropic",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        avg_latency_ms=800,
        max_context=200000,
        capabilities=["reasoning", "coding", "analysis", "creative"],
        thinking_levels=[],
        best_for=["balanced", "general_tasks"]
    ),
    "claude-haiku": ModelConfig(
        id="claude-haiku",
        name="Claude Haiku",
        provider="anthropic",
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        avg_latency_ms=200,
        max_context=200000,
        capabilities=["classification", "extraction", "simple_qa"],
        thinking_levels=[],
        best_for=["fast_responses", "simple_tasks", "high_volume"]
    ),
    "gemini-3-pro": ModelConfig(
        id="gemini-3-pro-preview",
        name="Gemini 3 Pro",
        provider="google",
        cost_per_1k_input=0.002,
        cost_per_1k_output=0.012,
        avg_latency_ms=3000,
        max_context=1048576,
        capabilities=["reasoning", "coding", "analysis", "vision", "code_execution", "search_grounding"],
        thinking_levels=["low", "high"],
        best_for=["complex_reasoning", "large_context", "agentic"]
    ),
    "gemini-3-flash": ModelConfig(
        id="gemini-3-flash-preview",
        name="Gemini 3 Flash",
        provider="google",
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.003,
        avg_latency_ms=500,
        max_context=1048576,
        capabilities=["reasoning", "coding", "analysis", "vision", "code_execution", "search_grounding"],
        thinking_levels=["minimal", "low", "medium", "high"],
        best_for=["balanced", "high_volume", "general_analysis"]
    ),
    "gemini-2.5-flash": ModelConfig(
        id="gemini-2.5-flash",
        name="Gemini 2.5 Flash",
        provider="google",
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        avg_latency_ms=300,
        max_context=1048576,
        capabilities=["reasoning", "coding", "analysis", "vision"],
        thinking_levels=["budget"],
        best_for=["cost_efficient", "high_volume"]
    ),
    "personaplex": ModelConfig(
        id="personaplex",
        name="NVIDIA PersonaPlex",
        provider="nvidia",
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.001,
        avg_latency_ms=170,
        max_context=32000,
        capabilities=["voice", "full_duplex", "personas"],
        thinking_levels=[],
        best_for=["voice", "real_time_conversation"]
    ),
    "deep-research": ModelConfig(
        id="deep-research-pro-preview-12-2025",
        name="Gemini Deep Research",
        provider="google",
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.05,
        avg_latency_ms=60000,
        max_context=1048576,
        capabilities=["research", "web_search", "file_search", "synthesis"],
        thinking_levels=[],
        best_for=["comprehensive_research", "due_diligence"]
    ),
}


# =============================================================================
# ROUTING DECISION
# =============================================================================

@dataclass
class RoutingDecision:
    """Result of model routing decision."""
    model_id: str
    model_config: ModelConfig
    thinking_level: Optional[str]
    estimated_cost: float
    estimated_latency_ms: int
    confidence: float
    reasoning: str
    matched_pattern_id: Optional[str] = None
    fallback_model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_name": self.model_config.name,
            "thinking_level": self.thinking_level,
            "estimated_cost": self.estimated_cost,
            "estimated_latency_ms": self.estimated_latency_ms,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "matched_pattern_id": self.matched_pattern_id,
            "fallback_model": self.fallback_model
        }


# =============================================================================
# MODEL ROUTER
# =============================================================================

class ModelRouter:
    """
    Intelligent model router that selects optimal models based on:
    - Task requirements
    - User preferences
    - Historical patterns
    - Cost/latency constraints
    """

    def __init__(
        self,
        repository: Optional[KnowledgeRepository] = None,
        models: Optional[Dict[str, ModelConfig]] = None
    ):
        """
        Initialize the model router.

        Args:
            repository: Knowledge repository for patterns and preferences
            models: Custom model registry (defaults to MODEL_REGISTRY)
        """
        self.repository = repository or KnowledgeRepository()
        self.models = models or MODEL_REGISTRY

    def route(
        self,
        task: str,
        context: Optional[str] = None,
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        preference_context: str = "default",
        user_id: str = "default",
        required_capabilities: Optional[List[str]] = None,
        max_cost_usd: Optional[float] = None,
        max_latency_ms: Optional[int] = None,
        exclude_models: Optional[List[str]] = None
    ) -> RoutingDecision:
        """
        Route to the best model for a task.

        Args:
            task: Task description
            context: Task context (e.g., "code_review", "voice_response")
            complexity: Task complexity level
            preference_context: User preference context name
            user_id: User ID
            required_capabilities: Capabilities the model must have
            max_cost_usd: Maximum cost constraint
            max_latency_ms: Maximum latency constraint
            exclude_models: Models to exclude

        Returns:
            Routing decision with selected model
        """
        # Get user preferences
        prefs = self.repository.get_user_preference_vector(
            context_name=preference_context,
            user_id=user_id
        )

        # Check for historical pattern
        pattern = None
        if context:
            pattern = self.repository.get_best_pattern(context)

        # Filter eligible models
        candidates = self._filter_candidates(
            required_capabilities=required_capabilities,
            max_cost_usd=max_cost_usd,
            max_latency_ms=max_latency_ms,
            exclude_models=exclude_models
        )

        if not candidates:
            # Fallback to default
            return self._create_fallback_decision("No eligible models found")

        # Score candidates
        scored = self._score_candidates(
            candidates=candidates,
            task=task,
            context=context,
            complexity=complexity,
            prefs=prefs,
            pattern=pattern
        )

        # Select best
        best = max(scored, key=lambda x: x[1])
        model_id, score, reasoning = best

        # Determine thinking level
        thinking_level = self._select_thinking_level(
            model=self.models[model_id],
            complexity=complexity,
            prefs=prefs
        )

        # Estimate cost (rough estimate based on average tokens)
        estimated_tokens = self._estimate_tokens(task, complexity)
        model_config = self.models[model_id]
        estimated_cost = (
            (estimated_tokens / 1000) * model_config.cost_per_1k_input +
            (estimated_tokens / 1000) * model_config.cost_per_1k_output
        )

        # Find fallback
        fallback = None
        if len(scored) > 1:
            second_best = sorted(scored, key=lambda x: x[1], reverse=True)[1]
            fallback = second_best[0]

        return RoutingDecision(
            model_id=model_id,
            model_config=model_config,
            thinking_level=thinking_level,
            estimated_cost=estimated_cost,
            estimated_latency_ms=model_config.avg_latency_ms,
            confidence=min(0.95, 0.5 + score * 0.5),
            reasoning=reasoning,
            matched_pattern_id=pattern.get("id") if pattern else None,
            fallback_model=fallback
        )

    def _filter_candidates(
        self,
        required_capabilities: Optional[List[str]],
        max_cost_usd: Optional[float],
        max_latency_ms: Optional[int],
        exclude_models: Optional[List[str]]
    ) -> List[str]:
        """Filter models based on constraints."""
        candidates = []

        for model_id, config in self.models.items():
            # Check exclusion
            if exclude_models and model_id in exclude_models:
                continue

            # Check capabilities
            if required_capabilities:
                if not all(cap in config.capabilities for cap in required_capabilities):
                    continue

            # Check cost (rough estimate)
            if max_cost_usd:
                # Estimate 1000 tokens
                est_cost = (config.cost_per_1k_input + config.cost_per_1k_output) * 1
                if est_cost > max_cost_usd:
                    continue

            # Check latency
            if max_latency_ms and config.avg_latency_ms > max_latency_ms:
                continue

            candidates.append(model_id)

        return candidates

    def _score_candidates(
        self,
        candidates: List[str],
        task: str,
        context: Optional[str],
        complexity: TaskComplexity,
        prefs: UserPreferenceVectorEntry,
        pattern: Optional[Dict[str, Any]]
    ) -> List[tuple]:
        """Score candidates based on preferences and patterns."""
        scored = []

        for model_id in candidates:
            config = self.models[model_id]
            score = 0.0
            reasons = []

            # Base preference score
            pref_score = prefs.get_model_preference(model_id)
            score += pref_score * 0.3
            if pref_score > 0.7:
                reasons.append(f"high preference ({pref_score:.1f})")

            # Pattern match bonus
            if pattern and pattern.get("model_used") == model_id:
                pattern_bonus = pattern.get("success_rate", 0.5) * 0.3
                score += pattern_bonus
                reasons.append(f"historical pattern (success: {pattern.get('success_rate', 0):.0%})")

            # Capability match for context
            if context:
                context_capabilities = self._get_context_capabilities(context)
                matches = sum(1 for cap in context_capabilities if cap in config.capabilities)
                cap_score = matches / max(len(context_capabilities), 1) * 0.2
                score += cap_score
                if cap_score > 0.1:
                    reasons.append(f"capability match")

            # Cost/latency score based on preferences
            max_cost = 0.1
            max_latency = 30000
            cost_score = (1.0 - min(config.cost_per_1k_input / 0.01, 1.0)) * prefs.cost_weight
            latency_score = (1.0 - min(config.avg_latency_ms / max_latency, 1.0)) * prefs.latency_weight
            score += cost_score + latency_score

            # Complexity match
            if complexity == TaskComplexity.HIGH and config.max_context > 500000:
                score += 0.1
                reasons.append("large context support")
            elif complexity == TaskComplexity.LOW and config.avg_latency_ms < 500:
                score += 0.1
                reasons.append("fast for simple tasks")

            reasoning = "; ".join(reasons) if reasons else "default selection"
            scored.append((model_id, score, reasoning))

        return scored

    def _get_context_capabilities(self, context: str) -> List[str]:
        """Get required capabilities for a context."""
        context_map = {
            "code_review": ["coding", "analysis"],
            "document_analysis": ["analysis", "reasoning"],
            "voice_response": ["voice"],
            "research": ["research", "web_search"],
            "image_generation": ["image_generation"],
            "real_time": ["voice", "full_duplex"],
        }
        return context_map.get(context, ["reasoning"])

    def _select_thinking_level(
        self,
        model: ModelConfig,
        complexity: TaskComplexity,
        prefs: UserPreferenceVectorEntry
    ) -> Optional[str]:
        """Select appropriate thinking level."""
        if not model.thinking_levels:
            return None

        # Map complexity to thinking level
        if complexity == TaskComplexity.LOW:
            preferred = "minimal" if "minimal" in model.thinking_levels else "low"
        elif complexity == TaskComplexity.HIGH:
            preferred = "high"
        else:
            preferred = "medium" if "medium" in model.thinking_levels else "low"

        # Adjust based on latency preference
        if prefs.latency_weight > 0.4 and "minimal" in model.thinking_levels:
            preferred = "minimal"

        # Ensure it's available
        if preferred in model.thinking_levels:
            return preferred

        return model.thinking_levels[0] if model.thinking_levels else None

    def _estimate_tokens(self, task: str, complexity: TaskComplexity) -> int:
        """Estimate token usage for a task."""
        base = len(task.split()) * 1.5  # Rough estimate

        multipliers = {
            TaskComplexity.LOW: 1.0,
            TaskComplexity.MEDIUM: 2.0,
            TaskComplexity.HIGH: 4.0
        }

        return int(base * multipliers.get(complexity, 2.0) + 500)  # Add base overhead

    def _create_fallback_decision(self, reason: str) -> RoutingDecision:
        """Create fallback decision when no candidates available."""
        fallback_model = "gemini-3-flash"
        config = self.models[fallback_model]

        return RoutingDecision(
            model_id=fallback_model,
            model_config=config,
            thinking_level="medium",
            estimated_cost=0.001,
            estimated_latency_ms=config.avg_latency_ms,
            confidence=0.3,
            reasoning=f"Fallback: {reason}"
        )

    def record_outcome(
        self,
        decision: RoutingDecision,
        success: bool,
        actual_cost: Optional[float] = None,
        actual_latency: Optional[int] = None,
        accuracy_score: Optional[float] = None,
        tools_used: Optional[List[ToolInvocation]] = None,
        context: Optional[str] = None
    ) -> None:
        """
        Record the outcome of a routing decision.

        Args:
            decision: The routing decision that was made
            success: Whether the task succeeded
            actual_cost: Actual cost in USD
            actual_latency: Actual latency in ms
            accuracy_score: How accurate was the result (0-1)
            tools_used: Tools that were invoked
            context: Task context
        """
        outcome = PatternOutcome.SUCCESS if success else PatternOutcome.FAILURE

        self.repository.learn_model_pattern(
            task_context=context or "unknown",
            model_used=decision.model_id,
            outcome=outcome,
            tools_sequence=tools_used,
            accuracy_score=accuracy_score,
            total_cost_usd=actual_cost,
            total_latency_ms=actual_latency,
            complexity=TaskComplexity.MEDIUM,  # Could be passed in
            preference_context=None
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_router() -> ModelRouter:
    """Get a router instance."""
    return ModelRouter()


def quick_route(task: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick routing for common use cases.

    Args:
        task: Task description
        context: Optional context

    Returns:
        Routing decision as dict
    """
    router = get_router()
    decision = router.route(task=task, context=context)
    return decision.to_dict()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Arcus Model Router - Test Run")
    print("=" * 50)

    router = ModelRouter()

    # Test basic routing
    print("\n1. Basic routing test:")
    decision = router.route(
        task="Review this Python code for security issues",
        context="code_review",
        complexity=TaskComplexity.MEDIUM
    )
    print(f"   Model: {decision.model_id}")
    print(f"   Thinking: {decision.thinking_level}")
    print(f"   Est. Cost: ${decision.estimated_cost:.4f}")
    print(f"   Reasoning: {decision.reasoning}")

    # Test with cost constraint
    print("\n2. Cost-constrained routing:")
    decision = router.route(
        task="Summarize this document",
        context="document_analysis",
        max_cost_usd=0.001
    )
    print(f"   Model: {decision.model_id}")
    print(f"   Est. Cost: ${decision.estimated_cost:.4f}")

    # Test voice routing
    print("\n3. Voice routing:")
    decision = router.route(
        task="Respond to voice query",
        context="voice_response",
        required_capabilities=["voice"],
        max_latency_ms=500
    )
    print(f"   Model: {decision.model_id}")
    print(f"   Latency: {decision.estimated_latency_ms}ms")

    print("\nTest complete!")
