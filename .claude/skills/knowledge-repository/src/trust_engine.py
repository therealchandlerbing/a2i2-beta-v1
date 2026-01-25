"""
Arcus Trust Engine - Autonomy Trust Progression System

This module manages trust levels and autonomy progression:
1. Track trust scores by action category
2. Compute trust deltas from outcomes
3. Manage autonomy level transitions
4. Provide trust-based reward signals
5. Enforce autonomy boundaries

Implements the "Autonomy Trust as Reward" enhancement from Phase 3.

Usage:
    from trust_engine import TrustEngine, AutonomyLevel, ActionOutcome

    engine = TrustEngine()

    # Record an action outcome
    engine.record_outcome(
        action_type="file_read",
        category="read",
        success=True,
        required_correction=False
    )

    # Check current trust level
    level = engine.get_autonomy_level()

    # Get trust-based reward signal
    reward = engine.compute_trust_reward(action_type, outcome)
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict


# =============================================================================
# CONSTANTS
# =============================================================================

# Trust score deltas
TRUST_DELTA_SUCCESS = 0.01           # Clean success
TRUST_DELTA_CORRECTED = -0.005       # Success with correction
TRUST_DELTA_FAILURE = -0.02          # Failure
TRUST_DELTA_BOUNDARY_VIOLATION = -0.05  # Boundary violation
TRUST_DELTA_OVERRIDE = -0.03         # Human override

# Trust decay (for staleness)
TRUST_DECAY_RATE = 0.001             # Daily decay
TRUST_DECAY_INACTIVE_DAYS = 7        # Start decay after N days

# Autonomy level thresholds
AUTONOMY_THRESHOLDS = {
    0: 0.0,     # Assisted
    1: 0.3,     # Supervised
    2: 0.5,     # Autonomous
    3: 0.7,     # Trusted
    4: 0.85     # Partner
}

# Minimum actions for level consideration
MIN_ACTIONS_FOR_LEVEL = {
    0: 0,
    1: 10,
    2: 50,
    3: 200,
    4: 500
}

# Category weights for overall trust
CATEGORY_WEIGHTS = {
    "read": 0.1,
    "write": 0.2,
    "execute": 0.25,
    "communicate": 0.15,
    "schedule": 0.1,
    "financial": 0.15,
    "system": 0.05
}

# Trust reward scaling
TRUST_REWARD_SCALE = 0.1  # How much trust affects reward


# =============================================================================
# ENUMS
# =============================================================================

class AutonomyLevel(Enum):
    ASSISTED = 0      # Human does, Claude advises
    SUPERVISED = 1    # Claude proposes, human confirms
    AUTONOMOUS = 2    # Claude acts, human reviews after
    TRUSTED = 3       # Claude acts, exceptions only
    PARTNER = 4       # Full peer-level collaboration

    @property
    def description(self) -> str:
        descriptions = {
            0: "Human executes, Claude advises",
            1: "Claude proposes, human confirms",
            2: "Claude acts, human reviews after",
            3: "Claude acts, escalates exceptions only",
            4: "Full peer-level collaboration"
        }
        return descriptions.get(self.value, "Unknown")


class ActionCategory(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    COMMUNICATE = "communicate"
    SCHEDULE = "schedule"
    FINANCIAL = "financial"
    SYSTEM = "system"


class OutcomeType(Enum):
    SUCCESS = "success"
    SUCCESS_CORRECTED = "success_corrected"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    OVERRIDDEN = "overridden"
    ESCALATED = "escalated"
    BOUNDARY_VIOLATION = "boundary_violation"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ActionOutcome:
    """Outcome of an autonomous action."""
    action_id: str
    action_type: str
    category: ActionCategory
    outcome_type: OutcomeType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correction_severity: float = 0.0  # 0-1
    user_feedback: Optional[str] = None
    boundary_check_passed: bool = True
    boundaries_checked: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.outcome_type in (OutcomeType.SUCCESS, OutcomeType.SUCCESS_CORRECTED)

    @property
    def required_correction(self) -> bool:
        return self.outcome_type == OutcomeType.SUCCESS_CORRECTED


@dataclass
class TrustMetrics:
    """Trust metrics for a category or overall."""
    total_actions: int = 0
    successful_actions: int = 0
    corrected_actions: int = 0
    failed_actions: int = 0
    overridden_actions: int = 0
    boundary_violations: int = 0
    trust_score: float = 0.5  # Start neutral
    last_action_at: Optional[str] = None
    first_action_at: Optional[str] = None

    @property
    def success_rate(self) -> float:
        if self.total_actions == 0:
            return 0.0
        return self.successful_actions / self.total_actions

    @property
    def correction_rate(self) -> float:
        if self.successful_actions == 0:
            return 0.0
        return self.corrected_actions / self.successful_actions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "corrected_actions": self.corrected_actions,
            "failed_actions": self.failed_actions,
            "overridden_actions": self.overridden_actions,
            "boundary_violations": self.boundary_violations,
            "trust_score": self.trust_score,
            "success_rate": self.success_rate,
            "correction_rate": self.correction_rate,
            "last_action_at": self.last_action_at,
            "first_action_at": self.first_action_at
        }


@dataclass
class TrustState:
    """Complete trust state for a user."""
    user_id: str = "default"
    overall_trust: float = 0.5
    current_level: AutonomyLevel = AutonomyLevel.ASSISTED
    metrics_by_category: Dict[str, TrustMetrics] = field(default_factory=dict)
    level_history: List[Dict[str, Any]] = field(default_factory=list)
    pending_level_upgrade: Optional[int] = None
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "overall_trust": self.overall_trust,
            "current_level": self.current_level.value,
            "current_level_name": self.current_level.name,
            "metrics_by_category": {
                cat: metrics.to_dict()
                for cat, metrics in self.metrics_by_category.items()
            },
            "level_history": self.level_history,
            "pending_level_upgrade": self.pending_level_upgrade,
            "last_updated": self.last_updated
        }


@dataclass
class TrustRewardSignal:
    """Trust-based reward signal."""
    base_reward: float
    trust_bonus: float
    trust_penalty: float
    final_reward: float
    trust_delta: float
    new_trust_score: float
    autonomy_level_change: Optional[int] = None
    explanation: str = ""


@dataclass
class BoundaryDefinition:
    """Definition of an autonomy boundary."""
    name: str
    description: str
    category: ActionCategory
    min_level: AutonomyLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    always_confirm: bool = False
    never_without_asking: bool = False


# =============================================================================
# TRUST ENGINE
# =============================================================================

class TrustEngine:
    """
    Manages trust progression and autonomy levels.

    Features:
    1. Track trust scores by action category
    2. Compute trust deltas from outcomes
    3. Manage autonomy level transitions
    4. Provide trust-based reward signals
    5. Enforce autonomy boundaries
    """

    def __init__(
        self,
        user_id: str = "default",
        initial_level: AutonomyLevel = AutonomyLevel.ASSISTED,
        boundaries: Optional[List[BoundaryDefinition]] = None
    ):
        """
        Initialize the trust engine.

        Args:
            user_id: User identifier
            initial_level: Starting autonomy level
            boundaries: Boundary definitions
        """
        self.user_id = user_id
        self._state = TrustState(
            user_id=user_id,
            current_level=initial_level
        )
        self._boundaries = {b.name: b for b in (boundaries or [])}
        self._init_default_boundaries()
        self._outcome_history: List[ActionOutcome] = []

    def _init_default_boundaries(self) -> None:
        """Initialize default boundary definitions."""
        default_boundaries = [
            BoundaryDefinition(
                name="file_write",
                description="Writing to files",
                category=ActionCategory.WRITE,
                min_level=AutonomyLevel.SUPERVISED
            ),
            BoundaryDefinition(
                name="external_communication",
                description="Sending external communications",
                category=ActionCategory.COMMUNICATE,
                min_level=AutonomyLevel.AUTONOMOUS,
                always_confirm=True
            ),
            BoundaryDefinition(
                name="financial_actions",
                description="Any financial operations",
                category=ActionCategory.FINANCIAL,
                min_level=AutonomyLevel.TRUSTED,
                always_confirm=True
            ),
            BoundaryDefinition(
                name="system_changes",
                description="System configuration changes",
                category=ActionCategory.SYSTEM,
                min_level=AutonomyLevel.PARTNER,
                never_without_asking=True
            ),
            BoundaryDefinition(
                name="destructive_operations",
                description="Destructive file or data operations",
                category=ActionCategory.WRITE,
                min_level=AutonomyLevel.TRUSTED,
                always_confirm=True
            ),
        ]

        for boundary in default_boundaries:
            if boundary.name not in self._boundaries:
                self._boundaries[boundary.name] = boundary

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def record_outcome(
        self,
        action_type: str,
        category: str,
        success: bool,
        required_correction: bool = False,
        correction_severity: float = 0.0,
        was_overridden: bool = False,
        boundary_violation: bool = False,
        user_feedback: Optional[str] = None
    ) -> TrustRewardSignal:
        """
        Record an action outcome and update trust.

        Args:
            action_type: Type of action performed
            category: Action category
            success: Whether the action succeeded
            required_correction: Whether user correction was needed
            correction_severity: Severity of correction (0-1)
            was_overridden: Whether human overrode the action
            boundary_violation: Whether a boundary was violated
            user_feedback: Optional user feedback

        Returns:
            Trust-based reward signal
        """
        import uuid

        # Determine outcome type
        if boundary_violation:
            outcome_type = OutcomeType.BOUNDARY_VIOLATION
        elif was_overridden:
            outcome_type = OutcomeType.OVERRIDDEN
        elif success and required_correction:
            outcome_type = OutcomeType.SUCCESS_CORRECTED
        elif success:
            outcome_type = OutcomeType.SUCCESS
        else:
            outcome_type = OutcomeType.FAILURE

        # Create outcome record
        outcome = ActionOutcome(
            action_id=str(uuid.uuid4())[:8],
            action_type=action_type,
            category=ActionCategory(category) if isinstance(category, str) else category,
            outcome_type=outcome_type,
            correction_severity=correction_severity,
            user_feedback=user_feedback,
            boundary_check_passed=not boundary_violation
        )

        self._outcome_history.append(outcome)

        # Update trust metrics
        trust_delta = self._update_trust_metrics(outcome)

        # Check for level transitions
        level_change = self._check_level_transition()

        # Compute trust reward signal
        reward_signal = self._compute_trust_reward(outcome, trust_delta, level_change)

        return reward_signal

    def get_autonomy_level(self) -> AutonomyLevel:
        """Get current autonomy level."""
        return self._state.current_level

    def get_trust_score(self, category: Optional[str] = None) -> float:
        """
        Get trust score.

        Args:
            category: Specific category (overall if None)

        Returns:
            Trust score (0-1)
        """
        if category is None:
            return self._state.overall_trust
        metrics = self._state.metrics_by_category.get(category)
        return metrics.trust_score if metrics else 0.5

    def get_trust_state(self) -> TrustState:
        """Get complete trust state."""
        return self._state

    def get_metrics(self, category: Optional[str] = None) -> TrustMetrics:
        """
        Get trust metrics.

        Args:
            category: Specific category (overall if None)

        Returns:
            Trust metrics
        """
        if category is None:
            # Aggregate metrics
            total = TrustMetrics()
            for metrics in self._state.metrics_by_category.values():
                total.total_actions += metrics.total_actions
                total.successful_actions += metrics.successful_actions
                total.corrected_actions += metrics.corrected_actions
                total.failed_actions += metrics.failed_actions
                total.overridden_actions += metrics.overridden_actions
                total.boundary_violations += metrics.boundary_violations
            total.trust_score = self._state.overall_trust
            return total

        return self._state.metrics_by_category.get(category, TrustMetrics())

    def check_boundary(
        self,
        action_type: str,
        category: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Check if an action is within autonomy boundaries.

        Args:
            action_type: Type of action
            category: Action category
            context: Additional context

        Returns:
            Tuple of (passed, boundaries_checked, violations)
        """
        passed = True
        boundaries_checked = []
        violations = []

        cat = ActionCategory(category) if isinstance(category, str) else category
        current_level = self._state.current_level

        for name, boundary in self._boundaries.items():
            if boundary.category != cat:
                continue

            boundaries_checked.append(name)

            # Check minimum level
            if current_level.value < boundary.min_level.value:
                passed = False
                violations.append(f"{name}: requires {boundary.min_level.name} level")

            # Check always_confirm
            if boundary.always_confirm and current_level.value < AutonomyLevel.PARTNER.value:
                # This doesn't fail, just notes it needs confirmation
                pass

            # Check never_without_asking
            if boundary.never_without_asking:
                passed = False
                violations.append(f"{name}: requires explicit user permission")

        return passed, boundaries_checked, violations

    def can_act_autonomously(
        self,
        action_type: str,
        category: str
    ) -> bool:
        """
        Check if an action can be performed autonomously.

        Args:
            action_type: Type of action
            category: Action category

        Returns:
            Whether autonomous action is allowed
        """
        passed, _, _ = self.check_boundary(action_type, category)
        return passed and self._state.current_level.value >= AutonomyLevel.AUTONOMOUS.value

    def propose_level_upgrade(self) -> Optional[AutonomyLevel]:
        """
        Check if a level upgrade should be proposed.

        Returns:
            Proposed new level if eligible, None otherwise
        """
        current = self._state.current_level.value
        next_level = current + 1

        if next_level > AutonomyLevel.PARTNER.value:
            return None

        # Check threshold
        threshold = AUTONOMY_THRESHOLDS.get(next_level, 1.0)
        if self._state.overall_trust < threshold:
            return None

        # Check minimum actions
        total_actions = sum(
            m.total_actions for m in self._state.metrics_by_category.values()
        )
        min_actions = MIN_ACTIONS_FOR_LEVEL.get(next_level, 0)
        if total_actions < min_actions:
            return None

        self._state.pending_level_upgrade = next_level
        return AutonomyLevel(next_level)

    def confirm_level_upgrade(self) -> bool:
        """
        Confirm a pending level upgrade.

        Returns:
            Whether upgrade was confirmed
        """
        if self._state.pending_level_upgrade is None:
            return False

        new_level = AutonomyLevel(self._state.pending_level_upgrade)
        self._state.level_history.append({
            "from": self._state.current_level.value,
            "to": new_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "trust_score": self._state.overall_trust
        })
        self._state.current_level = new_level
        self._state.pending_level_upgrade = None

        return True

    def reject_level_upgrade(self) -> None:
        """Reject a pending level upgrade."""
        self._state.pending_level_upgrade = None

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _update_trust_metrics(self, outcome: ActionOutcome) -> float:
        """Update trust metrics and return trust delta."""
        category = outcome.category.value

        # Get or create metrics for category
        if category not in self._state.metrics_by_category:
            self._state.metrics_by_category[category] = TrustMetrics()
        metrics = self._state.metrics_by_category[category]

        # Update counts
        metrics.total_actions += 1
        metrics.last_action_at = outcome.timestamp
        if metrics.first_action_at is None:
            metrics.first_action_at = outcome.timestamp

        if outcome.outcome_type == OutcomeType.SUCCESS:
            metrics.successful_actions += 1
        elif outcome.outcome_type == OutcomeType.SUCCESS_CORRECTED:
            metrics.successful_actions += 1
            metrics.corrected_actions += 1
        elif outcome.outcome_type == OutcomeType.FAILURE:
            metrics.failed_actions += 1
        elif outcome.outcome_type == OutcomeType.OVERRIDDEN:
            metrics.overridden_actions += 1
        elif outcome.outcome_type == OutcomeType.BOUNDARY_VIOLATION:
            metrics.boundary_violations += 1

        # Calculate trust delta
        trust_delta = self._calculate_trust_delta(outcome)

        # Update category trust score
        metrics.trust_score = max(0.0, min(1.0, metrics.trust_score + trust_delta))

        # Update overall trust (weighted average)
        self._update_overall_trust()

        return trust_delta

    def _calculate_trust_delta(self, outcome: ActionOutcome) -> float:
        """Calculate trust delta for an outcome."""
        if outcome.outcome_type == OutcomeType.SUCCESS:
            return TRUST_DELTA_SUCCESS
        elif outcome.outcome_type == OutcomeType.SUCCESS_CORRECTED:
            # Scale by correction severity
            return TRUST_DELTA_CORRECTED * (1 + outcome.correction_severity)
        elif outcome.outcome_type == OutcomeType.FAILURE:
            return TRUST_DELTA_FAILURE
        elif outcome.outcome_type == OutcomeType.OVERRIDDEN:
            return TRUST_DELTA_OVERRIDE
        elif outcome.outcome_type == OutcomeType.BOUNDARY_VIOLATION:
            return TRUST_DELTA_BOUNDARY_VIOLATION
        else:
            return 0.0

    def _update_overall_trust(self) -> None:
        """Update overall trust from category trust scores."""
        weighted_sum = 0.0
        total_weight = 0.0

        for category, metrics in self._state.metrics_by_category.items():
            weight = CATEGORY_WEIGHTS.get(category, 0.1)
            # Weight by number of actions too
            action_weight = min(1.0, metrics.total_actions / 10)
            effective_weight = weight * (0.5 + 0.5 * action_weight)
            weighted_sum += metrics.trust_score * effective_weight
            total_weight += effective_weight

        if total_weight > 0:
            self._state.overall_trust = weighted_sum / total_weight
        else:
            self._state.overall_trust = 0.5

        self._state.last_updated = datetime.utcnow().isoformat()

    def _check_level_transition(self) -> Optional[int]:
        """Check if autonomy level should change."""
        current = self._state.current_level.value

        # Check for downgrade
        if current > 0:
            threshold = AUTONOMY_THRESHOLDS.get(current, 0.0)
            if self._state.overall_trust < threshold * 0.8:  # 20% buffer
                # Downgrade
                new_level = current - 1
                self._state.level_history.append({
                    "from": current,
                    "to": new_level,
                    "timestamp": datetime.utcnow().isoformat(),
                    "trust_score": self._state.overall_trust,
                    "reason": "trust_below_threshold"
                })
                self._state.current_level = AutonomyLevel(new_level)
                return new_level - current  # Negative for downgrade

        return None

    def _compute_trust_reward(
        self,
        outcome: ActionOutcome,
        trust_delta: float,
        level_change: Optional[int]
    ) -> TrustRewardSignal:
        """Compute trust-based reward signal."""
        # Base reward from outcome
        base_rewards = {
            OutcomeType.SUCCESS: 1.0,
            OutcomeType.SUCCESS_CORRECTED: 0.7,
            OutcomeType.FAILURE: 0.0,
            OutcomeType.TIMEOUT: 0.1,
            OutcomeType.CANCELLED: 0.2,
            OutcomeType.OVERRIDDEN: 0.3,
            OutcomeType.ESCALATED: 0.5,
            OutcomeType.BOUNDARY_VIOLATION: 0.0
        }
        base_reward = base_rewards.get(outcome.outcome_type, 0.5)

        # Trust bonus (for high trust)
        trust_bonus = 0.0
        if self._state.overall_trust > 0.7:
            trust_bonus = (self._state.overall_trust - 0.7) * TRUST_REWARD_SCALE

        # Trust penalty (for low trust or violations)
        trust_penalty = 0.0
        if self._state.overall_trust < 0.3:
            trust_penalty = (0.3 - self._state.overall_trust) * TRUST_REWARD_SCALE
        if outcome.outcome_type == OutcomeType.BOUNDARY_VIOLATION:
            trust_penalty += 0.2

        # Final reward
        final_reward = max(0.0, min(1.0, base_reward + trust_bonus - trust_penalty))

        # Generate explanation
        explanation = self._generate_explanation(outcome, trust_delta, level_change)

        return TrustRewardSignal(
            base_reward=base_reward,
            trust_bonus=trust_bonus,
            trust_penalty=trust_penalty,
            final_reward=final_reward,
            trust_delta=trust_delta,
            new_trust_score=self._state.overall_trust,
            autonomy_level_change=level_change,
            explanation=explanation
        )

    def _generate_explanation(
        self,
        outcome: ActionOutcome,
        trust_delta: float,
        level_change: Optional[int]
    ) -> str:
        """Generate explanation for trust change."""
        parts = []

        if outcome.success:
            parts.append(f"Action succeeded")
            if outcome.required_correction:
                parts.append(f"but required correction")
        else:
            parts.append(f"Action failed ({outcome.outcome_type.value})")

        parts.append(f"Trust delta: {trust_delta:+.3f}")
        parts.append(f"New trust: {self._state.overall_trust:.3f}")

        if level_change is not None:
            if level_change > 0:
                parts.append(f"Level upgraded to {self._state.current_level.name}")
            else:
                parts.append(f"Level downgraded to {self._state.current_level.name}")

        return ". ".join(parts)

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_trust_statistics(self) -> Dict[str, Any]:
        """Get comprehensive trust statistics."""
        total_metrics = self.get_metrics()

        return {
            "user_id": self.user_id,
            "current_level": self._state.current_level.name,
            "overall_trust": self._state.overall_trust,
            "total_actions": total_metrics.total_actions,
            "success_rate": total_metrics.success_rate,
            "correction_rate": total_metrics.correction_rate,
            "boundary_violations": total_metrics.boundary_violations,
            "metrics_by_category": {
                cat: metrics.to_dict()
                for cat, metrics in self._state.metrics_by_category.items()
            },
            "level_history_count": len(self._state.level_history),
            "pending_upgrade": self._state.pending_level_upgrade is not None,
            "days_at_current_level": self._days_at_current_level()
        }

    def _days_at_current_level(self) -> int:
        """Calculate days at current level."""
        if not self._state.level_history:
            return 0

        last_change = self._state.level_history[-1].get("timestamp")
        if not last_change:
            return 0

        last_dt = datetime.fromisoformat(last_change.replace("Z", "+00:00"))
        now = datetime.utcnow()
        return (now - last_dt.replace(tzinfo=None)).days


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_trust_engine(user_id: str = "default") -> TrustEngine:
    """Create a default trust engine."""
    return TrustEngine(user_id=user_id)


