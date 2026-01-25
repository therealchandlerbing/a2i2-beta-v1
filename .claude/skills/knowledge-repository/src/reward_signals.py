"""
Arcus Reward Signals - Normalized Reward Computation for Skill Optimization

This module provides a reward system for skill trajectories that can be used for:
1. Evaluating skill execution quality
2. Comparing different skill/model combinations
3. Future reinforcement learning optimization
4. Preference-weighted outcome scoring

Implements the "Normalized Reward Signals" enhancement from Phase 3.

Usage:
    from reward_signals import RewardCalculator, SkillTrajectory

    calculator = RewardCalculator()

    # Compute reward for a skill execution trajectory
    reward = calculator.compute_reward(
        trajectory=trajectory,
        outcome=outcome,
        user_preferences=preferences
    )

    # Get reward breakdown
    breakdown = calculator.get_reward_breakdown(trajectory, outcome, preferences)
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import deque


# =============================================================================
# CONSTANTS
# =============================================================================

# Normalization bounds (for batch normalization)
MAX_COST_USD_DEFAULT = 0.10       # Maximum expected cost per trajectory
MAX_LATENCY_MS_DEFAULT = 30000   # Maximum expected latency (30 seconds)
MAX_TOKENS_DEFAULT = 100000      # Maximum expected tokens

# Reward component weights (default)
DEFAULT_ACCURACY_WEIGHT = 0.5
DEFAULT_COST_WEIGHT = 0.3
DEFAULT_LATENCY_WEIGHT = 0.2

# Bonus/penalty factors
TOOL_PREFERENCE_BONUS = 0.1      # Bonus for using preferred tools
CORRECTION_PENALTY = 0.15        # Penalty for requiring correction
FAILURE_PENALTY = 0.5            # Penalty multiplier for failures
EFFICIENCY_BONUS = 0.1           # Bonus for under-budget execution

# Moving average window for normalization
NORMALIZATION_WINDOW = 100


# =============================================================================
# ENUMS
# =============================================================================

class OutcomeType(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class RewardSignalType(Enum):
    ACCURACY = "accuracy"
    COST = "cost"
    LATENCY = "latency"
    PREFERENCE = "preference"
    EFFICIENCY = "efficiency"
    TRUST = "trust"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SkillExecution:
    """A single skill execution within a trajectory."""
    skill_name: str
    capability: str
    model_used: str
    tokens_input: int = 0
    tokens_output: int = 0
    tokens_thinking: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    context_tokens: int = 0
    thinking_level: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output + self.tokens_thinking


@dataclass
class SkillTrajectory:
    """A sequence of skill executions for a task."""
    trajectory_id: str
    task_description: str
    task_context: Optional[str] = None
    executions: List[SkillExecution] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    user_id: str = "default"
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_cost(self) -> float:
        return sum(e.cost_usd for e in self.executions)

    @property
    def total_latency(self) -> int:
        return sum(e.latency_ms for e in self.executions)

    @property
    def total_tokens(self) -> int:
        return sum(e.total_tokens for e in self.executions)

    @property
    def skills_used(self) -> List[str]:
        return [e.skill_name for e in self.executions]

    @property
    def models_used(self) -> List[str]:
        return list(set(e.model_used for e in self.executions))

    @property
    def success_rate(self) -> float:
        if not self.executions:
            return 0.0
        return sum(1 for e in self.executions if e.success) / len(self.executions)


@dataclass
class Outcome:
    """The outcome of a skill trajectory."""
    outcome_type: OutcomeType
    accuracy: float = 1.0  # 0-1, how accurate/complete was the result
    user_satisfaction: Optional[float] = None  # 0-1, if feedback provided
    required_correction: bool = False
    correction_severity: float = 0.0  # 0-1, how significant was the correction
    error_message: Optional[str] = None
    output_quality: float = 1.0  # 0-1, quality of the output
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.outcome_type in (OutcomeType.SUCCESS, OutcomeType.PARTIAL)


@dataclass
class UserPreferenceVector:
    """User preferences for reward weighting."""
    user_id: str = "default"
    context_name: str = "default"

    # Objective weights (should sum to 1.0)
    accuracy_weight: float = DEFAULT_ACCURACY_WEIGHT
    cost_weight: float = DEFAULT_COST_WEIGHT
    latency_weight: float = DEFAULT_LATENCY_WEIGHT

    # Tool/model preferences (0.0 = avoid, 1.0 = prefer)
    model_preferences: Dict[str, float] = field(default_factory=dict)
    skill_preferences: Dict[str, float] = field(default_factory=dict)

    # Context-specific overrides
    overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class RewardBreakdown:
    """Detailed breakdown of reward components."""
    total_reward: float
    accuracy_component: float
    cost_component: float
    latency_component: float
    preference_bonus: float
    efficiency_bonus: float
    correction_penalty: float
    raw_scores: Dict[str, float] = field(default_factory=dict)
    normalized_scores: Dict[str, float] = field(default_factory=dict)
    weights_applied: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_reward": self.total_reward,
            "components": {
                "accuracy": self.accuracy_component,
                "cost": self.cost_component,
                "latency": self.latency_component,
                "preference_bonus": self.preference_bonus,
                "efficiency_bonus": self.efficiency_bonus,
                "correction_penalty": self.correction_penalty
            },
            "raw_scores": self.raw_scores,
            "normalized_scores": self.normalized_scores,
            "weights_applied": self.weights_applied
        }


@dataclass
class RewardSignal:
    """A reward signal to be stored and used for learning."""
    signal_id: str
    trajectory_id: str
    reward: float
    breakdown: RewardBreakdown
    user_id: str
    context: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# NORMALIZATION TRACKER
# =============================================================================

class RunningNormalizer:
    """
    Tracks running statistics for normalization.

    Uses exponential moving average for online normalization
    of cost and latency values based on recent history.
    """

    def __init__(self, window_size: int = NORMALIZATION_WINDOW):
        self.window_size = window_size
        self._cost_history: deque = deque(maxlen=window_size)
        self._latency_history: deque = deque(maxlen=window_size)
        self._tokens_history: deque = deque(maxlen=window_size)

        # Fallback bounds
        self._max_cost = MAX_COST_USD_DEFAULT
        self._max_latency = MAX_LATENCY_MS_DEFAULT
        self._max_tokens = MAX_TOKENS_DEFAULT

    def update(self, cost: float, latency: int, tokens: int) -> None:
        """Update running statistics with new observation."""
        self._cost_history.append(cost)
        self._latency_history.append(latency)
        self._tokens_history.append(tokens)

        # Update max values if we have enough data
        if len(self._cost_history) >= 10:
            self._max_cost = max(self._cost_history) * 1.2  # 20% buffer
            self._max_latency = max(self._latency_history) * 1.2
            self._max_tokens = max(self._tokens_history) * 1.2

    @property
    def max_cost(self) -> float:
        return max(self._max_cost, 0.001)  # Prevent division by zero

    @property
    def max_latency(self) -> int:
        return max(int(self._max_latency), 100)

    @property
    def max_tokens(self) -> int:
        return max(int(self._max_tokens), 1000)

    def normalize_cost(self, cost: float) -> float:
        """Normalize cost to 0-1 range (lower is better)."""
        return min(1.0, cost / self.max_cost)

    def normalize_latency(self, latency: int) -> float:
        """Normalize latency to 0-1 range (lower is better)."""
        return min(1.0, latency / self.max_latency)

    def get_stats(self) -> Dict[str, Any]:
        """Get current normalization statistics."""
        return {
            "window_size": self.window_size,
            "samples": len(self._cost_history),
            "max_cost": self.max_cost,
            "max_latency": self.max_latency,
            "max_tokens": self.max_tokens,
            "avg_cost": sum(self._cost_history) / len(self._cost_history) if self._cost_history else 0,
            "avg_latency": sum(self._latency_history) / len(self._latency_history) if self._latency_history else 0
        }


# =============================================================================
# REWARD CALCULATOR
# =============================================================================

class RewardCalculator:
    """
    Computes normalized rewards for skill execution trajectories.

    The reward function balances:
    1. Accuracy/Quality - How well did the task complete?
    2. Cost efficiency - How much did it cost (tokens, API calls)?
    3. Latency - How long did it take?
    4. User preferences - Did it use preferred tools/models?
    5. Corrections - Did it require user correction?

    Formula:
        reward = (
            accuracy_score * accuracy_weight +
            (1 - normalized_cost) * cost_weight +
            (1 - normalized_latency) * latency_weight +
            preference_bonus -
            correction_penalty
        ) * outcome_multiplier
    """

    def __init__(
        self,
        normalizer: Optional[RunningNormalizer] = None,
        default_preferences: Optional[UserPreferenceVector] = None
    ):
        """
        Initialize the reward calculator.

        Args:
            normalizer: Running normalizer for cost/latency
            default_preferences: Default user preferences
        """
        self.normalizer = normalizer or RunningNormalizer()
        self.default_preferences = default_preferences or UserPreferenceVector()
        self._reward_history: List[RewardSignal] = []

    def compute_reward(
        self,
        trajectory: SkillTrajectory,
        outcome: Outcome,
        user_preferences: Optional[UserPreferenceVector] = None
    ) -> float:
        """
        Compute the total reward for a trajectory.

        Args:
            trajectory: The skill execution trajectory
            outcome: The outcome of the trajectory
            user_preferences: User preference vector (uses default if None)

        Returns:
            Normalized reward value (typically 0-1, can exceed with bonuses)
        """
        breakdown = self.get_reward_breakdown(trajectory, outcome, user_preferences)
        return breakdown.total_reward

    def get_reward_breakdown(
        self,
        trajectory: SkillTrajectory,
        outcome: Outcome,
        user_preferences: Optional[UserPreferenceVector] = None
    ) -> RewardBreakdown:
        """
        Get detailed breakdown of reward components.

        Args:
            trajectory: The skill execution trajectory
            outcome: The outcome of the trajectory
            user_preferences: User preference vector

        Returns:
            Detailed reward breakdown
        """
        prefs = user_preferences or self.default_preferences

        # Update normalizer with this trajectory
        self.normalizer.update(
            cost=trajectory.total_cost,
            latency=trajectory.total_latency,
            tokens=trajectory.total_tokens
        )

        # Calculate raw scores
        raw_scores = {
            "accuracy": outcome.accuracy,
            "output_quality": outcome.output_quality,
            "cost": trajectory.total_cost,
            "latency": trajectory.total_latency,
            "skill_success_rate": trajectory.success_rate
        }

        # Normalize cost and latency (inverted: lower is better)
        normalized_cost = self.normalizer.normalize_cost(trajectory.total_cost)
        normalized_latency = self.normalizer.normalize_latency(trajectory.total_latency)

        normalized_scores = {
            "accuracy": outcome.accuracy,
            "cost": 1.0 - normalized_cost,  # Invert: lower cost = higher score
            "latency": 1.0 - normalized_latency,  # Invert: lower latency = higher score
            "quality": outcome.output_quality
        }

        # Calculate base components
        accuracy_component = outcome.accuracy * outcome.output_quality
        cost_component = 1.0 - normalized_cost
        latency_component = 1.0 - normalized_latency

        # Calculate preference bonus
        preference_bonus = self._calculate_preference_bonus(trajectory, prefs)

        # Calculate efficiency bonus (if under budget)
        efficiency_bonus = self._calculate_efficiency_bonus(trajectory, outcome)

        # Calculate correction penalty
        correction_penalty = 0.0
        if outcome.required_correction:
            correction_penalty = CORRECTION_PENALTY * (1 + outcome.correction_severity)

        # Apply weights
        weights = {
            "accuracy": prefs.accuracy_weight,
            "cost": prefs.cost_weight,
            "latency": prefs.latency_weight
        }

        weighted_sum = (
            accuracy_component * prefs.accuracy_weight +
            cost_component * prefs.cost_weight +
            latency_component * prefs.latency_weight
        )

        # Add bonuses, subtract penalties
        total_before_multiplier = (
            weighted_sum +
            preference_bonus +
            efficiency_bonus -
            correction_penalty
        )

        # Apply outcome multiplier
        outcome_multiplier = self._get_outcome_multiplier(outcome)
        total_reward = total_before_multiplier * outcome_multiplier

        # Clamp to reasonable range
        total_reward = max(0.0, min(1.5, total_reward))

        return RewardBreakdown(
            total_reward=total_reward,
            accuracy_component=accuracy_component * prefs.accuracy_weight,
            cost_component=cost_component * prefs.cost_weight,
            latency_component=latency_component * prefs.latency_weight,
            preference_bonus=preference_bonus,
            efficiency_bonus=efficiency_bonus,
            correction_penalty=correction_penalty,
            raw_scores=raw_scores,
            normalized_scores=normalized_scores,
            weights_applied=weights
        )

    def _calculate_preference_bonus(
        self,
        trajectory: SkillTrajectory,
        preferences: UserPreferenceVector
    ) -> float:
        """Calculate bonus for using preferred skills/models."""
        bonus = 0.0

        for execution in trajectory.executions:
            # Model preference bonus
            model_pref = preferences.model_preferences.get(execution.model_used, 0.5)
            if model_pref > 0.7:  # Preferred model
                bonus += TOOL_PREFERENCE_BONUS * (model_pref - 0.5)

            # Skill preference bonus
            skill_pref = preferences.skill_preferences.get(execution.skill_name, 0.5)
            if skill_pref > 0.7:  # Preferred skill
                bonus += TOOL_PREFERENCE_BONUS * (skill_pref - 0.5)

        # Normalize by number of executions
        if trajectory.executions:
            bonus /= len(trajectory.executions)

        return min(bonus, TOOL_PREFERENCE_BONUS * 2)  # Cap the bonus

    def _calculate_efficiency_bonus(
        self,
        trajectory: SkillTrajectory,
        outcome: Outcome
    ) -> float:
        """Calculate bonus for efficient execution."""
        if not outcome.success:
            return 0.0

        bonus = 0.0

        # Bonus for using fewer tokens than expected
        expected_tokens = 10000 * len(trajectory.executions)  # Rough estimate
        if trajectory.total_tokens < expected_tokens * 0.5:
            bonus += EFFICIENCY_BONUS * 0.5

        # Bonus for fast execution
        expected_latency = 2000 * len(trajectory.executions)  # 2s per skill
        if trajectory.total_latency < expected_latency * 0.5:
            bonus += EFFICIENCY_BONUS * 0.5

        return bonus

    def _get_outcome_multiplier(self, outcome: Outcome) -> float:
        """Get multiplier based on outcome type."""
        multipliers = {
            OutcomeType.SUCCESS: 1.0,
            OutcomeType.PARTIAL: 0.7,
            OutcomeType.FAILURE: 1.0 - FAILURE_PENALTY,
            OutcomeType.TIMEOUT: 0.3,
            OutcomeType.CANCELLED: 0.1
        }
        return multipliers.get(outcome.outcome_type, 0.5)

    def create_reward_signal(
        self,
        trajectory: SkillTrajectory,
        outcome: Outcome,
        user_preferences: Optional[UserPreferenceVector] = None
    ) -> RewardSignal:
        """
        Create a reward signal for storage and learning.

        Args:
            trajectory: The skill execution trajectory
            outcome: The outcome of the trajectory
            user_preferences: User preference vector

        Returns:
            RewardSignal ready for storage
        """
        import uuid

        breakdown = self.get_reward_breakdown(trajectory, outcome, user_preferences)

        signal = RewardSignal(
            signal_id=str(uuid.uuid4())[:8],
            trajectory_id=trajectory.trajectory_id,
            reward=breakdown.total_reward,
            breakdown=breakdown,
            user_id=trajectory.user_id,
            context=trajectory.task_context,
            metadata={
                "skills_used": trajectory.skills_used,
                "models_used": trajectory.models_used,
                "outcome_type": outcome.outcome_type.value,
                "total_cost": trajectory.total_cost,
                "total_latency": trajectory.total_latency
            }
        )

        self._reward_history.append(signal)
        return signal

    def get_reward_statistics(
        self,
        context: Optional[str] = None,
        user_id: Optional[str] = None,
        last_n: int = 100
    ) -> Dict[str, Any]:
        """
        Get statistics on recent rewards.

        Args:
            context: Filter by context
            user_id: Filter by user
            last_n: Number of recent signals to analyze

        Returns:
            Reward statistics
        """
        signals = self._reward_history[-last_n:]

        if context:
            signals = [s for s in signals if s.context == context]
        if user_id:
            signals = [s for s in signals if s.user_id == user_id]

        if not signals:
            return {
                "count": 0,
                "avg_reward": 0.0,
                "min_reward": 0.0,
                "max_reward": 0.0,
                "std_reward": 0.0
            }

        rewards = [s.reward for s in signals]
        avg = sum(rewards) / len(rewards)
        variance = sum((r - avg) ** 2 for r in rewards) / len(rewards)

        return {
            "count": len(signals),
            "avg_reward": avg,
            "min_reward": min(rewards),
            "max_reward": max(rewards),
            "std_reward": math.sqrt(variance),
            "normalizer_stats": self.normalizer.get_stats()
        }


# =============================================================================
# REWARD AGGREGATOR
# =============================================================================

class RewardAggregator:
    """
    Aggregates rewards across multiple trajectories for skill/model comparison.
    """

    def __init__(self):
        self._rewards_by_skill: Dict[str, List[float]] = {}
        self._rewards_by_model: Dict[str, List[float]] = {}
        self._rewards_by_context: Dict[str, List[float]] = {}

    def add_reward(self, signal: RewardSignal) -> None:
        """Add a reward signal to the aggregator."""
        # By skill
        for skill in signal.metadata.get("skills_used", []):
            if skill not in self._rewards_by_skill:
                self._rewards_by_skill[skill] = []
            self._rewards_by_skill[skill].append(signal.reward)

        # By model
        for model in signal.metadata.get("models_used", []):
            if model not in self._rewards_by_model:
                self._rewards_by_model[model] = []
            self._rewards_by_model[model].append(signal.reward)

        # By context
        if signal.context:
            if signal.context not in self._rewards_by_context:
                self._rewards_by_context[signal.context] = []
            self._rewards_by_context[signal.context].append(signal.reward)

    def get_skill_rankings(self) -> List[Tuple[str, float, int]]:
        """Get skills ranked by average reward."""
        rankings = []
        for skill, rewards in self._rewards_by_skill.items():
            avg = sum(rewards) / len(rewards) if rewards else 0
            rankings.append((skill, avg, len(rewards)))
        return sorted(rankings, key=lambda x: x[1], reverse=True)

    def get_model_rankings(self) -> List[Tuple[str, float, int]]:
        """Get models ranked by average reward."""
        rankings = []
        for model, rewards in self._rewards_by_model.items():
            avg = sum(rewards) / len(rewards) if rewards else 0
            rankings.append((model, avg, len(rewards)))
        return sorted(rankings, key=lambda x: x[1], reverse=True)

    def get_best_skill_for_context(self, context: str) -> Optional[str]:
        """Get the best-performing skill for a context."""
        # This would need cross-referencing with context data
        # Placeholder for now
        rankings = self.get_skill_rankings()
        return rankings[0][0] if rankings else None

    def get_summary(self) -> Dict[str, Any]:
        """Get aggregation summary."""
        return {
            "skills_tracked": len(self._rewards_by_skill),
            "models_tracked": len(self._rewards_by_model),
            "contexts_tracked": len(self._rewards_by_context),
            "skill_rankings": self.get_skill_rankings()[:5],
            "model_rankings": self.get_model_rankings()[:5]
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_trajectory_reward(
    executions: List[Dict[str, Any]],
    outcome_success: bool,
    accuracy: float = 1.0,
    required_correction: bool = False,
    user_preferences: Optional[Dict[str, float]] = None
) -> float:
    """
    Convenience function to compute reward from raw data.

    Args:
        executions: List of execution dicts
        outcome_success: Whether the trajectory succeeded
        accuracy: Accuracy score (0-1)
        required_correction: Whether user correction was needed
        user_preferences: Dict with accuracy_weight, cost_weight, latency_weight

    Returns:
        Computed reward
    """
    # Build trajectory
    skill_executions = [
        SkillExecution(
            skill_name=e.get("skill_name", "unknown"),
            capability=e.get("capability", "unknown"),
            model_used=e.get("model_used", "unknown"),
            tokens_input=e.get("tokens_input", 0),
            tokens_output=e.get("tokens_output", 0),
            tokens_thinking=e.get("tokens_thinking", 0),
            cost_usd=e.get("cost_usd", 0.0),
            latency_ms=e.get("latency_ms", 0),
            success=e.get("success", True)
        )
        for e in executions
    ]

    trajectory = SkillTrajectory(
        trajectory_id="temp",
        task_description="",
        executions=skill_executions
    )

    outcome = Outcome(
        outcome_type=OutcomeType.SUCCESS if outcome_success else OutcomeType.FAILURE,
        accuracy=accuracy,
        required_correction=required_correction
    )

    prefs = None
    if user_preferences:
        prefs = UserPreferenceVector(
            accuracy_weight=user_preferences.get("accuracy_weight", DEFAULT_ACCURACY_WEIGHT),
            cost_weight=user_preferences.get("cost_weight", DEFAULT_COST_WEIGHT),
            latency_weight=user_preferences.get("latency_weight", DEFAULT_LATENCY_WEIGHT)
        )

    calculator = RewardCalculator()
    return calculator.compute_reward(trajectory, outcome, prefs)


def create_reward_calculator() -> RewardCalculator:
    """Create a default reward calculator."""
    return RewardCalculator()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Arcus Reward Signals - Test Run")
    print("=" * 50)

    calculator = RewardCalculator()

    # Create a test trajectory
    trajectory = SkillTrajectory(
        trajectory_id="test-001",
        task_description="Find information about TechCorp",
        task_context="research",
        executions=[
            SkillExecution(
                skill_name="knowledge_repository",
                capability="recall",
                model_used="claude-sonnet",
                tokens_input=1000,
                tokens_output=500,
                cost_usd=0.002,
                latency_ms=800,
                success=True
            ),
            SkillExecution(
                skill_name="research",
                capability="search",
                model_used="gemini-3-flash",
                tokens_input=500,
                tokens_output=2000,
                cost_usd=0.003,
                latency_ms=1500,
                success=True
            )
        ]
    )

    # Create outcome
    outcome = Outcome(
        outcome_type=OutcomeType.SUCCESS,
        accuracy=0.9,
        output_quality=0.85,
        required_correction=False
    )

    # Create user preferences
    preferences = UserPreferenceVector(
        accuracy_weight=0.5,
        cost_weight=0.3,
        latency_weight=0.2,
        model_preferences={"claude-sonnet": 0.8, "gemini-3-flash": 0.7},
        skill_preferences={"knowledge_repository": 0.9}
    )

    # Test reward computation
    print("\n1. Reward Computation Test:")
    breakdown = calculator.get_reward_breakdown(trajectory, outcome, preferences)
    print(f"   Total Reward: {breakdown.total_reward:.4f}")
    print(f"   Accuracy Component: {breakdown.accuracy_component:.4f}")
    print(f"   Cost Component: {breakdown.cost_component:.4f}")
    print(f"   Latency Component: {breakdown.latency_component:.4f}")
    print(f"   Preference Bonus: {breakdown.preference_bonus:.4f}")
    print(f"   Efficiency Bonus: {breakdown.efficiency_bonus:.4f}")

    # Test with correction
    print("\n2. With Correction Penalty:")
    outcome_corrected = Outcome(
        outcome_type=OutcomeType.SUCCESS,
        accuracy=0.8,
        required_correction=True,
        correction_severity=0.3
    )
    reward_corrected = calculator.compute_reward(trajectory, outcome_corrected, preferences)
    print(f"   Reward with correction: {reward_corrected:.4f}")

    # Test with failure
    print("\n3. With Failure:")
    outcome_failed = Outcome(
        outcome_type=OutcomeType.FAILURE,
        accuracy=0.2,
        error_message="Task could not be completed"
    )
    reward_failed = calculator.compute_reward(trajectory, outcome_failed, preferences)
    print(f"   Reward with failure: {reward_failed:.4f}")

    # Create reward signal
    print("\n4. Reward Signal Creation:")
    signal = calculator.create_reward_signal(trajectory, outcome, preferences)
    print(f"   Signal ID: {signal.signal_id}")
    print(f"   Reward: {signal.reward:.4f}")

    # Test statistics
    print("\n5. Reward Statistics:")
    # Add more signals for statistics
    for i in range(10):
        calculator.create_reward_signal(trajectory, outcome, preferences)
    stats = calculator.get_reward_statistics()
    print(f"   Count: {stats['count']}")
    print(f"   Avg Reward: {stats['avg_reward']:.4f}")
    print(f"   Std Reward: {stats['std_reward']:.4f}")

    print("\nTest complete!")
