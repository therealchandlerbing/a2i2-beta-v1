"""
Arcus Knowledge Repository - Digital Twin Modeling
Phase 4: Model HOW Users Think

Digital Twin Modeling (DTM) captures cognitive patterns, decision-making
styles, and reasoning preferences to anticipate user needs and provide
personalized assistance.

Key Features:
- Cognitive pattern detection
- Decision-making style modeling
- Reasoning preference tracking
- Proactive suggestion generation
- Anticipatory context preparation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4


class CognitiveStyle(Enum):
    """Primary cognitive styles in decision-making."""
    ANALYTICAL = "analytical"       # Data-driven, systematic
    INTUITIVE = "intuitive"         # Gut feeling, pattern recognition
    DIRECTIVE = "directive"         # Quick, action-oriented
    CONCEPTUAL = "conceptual"       # Creative, big-picture
    BEHAVIORAL = "behavioral"       # People-focused, collaborative


class CommunicationStyle(Enum):
    """Communication preferences."""
    DIRECT = "direct"               # Short, to the point
    DETAILED = "detailed"           # Comprehensive, thorough
    VISUAL = "visual"               # Diagrams, charts preferred
    NARRATIVE = "narrative"         # Story-based, contextual
    STRUCTURED = "structured"       # Lists, hierarchies


class TimeOrientation(Enum):
    """Time perspective in decision-making."""
    PAST_FOCUSED = "past_focused"       # Historical precedent
    PRESENT_FOCUSED = "present_focused" # Current state
    FUTURE_FOCUSED = "future_focused"   # Long-term planning


class RiskTolerance(Enum):
    """Risk tolerance level."""
    RISK_AVERSE = "risk_averse"         # Conservative
    RISK_NEUTRAL = "risk_neutral"       # Balanced
    RISK_SEEKING = "risk_seeking"       # Aggressive


class InformationProcessing(Enum):
    """How user processes information."""
    SEQUENTIAL = "sequential"       # Step-by-step
    HOLISTIC = "holistic"           # Big picture first
    COMPARATIVE = "comparative"     # Side-by-side analysis
    ITERATIVE = "iterative"         # Refine through cycles


@dataclass
class CognitiveProfile:
    """User's cognitive profile capturing thinking patterns."""
    id: str
    user_id: str

    # Primary styles (can have multiple)
    cognitive_styles: Dict[CognitiveStyle, float] = field(default_factory=dict)
    communication_style: CommunicationStyle = CommunicationStyle.DIRECT
    time_orientation: TimeOrientation = TimeOrientation.PRESENT_FOCUSED
    risk_tolerance: RiskTolerance = RiskTolerance.RISK_NEUTRAL
    information_processing: InformationProcessing = InformationProcessing.SEQUENTIAL

    # Confidence in the profile
    profile_confidence: float = 0.5
    observations_count: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def primary_cognitive_style(self) -> Optional[CognitiveStyle]:
        """Get the dominant cognitive style."""
        if not self.cognitive_styles:
            return None
        return max(self.cognitive_styles.items(), key=lambda x: x[1])[0]


@dataclass
class DecisionPattern:
    """A captured decision-making pattern."""
    id: str
    user_id: str
    pattern_type: str

    # Pattern details
    context_tags: List[str]
    decision_factors: List[str]           # What they consider
    typical_questions: List[str]          # Questions they ask
    information_needs: List[str]          # What info they need
    decision_timeline: str                # Fast, moderate, deliberate

    # Outcomes
    successful_outcomes: int = 0
    unsuccessful_outcomes: int = 0

    # Confidence and usage
    confidence: float = 0.5
    times_observed: int = 1
    last_observed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningPreference:
    """Captured reasoning preference for specific domains."""
    id: str
    user_id: str
    domain: str                           # e.g., "technical", "financial", "strategic"

    # Reasoning characteristics
    preferred_frameworks: List[str]       # Frameworks they use
    data_preferences: List[str]           # Types of data they value
    analogies_used: List[str]             # Common analogies
    biases_detected: List[str]            # Cognitive biases observed

    # Depth preferences
    analysis_depth: str                   # "surface", "moderate", "deep"
    verification_level: str               # "trust", "verify", "deep_verify"

    confidence: float = 0.5
    observations: int = 1