def quick_trust_check(
    action_type: str,
    category: str,
    user_id: str = "default"
) -> Tuple[bool, AutonomyLevel]:
    """
    Quick check if an action is allowed.

    Returns:
        Tuple of (allowed, current_level)
    """
    engine = TrustEngine(user_id=user_id)
    allowed = engine.can_act_autonomously(action_type, category)
    return allowed, engine.get_autonomy_level()


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Arcus Trust Engine - Test Run")
    print("=" * 50)

    engine = TrustEngine(user_id="test_user")

    # Test initial state
    print("\n1. Initial State:")
    print(f"   Level: {engine.get_autonomy_level().name}")
    print(f"   Trust Score: {engine.get_trust_score():.3f}")

    # Test boundary checking
    print("\n2. Boundary Check:")
    passed, checked, violations = engine.check_boundary("git_commit", "write")
    print(f"   Passed: {passed}")
    print(f"   Checked: {checked}")
    print(f"   Violations: {violations}")

    # Test recording successful outcomes
    print("\n3. Recording Successful Actions:")
    for i in range(10):
        signal = engine.record_outcome(
            action_type="file_read",
            category="read",
            success=True,
            required_correction=False
        )
    print(f"   After 10 successes:")
    print(f"   Trust Score: {engine.get_trust_score():.3f}")
    print(f"   Level: {engine.get_autonomy_level().name}")

    # Test recording with corrections
    print("\n4. Recording Actions with Corrections:")
    for i in range(3):
        signal = engine.record_outcome(
            action_type="code_edit",
            category="write",
            success=True,
            required_correction=True,
            correction_severity=0.3
        )
    print(f"   After corrections:")
    print(f"   Trust Score: {engine.get_trust_score():.3f}")

    # Test recording failure
    print("\n5. Recording Failure:")
    signal = engine.record_outcome(
        action_type="api_call",
        category="execute",
        success=False
    )
    print(f"   Trust Delta: {signal.trust_delta:.3f}")
    print(f"   New Trust: {signal.new_trust_score:.3f}")

    # Test boundary violation
    print("\n6. Boundary Violation:")
    signal = engine.record_outcome(
        action_type="send_email",
        category="communicate",
        success=True,
        boundary_violation=True
    )
    print(f"   Trust Delta: {signal.trust_delta:.3f}")
    print(f"   Base Reward: {signal.base_reward:.3f}")
    print(f"   Final Reward: {signal.final_reward:.3f}")

    # Test level upgrade proposal
    print("\n7. Level Upgrade Check:")
    # Add more successful actions
    for i in range(50):
        engine.record_outcome(
            action_type="file_read",
            category="read",
            success=True
        )
    proposed = engine.propose_level_upgrade()
    print(f"   Proposed Upgrade: {proposed.name if proposed else 'None'}")
    print(f"   Trust Score: {engine.get_trust_score():.3f}")

    # Get statistics
    print("\n8. Trust Statistics:")
    stats = engine.get_trust_statistics()
    print(f"   Total Actions: {stats['total_actions']}")
    print(f"   Success Rate: {stats['success_rate']:.1%}")
    print(f"   Categories: {list(stats['metrics_by_category'].keys())}")

    print("\nTest complete!")