@dataclass
class AnticipatedNeed:
    """A proactively anticipated user need."""
    id: str
    user_id: str

    # What we anticipate
    need_type: str                        # "information", "decision", "action", "reminder"
    description: str
    context_triggers: List[str]           # What triggers this need
    time_triggers: List[str]              # Time-based triggers

    # Prepared response
    prepared_content: Optional[str] = None
    preparation_confidence: float = 0.0

    # Tracking
    times_anticipated: int = 0
    times_fulfilled: int = 0
    accuracy_rate: float = 0.0

    # Validity
    valid_from: datetime = field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


@dataclass
class InteractionSignal:
    """A signal from user interaction for twin learning."""
    id: str
    user_id: str
    timestamp: datetime

    # Signal type
    signal_type: str                      # "question", "correction", "approval", "rejection"

    # Context
    topic: str
    entities_involved: List[str]
    task_type: str

    # Signal details
    content: str
    sentiment: str                        # "positive", "negative", "neutral"
    urgency: str                          # "low", "medium", "high"

    # Response to signal
    response_given: Optional[str] = None
    response_accepted: Optional[bool] = None
    correction_made: Optional[str] = None


@dataclass
class ProactiveSuggestion:
    """A proactive suggestion based on digital twin modeling."""
    id: str
    user_id: str

    # Suggestion details
    suggestion_type: str                  # "information", "action", "reminder", "insight"
    content: str
    reasoning: str                        # Why we're suggesting this

    # Confidence and relevance
    confidence: float
    relevance_score: float
    urgency: str

    # Trigger context
    triggered_by: List[str]               # What triggered this
    context_match_score: float

    # Tracking
    presented: bool = False
    accepted: Optional[bool] = None
    feedback: Optional[str] = None
    presented_at: Optional[datetime] = None


class CognitivePatternDetector:
    """Detect cognitive patterns from user interactions."""

    # Keywords/phrases that indicate cognitive styles
    STYLE_INDICATORS = {
        CognitiveStyle.ANALYTICAL: [
            "data", "numbers", "statistics", "evidence", "metrics",
            "analyze", "compare", "measure", "quantify", "prove",
        ],
        CognitiveStyle.INTUITIVE: [
            "feel", "sense", "gut", "instinct", "seems",
            "appears", "probably", "likely", "might",
        ],
        CognitiveStyle.DIRECTIVE: [
            "just", "quickly", "now", "immediately", "action",
            "do", "execute", "implement", "decide",
        ],
        CognitiveStyle.CONCEPTUAL: [
            "vision", "strategy", "idea", "concept", "possibility",
            "imagine", "creative", "innovative", "transform",
        ],
        CognitiveStyle.BEHAVIORAL: [
            "team", "people", "together", "collaborate", "consensus",
            "everyone", "stakeholders", "opinion", "discuss",
        ],
    }

    COMMUNICATION_INDICATORS = {
        CommunicationStyle.DIRECT: ["brief", "short", "quick", "summary", "bottom line"],
        CommunicationStyle.DETAILED: ["explain", "elaborate", "detail", "comprehensive", "thorough"],
        CommunicationStyle.VISUAL: ["show", "diagram", "chart", "visualize", "picture"],
        CommunicationStyle.NARRATIVE: ["story", "example", "case", "scenario", "context"],
        CommunicationStyle.STRUCTURED: ["list", "steps", "order", "organize", "hierarchy"],
    }

    TIME_INDICATORS = {
        TimeOrientation.PAST_FOCUSED: ["before", "previously", "historically", "last time", "precedent"],
        TimeOrientation.PRESENT_FOCUSED: ["now", "current", "today", "immediate", "present"],
        TimeOrientation.FUTURE_FOCUSED: ["will", "plan", "future", "long-term", "eventually"],
    }

    def detect_from_text(self, text: str) -> Dict[str, Any]:
        """
        Detect cognitive patterns from text.

        Returns:
            Dictionary with detected patterns and confidence scores
        """
        text_lower = text.lower()
        results = {
            "cognitive_styles": {},
            "communication_style": None,
            "time_orientation": None,
            "signals": [],
        }

        # Detect cognitive styles
        for style, indicators in self.STYLE_INDICATORS.items():
            count = sum(1 for ind in indicators if ind in text_lower)
            if count > 0:
                # Normalize by text length
                score = min(1.0, count / (len(text.split()) / 20 + 1))
                results["cognitive_styles"][style] = score

        # Detect communication style
        max_comm_score = 0
        for style, indicators in self.COMMUNICATION_INDICATORS.items():
            count = sum(1 for ind in indicators if ind in text_lower)
            if count > max_comm_score:
                max_comm_score = count
                results["communication_style"] = style

        # Detect time orientation
        max_time_score = 0
        for orientation, indicators in self.TIME_INDICATORS.items():
            count = sum(1 for ind in indicators if ind in text_lower)
            if count > max_time_score:
                max_time_score = count
                results["time_orientation"] = orientation

        return results

    def detect_from_behavior(
        self,
        questions_asked: List[str],
        decisions_made: List[Dict],
        corrections_given: List[str]
    ) -> Dict[str, Any]:
        """
        Detect patterns from behavioral signals.

        Args:
            questions_asked: Questions the user has asked
            decisions_made: Decisions with context
            corrections_given: Corrections user has made

        Returns:
            Behavioral pattern analysis
        """
        results = {
            "question_patterns": [],
            "decision_patterns": [],
            "correction_patterns": [],
            "inferred_preferences": [],
        }

        # Analyze questions
        question_types = {
            "clarification": 0,
            "verification": 0,
            "exploration": 0,
            "validation": 0,
        }

        for q in questions_asked:
            q_lower = q.lower()
            if any(w in q_lower for w in ["what do you mean", "clarify", "explain"]):
                question_types["clarification"] += 1
            elif any(w in q_lower for w in ["are you sure", "confirm", "correct"]):
                question_types["verification"] += 1
            elif any(w in q_lower for w in ["what if", "could we", "alternatives"]):
                question_types["exploration"] += 1
            elif any(w in q_lower for w in ["is this right", "does this make sense"]):
                question_types["validation"] += 1

        results["question_patterns"] = question_types

        # Analyze decisions
        if decisions_made:
            fast_decisions = sum(1 for d in decisions_made if d.get("time_to_decide", 999) < 60)
            slow_decisions = len(decisions_made) - fast_decisions

            results["decision_patterns"] = {
                "fast_ratio": fast_decisions / len(decisions_made) if decisions_made else 0,
                "data_requested_avg": sum(d.get("data_requested", 0) for d in decisions_made) / len(decisions_made),
            }

        # Analyze corrections
        if corrections_given:
            correction_types = {
                "factual": sum(1 for c in corrections_given if "wrong" in c.lower() or "incorrect" in c.lower()),
                "style": sum(1 for c in corrections_given if "prefer" in c.lower() or "rather" in c.lower()),
                "completeness": sum(1 for c in corrections_given if "more" in c.lower() or "also" in c.lower()),
            }
            results["correction_patterns"] = correction_types

        return results


class DigitalTwinEngine:
    """
    Main engine for Digital Twin Modeling.

    Builds and maintains a cognitive model of each user,
    enabling anticipatory and personalized assistance.
    """

    def __init__(self):
        self.profiles: Dict[str, CognitiveProfile] = {}
        self.decision_patterns: Dict[str, List[DecisionPattern]] = {}
        self.reasoning_preferences: Dict[str, List[ReasoningPreference]] = {}
        self.anticipated_needs: Dict[str, List[AnticipatedNeed]] = {}
        self.interaction_history: Dict[str, List[InteractionSignal]] = {}

        self.pattern_detector = CognitivePatternDetector()

        # Configuration
        self.min_observations_for_confidence = 10
        self.pattern_decay_days = 30
        self.anticipation_window_hours = 24

    def get_or_create_profile(self, user_id: str) -> CognitiveProfile:
        """Get existing profile or create new one."""
        if user_id not in self.profiles:
            self.profiles[user_id] = CognitiveProfile(
                id=str(uuid4()),
                user_id=user_id,
            )
        return self.profiles[user_id]

    def record_interaction(
        self,
        user_id: str,
        signal_type: str,
        content: str,
        topic: str,
        task_type: str,
        entities: Optional[List[str]] = None,
        response_given: Optional[str] = None,
        response_accepted: Optional[bool] = None,
        correction: Optional[str] = None,
    ) -> InteractionSignal:
        """
        Record an interaction signal and update the digital twin.

        Args:
            user_id: User identifier
            signal_type: Type of signal (question, correction, etc.)
            content: The content of the interaction
            topic: Topic of the interaction
            task_type: Type of task being performed
            entities: Entities involved
            response_given: Claude's response
            response_accepted: Whether user accepted the response
            correction: Any correction provided

        Returns:
            The recorded signal
        """
        signal = InteractionSignal(
            id=str(uuid4()),
            user_id=user_id,
            timestamp=datetime.utcnow(),
            signal_type=signal_type,
            topic=topic,
            entities_involved=entities or [],
            task_type=task_type,
            content=content,
            sentiment=self._detect_sentiment(content),
            urgency=self._detect_urgency(content),
            response_given=response_given,
            response_accepted=response_accepted,
            correction_made=correction,
        )

        # Store signal
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
        self.interaction_history[user_id].append(signal)

        # Update profile based on signal
        self._update_profile_from_signal(user_id, signal)

        # Check for new patterns
        self._detect_new_patterns(user_id)

        # Update anticipated needs
        self._update_anticipated_needs(user_id, signal)

        return signal

    def get_personalized_context(
        self,
        user_id: str,
        task_type: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get personalized context for a task based on digital twin.

        Args:
            user_id: User identifier
            task_type: Type of task
            topic: Optional topic

        Returns:
            Personalized context dictionary
        """
        profile = self.get_or_create_profile(user_id)
        context = {
            "user_id": user_id,
            "profile": {
                "primary_style": profile.primary_cognitive_style.value if profile.primary_cognitive_style else None,
                "communication_style": profile.communication_style.value,
                "time_orientation": profile.time_orientation.value,
                "risk_tolerance": profile.risk_tolerance.value,
                "information_processing": profile.information_processing.value,
            },
            "recommendations": [],
            "anticipated_needs": [],
            "relevant_patterns": [],
        }

        # Add recommendations based on profile
        context["recommendations"] = self._generate_recommendations(profile, task_type)

        # Add relevant decision patterns
        if user_id in self.decision_patterns:
            relevant = [p for p in self.decision_patterns[user_id]
                        if task_type in p.context_tags or (topic and topic in p.context_tags)]
            context["relevant_patterns"] = [
                {
                    "type": p.pattern_type,
                    "factors": p.decision_factors,
                    "questions": p.typical_questions,
                    "info_needs": p.information_needs,
                }
                for p in relevant[:3]
            ]

        # Add anticipated needs
        if user_id in self.anticipated_needs:
            valid_needs = [
                n for n in self.anticipated_needs[user_id]
                if n.valid_until is None or n.valid_until > datetime.utcnow()
            ]
            context["anticipated_needs"] = [
                {
                    "type": n.need_type,
                    "description": n.description,
                    "confidence": n.preparation_confidence,
                }
                for n in valid_needs[:5]
            ]

        return context

    def generate_proactive_suggestions(
        self,
        user_id: str,
        current_context: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """
        Generate proactive suggestions based on digital twin.

        Args:
            user_id: User identifier
            current_context: Current context (topic, entities, task, etc.)

        Returns:
            List of proactive suggestions
        """
        suggestions = []
        profile = self.get_or_create_profile(user_id)

        # 1. Suggestions based on anticipated needs
        if user_id in self.anticipated_needs:
            for need in self.anticipated_needs[user_id]:
                if self._context_matches_triggers(current_context, need.context_triggers):
                    suggestion = ProactiveSuggestion(
                        id=str(uuid4()),
                        user_id=user_id,
                        suggestion_type=need.need_type,
                        content=need.prepared_content or need.description,
                        reasoning=f"Based on anticipated need: {need.description}",
                        confidence=need.preparation_confidence,
                        relevance_score=need.accuracy_rate if need.times_anticipated > 0 else 0.5,
                        urgency="medium",
                        triggered_by=need.context_triggers,
                        context_match_score=0.8,
                    )
                    suggestions.append(suggestion)

        # 2. Suggestions based on decision patterns
        if user_id in self.decision_patterns:
            for pattern in self.decision_patterns[user_id]:
                if current_context.get("task_type") in pattern.context_tags:
                    # Suggest information they typically need
                    for info_need in pattern.information_needs[:2]:
                        suggestion = ProactiveSuggestion(
                            id=str(uuid4()),
                            user_id=user_id,
                            suggestion_type="information",
                            content=f"You typically want to know: {info_need}",
                            reasoning=f"Based on your decision pattern for {pattern.pattern_type}",
                            confidence=pattern.confidence,
                            relevance_score=pattern.confidence,
                            urgency="low",
                            triggered_by=[pattern.pattern_type],
                            context_match_score=0.7,
                        )
                        suggestions.append(suggestion)

        # 3. Suggestions based on cognitive style
        style_suggestions = self._generate_style_based_suggestions(
            profile, current_context
        )
        suggestions.extend(style_suggestions)

        # Sort by relevance and confidence
        suggestions.sort(
            key=lambda s: s.relevance_score * s.confidence,
            reverse=True
        )

        return suggestions[:5]  # Top 5 suggestions

    def adapt_response(
        self,
        user_id: str,
        response: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Adapt a response based on the user's digital twin.

        Args:
            user_id: User identifier
            response: Original response
            context: Current context

        Returns:
            Adapted response
        """
        profile = self.get_or_create_profile(user_id)

        # Adapt based on communication style
        if profile.communication_style == CommunicationStyle.DIRECT:
            # Shorten response
            response = self._make_concise(response)
        elif profile.communication_style == CommunicationStyle.DETAILED:
            # Add context (in production, would expand)
            pass
        elif profile.communication_style == CommunicationStyle.STRUCTURED:
            # Format as list if not already
            if not any(marker in response for marker in ["•", "-", "1.", "*"]):
                response = self._format_as_list(response)

        # Adapt based on cognitive style
        primary_style = profile.primary_cognitive_style
        if primary_style == CognitiveStyle.ANALYTICAL:
            # Add data emphasis
            if "data" not in response.lower() and "number" not in response.lower():
                response = response + "\n\nI can provide supporting data if helpful."
        elif primary_style == CognitiveStyle.CONCEPTUAL:
            # Add big picture framing
            if "overall" not in response.lower() and "big picture" not in response.lower():
                response = "Here's the big picture: " + response

        return response

    def predict_next_action(
        self,
        user_id: str,
        current_context: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """
        Predict likely next actions based on digital twin.

        Args:
            user_id: User identifier
            current_context: Current context

        Returns:
            List of (action, probability) tuples
        """
        predictions = []
        profile = self.get_or_create_profile(user_id)

        # Based on recent interaction patterns
        if user_id in self.interaction_history:
            recent = self.interaction_history[user_id][-20:]
            action_counts: Dict[str, int] = {}

            for signal in recent:
                action = signal.task_type
                action_counts[action] = action_counts.get(action, 0) + 1

            total = sum(action_counts.values())
            for action, count in action_counts.items():
                predictions.append((action, count / total))

        # Based on decision patterns
        if user_id in self.decision_patterns:
            for pattern in self.decision_patterns[user_id]:
                if self._context_matches_pattern(current_context, pattern):
                    predictions.append(
                        (f"decision:{pattern.pattern_type}", pattern.confidence * 0.8)
                    )

        # Based on time patterns (time of day, day of week)
        hour = datetime.utcnow().hour
        if 9 <= hour <= 11:
            predictions.append(("morning_review", 0.6))
        elif 14 <= hour <= 16:
            predictions.append(("afternoon_work", 0.6))
        elif 17 <= hour <= 18:
            predictions.append(("end_of_day_summary", 0.5))

        # Sort and deduplicate
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions[:5]

    def get_twin_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of the digital twin for a user.

        Args:
            user_id: User identifier

        Returns:
            Summary dictionary
        """
        profile = self.get_or_create_profile(user_id)

        summary = {
            "user_id": user_id,
            "profile": {
                "cognitive_styles": {
                    k.value: v for k, v in profile.cognitive_styles.items()
                },
                "primary_style": profile.primary_cognitive_style.value if profile.primary_cognitive_style else None,
                "communication_style": profile.communication_style.value,
                "time_orientation": profile.time_orientation.value,
                "risk_tolerance": profile.risk_tolerance.value,
                "information_processing": profile.information_processing.value,
                "confidence": profile.profile_confidence,
                "observations": profile.observations_count,
            },
            "patterns": {
                "decision_patterns": len(self.decision_patterns.get(user_id, [])),
                "reasoning_preferences": len(self.reasoning_preferences.get(user_id, [])),
            },
            "anticipation": {
                "anticipated_needs": len(self.anticipated_needs.get(user_id, [])),
                "interaction_history": len(self.interaction_history.get(user_id, [])),
            },
            "last_updated": profile.updated_at.isoformat(),
        }

        return summary

    # Private methods

    def _update_profile_from_signal(
        self,
        user_id: str,
        signal: InteractionSignal
    ) -> None:
        """Update cognitive profile based on interaction signal."""
        profile = self.get_or_create_profile(user_id)

        # Detect patterns from signal content
        detected = self.pattern_detector.detect_from_text(signal.content)

        # Update cognitive styles with exponential moving average
        alpha = 0.1  # Learning rate
        for style, score in detected["cognitive_styles"].items():
            current = profile.cognitive_styles.get(style, 0.5)
            profile.cognitive_styles[style] = current * (1 - alpha) + score * alpha

        # Update communication style if detected
        if detected["communication_style"]:
            profile.communication_style = detected["communication_style"]

        # Update time orientation if detected
        if detected["time_orientation"]:
            profile.time_orientation = detected["time_orientation"]

        # Update counts and confidence
        profile.observations_count += 1
        profile.profile_confidence = min(
            0.95,
            profile.observations_count / (profile.observations_count + self.min_observations_for_confidence)
        )
        profile.updated_at = datetime.utcnow()

        # Handle corrections specially
        if signal.signal_type == "correction":
            self._handle_correction(user_id, signal)

    def _detect_new_patterns(self, user_id: str) -> None:
        """Detect new decision patterns from interaction history."""
        if user_id not in self.interaction_history:
            return

        history = self.interaction_history[user_id]
        if len(history) < 5:
            return

        # Group interactions by task type
        by_task: Dict[str, List[InteractionSignal]] = {}
        for signal in history[-50:]:  # Last 50 interactions
            if signal.task_type not in by_task:
                by_task[signal.task_type] = []
            by_task[signal.task_type].append(signal)

        # Look for patterns in each task type
        for task_type, signals in by_task.items():
            if len(signals) < 3:
                continue

            # Extract common questions
            questions = [s.content for s in signals if s.signal_type == "question"]

            # Extract common entities
            all_entities: Set[str] = set()
            for s in signals:
                all_entities.update(s.entities_involved)

            # Create or update pattern
            if user_id not in self.decision_patterns:
                self.decision_patterns[user_id] = []

            existing = next(
                (p for p in self.decision_patterns[user_id] if p.pattern_type == task_type),
                None
            )

            if existing:
                existing.times_observed += 1
                existing.last_observed = datetime.utcnow()
                existing.typical_questions = list(set(existing.typical_questions + questions[:5]))
            else:
                pattern = DecisionPattern(
                    id=str(uuid4()),
                    user_id=user_id,
                    pattern_type=task_type,
                    context_tags=[task_type],
                    decision_factors=[],
                    typical_questions=questions[:5],
                    information_needs=[],
                    decision_timeline="moderate",
                )
                self.decision_patterns[user_id].append(pattern)

    def _update_anticipated_needs(
        self,
        user_id: str,
        signal: InteractionSignal
    ) -> None:
        """Update anticipated needs based on interaction."""
        if user_id not in self.anticipated_needs:
            self.anticipated_needs[user_id] = []

        # Check if any anticipated need was fulfilled
        for need in self.anticipated_needs[user_id]:
            if self._signal_fulfills_need(signal, need):
                need.times_fulfilled += 1
                need.accuracy_rate = need.times_fulfilled / max(1, need.times_anticipated)

        # Generate new anticipated needs based on pattern
        if signal.signal_type in ["question", "command"]:
            # Anticipate follow-up needs
            anticipated = AnticipatedNeed(
                id=str(uuid4()),
                user_id=user_id,
                need_type="follow_up",
                description=f"Follow-up to {signal.task_type}",
                context_triggers=[signal.topic] + signal.entities_involved,
                time_triggers=["within_hour"],
                valid_until=datetime.utcnow() + timedelta(hours=1),
            )
            self.anticipated_needs[user_id].append(anticipated)

    def _handle_correction(
        self,
        user_id: str,
        signal: InteractionSignal
    ) -> None:
        """Handle a correction signal to improve the twin."""
        profile = self.profiles[user_id]

        # Corrections indicate mismatch - reduce confidence
        profile.profile_confidence *= 0.95

        # Try to learn from correction
        correction_text = signal.correction_made or signal.content

        # Check if it's a style correction
        style_indicators = ["prefer", "rather", "like", "want"]
        if any(ind in correction_text.lower() for ind in style_indicators):
            # Update communication preferences
            detected = self.pattern_detector.detect_from_text(correction_text)
            if detected["communication_style"]:
                profile.communication_style = detected["communication_style"]

    def _detect_sentiment(self, text: str) -> str:
        """Detect sentiment from text."""
        text_lower = text.lower()

        positive = ["thanks", "great", "good", "perfect", "excellent", "helpful"]
        negative = ["wrong", "bad", "incorrect", "no", "don't", "not what"]

        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency from text."""
        text_lower = text.lower()

        urgent = ["urgent", "asap", "immediately", "now", "quickly", "emergency"]
        if any(w in text_lower for w in urgent):
            return "high"

        moderate = ["soon", "today", "when you can"]
        if any(w in text_lower for w in moderate):
            return "medium"

        return "low"

    def _generate_recommendations(
        self,
        profile: CognitiveProfile,
        task_type: str
    ) -> List[str]:
        """Generate recommendations based on profile."""
        recommendations = []

        # Based on cognitive style
        primary = profile.primary_cognitive_style
        if primary == CognitiveStyle.ANALYTICAL:
            recommendations.append("Include data and metrics in responses")
            recommendations.append("Provide evidence for recommendations")
        elif primary == CognitiveStyle.INTUITIVE:
            recommendations.append("Lead with key insights before details")
            recommendations.append("Use pattern-based explanations")
        elif primary == CognitiveStyle.DIRECTIVE:
            recommendations.append("Lead with action items")
            recommendations.append("Keep responses concise")
        elif primary == CognitiveStyle.CONCEPTUAL:
            recommendations.append("Frame in terms of bigger picture")
            recommendations.append("Explore creative alternatives")
        elif primary == CognitiveStyle.BEHAVIORAL:
            recommendations.append("Consider stakeholder perspectives")
            recommendations.append("Emphasize collaborative aspects")

        # Based on communication style
        if profile.communication_style == CommunicationStyle.DIRECT:
            recommendations.append("Use bullet points")
        elif profile.communication_style == CommunicationStyle.DETAILED:
            recommendations.append("Provide comprehensive explanations")

        return recommendations[:5]

    def _generate_style_based_suggestions(
        self,
        profile: CognitiveProfile,
        context: Dict[str, Any]
    ) -> List[ProactiveSuggestion]:
        """Generate suggestions based on cognitive style."""
        suggestions = []

        primary = profile.primary_cognitive_style

        if primary == CognitiveStyle.ANALYTICAL and context.get("has_data"):
            suggestions.append(ProactiveSuggestion(
                id=str(uuid4()),
                user_id=profile.user_id,
                suggestion_type="analysis",
                content="I can provide a statistical breakdown of this data",
                reasoning="You typically appreciate data-driven analysis",
                confidence=profile.profile_confidence,
                relevance_score=0.7,
                urgency="low",
                triggered_by=["analytical_style", "has_data"],
                context_match_score=0.8,
            ))

        if primary == CognitiveStyle.CONCEPTUAL and context.get("task_type") == "planning":
            suggestions.append(ProactiveSuggestion(
                id=str(uuid4()),
                user_id=profile.user_id,
                suggestion_type="insight",
                content="Would you like me to explore alternative approaches?",
                reasoning="You often value creative exploration",
                confidence=profile.profile_confidence,
                relevance_score=0.7,
                urgency="low",
                triggered_by=["conceptual_style", "planning"],
                context_match_score=0.75,
            ))

        return suggestions

    def _context_matches_triggers(
        self,
        context: Dict[str, Any],
        triggers: List[str]
    ) -> bool:
        """Check if current context matches triggers."""
        context_values = set()

        # Flatten context values
        for key, value in context.items():
            if isinstance(value, str):
                context_values.add(value.lower())
            elif isinstance(value, list):
                context_values.update(v.lower() for v in value if isinstance(v, str))

        # Check if any trigger matches
        trigger_set = set(t.lower() for t in triggers)
        return bool(context_values & trigger_set)

    def _context_matches_pattern(
        self,
        context: Dict[str, Any],
        pattern: DecisionPattern
    ) -> bool:
        """Check if context matches a decision pattern."""
        task_type = context.get("task_type", "")
        topic = context.get("topic", "")

        return (
            task_type in pattern.context_tags or
            topic in pattern.context_tags
        )

    def _signal_fulfills_need(
        self,
        signal: InteractionSignal,
        need: AnticipatedNeed
    ) -> bool:
        """Check if a signal fulfills an anticipated need."""
        if signal.task_type == need.need_type:
            return True

        if any(trigger in signal.topic for trigger in need.context_triggers):
            return True

        return False

    def _make_concise(self, text: str) -> str:
        """Make text more concise."""
        # Simple implementation - in production use NLP
        sentences = text.split(". ")
        if len(sentences) > 3:
            # Keep first and last, skip middle
            return ". ".join([sentences[0]] + sentences[-2:])
        return text

    def _format_as_list(self, text: str) -> str:
        """Format text as a bulleted list."""
        sentences = text.split(". ")
        if len(sentences) > 1:
            return "\n".join(f"• {s.strip()}" for s in sentences if s.strip())
        return text
