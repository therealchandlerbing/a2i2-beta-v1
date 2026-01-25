"""
Arcus Knowledge Repository - Voice Orchestrator
Phase 4: Voice-Optimized Skill Routing

Provides ultra-low latency skill orchestration for voice interactions,
targeting <250ms response times to match PersonaPlex capabilities.

Key Features:
- Fast-path routing for voice queries
- Streaming partial results
- Interrupt handling with context preservation
- Voice-Native Knowledge Graph (VNKG) integration
- Proactive response preparation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, AsyncIterator
from uuid import uuid4
import asyncio
import time

from common import STOPWORDS


# =============================================================================
# CONSTANTS
# =============================================================================

# Latency targets (milliseconds)
TARGET_FIRST_RESPONSE_MS = 250        # PersonaPlex target for first audible response
TARGET_COMPLETE_RESPONSE_MS = 2000    # Target for full response
DEFAULT_STREAMING_CHUNK_MS = 100      # Default chunk interval for streaming

# VNKG retrieval settings
DEFAULT_MAX_VNKG_RESULTS = 3          # Maximum VNKG entries to return
DEFAULT_VNKG_LATENCY_BUDGET_MS = 100  # Time budget for VNKG retrieval

# Confidence thresholds
MIN_CONFIDENCE_IMMEDIATE = 0.7        # Minimum confidence for immediate response
MIN_CONFIDENCE_STREAMING = 0.5        # Minimum confidence for streaming response
MIN_VNKG_BREVITY_SCORE = 0.7          # Minimum brevity score for VNKG voice response

# Proactive preparation
DEFAULT_PREP_CACHE_TTL_SECONDS = 300  # 5 minute TTL for prepared responses
DEFAULT_ANTICIPATION_WINDOW_MS = 500  # Time window for follow-up anticipation

# Intent classification confidence scores
CONFIDENCE_QUICK_ANSWER = 0.9
CONFIDENCE_RECALL = 0.85
CONFIDENCE_COMMAND = 0.8
CONFIDENCE_COMPLEX_QUERY = 0.75
CONFIDENCE_CLARIFICATION = 0.6
CONFIDENCE_CONVERSATION = 0.5

# Voice-optimized brevity thresholds
BREVITY_IDEAL_MIN_WORDS = 15
BREVITY_IDEAL_MAX_WORDS = 30

# Skill routing thresholds
MIN_SKILL_PRIORITY_SCORE = 0.3        # Minimum priority to consider a skill
HIGH_QUALITY_PRIORITY_SCORE = 0.8     # Priority indicating high-quality response
MIN_RESPONSE_LENGTH_CHARS = 20        # Minimum response length to consider complete


class VoiceProvider(Enum):
    """Available voice providers with their characteristics."""
    PERSONAPLEX = "personaplex"      # Primary: <250ms latency
    GEMINI_LIVE = "gemini_live"      # Reasoning + voice
    GEMINI_TTS = "gemini_tts"        # Text-to-speech fallback


class ResponseMode(Enum):
    """How to deliver voice responses."""
    IMMEDIATE = "immediate"          # Single complete response
    STREAMING = "streaming"          # Stream partial results
    PROGRESSIVE = "progressive"      # Increasingly detailed responses
    INTERRUPTIBLE = "interruptible"  # Can be cut off by user


class VoiceIntent(Enum):
    """Classified intent types for voice queries."""
    QUICK_ANSWER = "quick_answer"    # Simple fact retrieval
    RECALL = "recall"                # Memory retrieval
    COMMAND = "command"              # Action request
    CLARIFICATION = "clarification"  # Need more info
    CONVERSATION = "conversation"    # Multi-turn dialogue
    COMPLEX_QUERY = "complex_query"  # Needs background processing


@dataclass
class VoiceConfig:
    """Configuration for voice-optimized orchestration."""

    # Latency targets (ms)
    max_first_response_ms: int = TARGET_FIRST_RESPONSE_MS
    max_complete_response_ms: int = TARGET_COMPLETE_RESPONSE_MS
    streaming_chunk_ms: int = DEFAULT_STREAMING_CHUNK_MS

    # Provider preferences
    primary_provider: VoiceProvider = VoiceProvider.PERSONAPLEX
    fallback_provider: VoiceProvider = VoiceProvider.GEMINI_LIVE

    # Response behavior
    default_response_mode: ResponseMode = ResponseMode.STREAMING
    allow_interrupt: bool = True
    interrupt_saves_context: bool = True

    # Skill routing weights for voice (0.0 = avoid, 1.0 = prefer)
    voice_skill_weights: Dict[str, float] = field(default_factory=lambda: {
        "recall": 1.0,           # Fast lookup - perfect for voice
        "quick_answer": 1.0,     # Direct response
        "entity_lookup": 0.9,    # Fast entity retrieval
        "relationship_query": 0.8,  # Graph queries
        "learn": 0.6,            # Can capture but slower
        "relate": 0.5,           # Moderate complexity
        "reflect": 0.2,          # Too slow for real-time
        "deep_research": 0.1,    # Background only
        "orchestrate": 0.3,      # Complex coordination
    })

    # Proactive features
    enable_proactive_prep: bool = True
    prep_cache_ttl_seconds: int = DEFAULT_PREP_CACHE_TTL_SECONDS
    anticipation_window_ms: int = DEFAULT_ANTICIPATION_WINDOW_MS

    # Quality thresholds
    min_confidence_for_immediate: float = MIN_CONFIDENCE_IMMEDIATE
    min_confidence_for_streaming: float = MIN_CONFIDENCE_STREAMING


@dataclass
class VoiceQuery:
    """Incoming voice query with metadata."""
    id: str
    text: str
    user_id: str
    session_id: str
    timestamp: datetime

    # Voice-specific metadata
    audio_duration_ms: Optional[int] = None
    speech_confidence: float = 1.0
    detected_language: str = "en"

    # Context
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    active_entities: List[str] = field(default_factory=list)
    current_topic: Optional[str] = None

    # Preferences
    response_mode: Optional[ResponseMode] = None
    max_response_length: Optional[int] = None  # Max words


@dataclass
class VoiceResponseChunk:
    """A chunk of voice response for streaming."""
    chunk_id: str
    sequence: int
    text: str
    is_final: bool

    # Timing
    generated_at: datetime = field(default_factory=datetime.utcnow)
    latency_ms: Optional[int] = None

    # Metadata
    confidence: float = 1.0
    source_skill: Optional[str] = None
    can_interrupt_after: bool = True


@dataclass
class VoiceResponse:
    """Complete voice response with all chunks and metadata."""
    id: str
    query_id: str
    chunks: List[VoiceResponseChunk]

    # Timing metrics
    first_chunk_latency_ms: int
    total_latency_ms: int

    # Response info
    provider_used: VoiceProvider
    response_mode: ResponseMode
    intent_detected: VoiceIntent

    # Quality metrics
    overall_confidence: float
    skills_used: List[str]
    context_tokens_used: int

    # Interruption handling
    was_interrupted: bool = False
    interrupt_point: Optional[int] = None
    saved_context: Optional[Dict[str, Any]] = None

    # Follow-up preparation
    anticipated_follow_ups: List[str] = field(default_factory=list)
    prepared_responses: Dict[str, str] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        """Get the complete response text."""
        return " ".join(chunk.text for chunk in self.chunks if chunk.text)


@dataclass
class VNKGEntry:
    """Voice-Native Knowledge Graph entry optimized for spoken retrieval."""
    id: str
    content: str

    # Voice optimization
    spoken_form: str                      # How to say it naturally
    phonetic_hints: List[str]             # Pronunciation aids
    brevity_score: float                  # 0-1, higher = more concise

    # Retrieval metadata
    keywords: List[str]
    entity_refs: List[str]
    topic_tags: List[str]

    # Usage patterns
    voice_retrieval_count: int = 0
    avg_retrieval_latency_ms: float = 0.0
    user_satisfaction_score: float = 0.0

    # Freshness
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = None


@dataclass
class ProactivePreparation:
    """Pre-computed response for anticipated queries."""
    id: str
    trigger_patterns: List[str]          # Patterns that trigger this response
    prepared_response: str
    confidence: float

    # Context requirements
    required_entities: List[str]
    required_topic: Optional[str]

    # Validity
    created_at: datetime
    expires_at: datetime
    used_count: int = 0


class IntentClassifier:
    """Classify voice query intent for routing decisions."""

    # Quick answer patterns (can be answered in <250ms)
    QUICK_PATTERNS = [
        "what is", "who is", "when is", "where is",
        "what's", "who's", "when's", "where's",
        "tell me about", "remind me",
        "what do you know about", "what's the status",
    ]

    # Recall patterns (memory retrieval)
    RECALL_PATTERNS = [
        "what did", "when did", "how did",
        "last time", "previously", "before",
        "history of", "remember when",
    ]

    # Command patterns (action requests)
    COMMAND_PATTERNS = [
        "please", "can you", "could you",
        "schedule", "send", "create", "update",
        "add", "remove", "delete", "change",
    ]

    # Complex query patterns (need background processing)
    COMPLEX_PATTERNS = [
        "analyze", "compare", "summarize",
        "research", "investigate", "find all",
        "comprehensive", "detailed",
    ]

    def classify(self, query: VoiceQuery) -> Tuple[VoiceIntent, float]:
        """
        Classify query intent and return confidence.

        Returns:
            Tuple of (intent, confidence)
        """
        text = query.text.lower().strip()

        # Check patterns in order of priority
        for pattern in self.QUICK_PATTERNS:
            if text.startswith(pattern) or f" {pattern}" in text:
                return VoiceIntent.QUICK_ANSWER, CONFIDENCE_QUICK_ANSWER

        for pattern in self.RECALL_PATTERNS:
            if pattern in text:
                return VoiceIntent.RECALL, CONFIDENCE_RECALL

        for pattern in self.COMMAND_PATTERNS:
            if pattern in text:
                return VoiceIntent.COMMAND, CONFIDENCE_COMMAND

        for pattern in self.COMPLEX_PATTERNS:
            if pattern in text:
                return VoiceIntent.COMPLEX_QUERY, CONFIDENCE_COMPLEX_QUERY

        # Check for clarification (short, question-like)
        if len(text.split()) < 5 and text.endswith("?"):
            return VoiceIntent.CLARIFICATION, CONFIDENCE_CLARIFICATION

        # Default to conversation
        return VoiceIntent.CONVERSATION, CONFIDENCE_CONVERSATION


class VoiceSkillRouter:
    """Route voice queries to optimal skills for fast response."""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.intent_classifier = IntentClassifier()

    def select_skills(
        self,
        query: VoiceQuery,
        intent: VoiceIntent,
        available_skills: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Select and prioritize skills for a voice query.

        Returns:
            List of (skill_name, priority_score) sorted by priority
        """
        skill_scores = []

        for skill in available_skills:
            base_weight = self.config.voice_skill_weights.get(skill, 0.5)

            # Adjust based on intent
            intent_multiplier = self._get_intent_multiplier(skill, intent)

            # Adjust based on context
            context_multiplier = self._get_context_multiplier(skill, query)

            final_score = base_weight * intent_multiplier * context_multiplier
            skill_scores.append((skill, final_score))

        # Sort by score descending
        skill_scores.sort(key=lambda x: x[1], reverse=True)

        return skill_scores

    def _get_intent_multiplier(self, skill: str, intent: VoiceIntent) -> float:
        """Get multiplier based on intent-skill match."""
        intent_skill_affinities = {
            VoiceIntent.QUICK_ANSWER: {
                "recall": 1.5, "entity_lookup": 1.3, "quick_answer": 1.5
            },
            VoiceIntent.RECALL: {
                "recall": 1.5, "entity_lookup": 1.2, "relationship_query": 1.3
            },
            VoiceIntent.COMMAND: {
                "learn": 1.3, "relate": 1.2, "orchestrate": 1.4
            },
            VoiceIntent.COMPLEX_QUERY: {
                "deep_research": 1.5, "reflect": 1.3, "orchestrate": 1.4
            },
            VoiceIntent.CONVERSATION: {
                "recall": 1.1, "quick_answer": 1.1
            },
            VoiceIntent.CLARIFICATION: {
                "recall": 1.2, "entity_lookup": 1.3
            },
        }

        return intent_skill_affinities.get(intent, {}).get(skill, 1.0)

    def _get_context_multiplier(self, skill: str, query: VoiceQuery) -> float:
        """Get multiplier based on query context."""
        multiplier = 1.0

        # Boost entity-related skills if entities are active
        if query.active_entities and skill in ["entity_lookup", "relationship_query"]:
            multiplier *= 1.2

        # Boost recall if there's conversation history
        if query.conversation_history and skill == "recall":
            multiplier *= 1.1

        # Boost topic-related skills if topic is set
        if query.current_topic and skill in ["recall", "quick_answer"]:
            multiplier *= 1.15

        return multiplier


class VNKGManager:
    """Manage Voice-Native Knowledge Graph entries."""

    def __init__(self):
        self.entries: Dict[str, VNKGEntry] = {}
        self.keyword_index: Dict[str, List[str]] = {}  # keyword -> entry_ids
        self.entity_index: Dict[str, List[str]] = {}   # entity -> entry_ids

    def add_entry(self, entry: VNKGEntry) -> None:
        """Add or update a VNKG entry."""
        self.entries[entry.id] = entry

        # Update keyword index
        for keyword in entry.keywords:
            if keyword not in self.keyword_index:
                self.keyword_index[keyword] = []
            if entry.id not in self.keyword_index[keyword]:
                self.keyword_index[keyword].append(entry.id)

        # Update entity index
        for entity in entry.entity_refs:
            if entity not in self.entity_index:
                self.entity_index[entity] = []
            if entry.id not in self.entity_index[entity]:
                self.entity_index[entity].append(entry.id)

    def optimize_for_voice(self, content: str, context: Optional[Dict] = None) -> VNKGEntry:
        """
        Convert content to voice-optimized format.

        Args:
            content: Raw content to optimize
            context: Optional context for optimization

        Returns:
            Voice-optimized VNKG entry
        """
        # Generate spoken form (natural speech)
        spoken_form = self._generate_spoken_form(content)

        # Calculate brevity score
        brevity_score = self._calculate_brevity(content, spoken_form)

        # Extract keywords and entities
        keywords = self._extract_keywords(content)
        entities = self._extract_entities(content, context)

        # Generate phonetic hints for complex terms
        phonetic_hints = self._generate_phonetic_hints(content)

        entry = VNKGEntry(
            id=str(uuid4()),
            content=content,
            spoken_form=spoken_form,
            phonetic_hints=phonetic_hints,
            brevity_score=brevity_score,
            keywords=keywords,
            entity_refs=entities,
            topic_tags=context.get("topics", []) if context else [],
        )

        self.add_entry(entry)
        return entry

    def retrieve_for_voice(
        self,
        query: str,
        entities: Optional[List[str]] = None,
        max_results: int = DEFAULT_MAX_VNKG_RESULTS,
        max_latency_ms: int = DEFAULT_VNKG_LATENCY_BUDGET_MS
    ) -> List[VNKGEntry]:
        """
        Retrieve VNKG entries optimized for voice response.

        Args:
            query: Search query
            entities: Optional entity filter
            max_results: Maximum results to return
            max_latency_ms: Maximum retrieval time

        Returns:
            List of matching VNKG entries
        """
        start_time = time.time()
        results = []

        # Extract query keywords
        query_keywords = set(query.lower().split())

        # Score entries by relevance
        scored_entries = []
        for entry_id, entry in self.entries.items():
            # Check TTL
            if entry.ttl_seconds:
                age = (datetime.utcnow() - entry.created_at).total_seconds()
                if age > entry.ttl_seconds:
                    continue

            # Calculate relevance score
            score = 0.0

            # Keyword match
            entry_keywords = set(entry.keywords)
            keyword_overlap = len(query_keywords & entry_keywords)
            score += keyword_overlap * 0.3

            # Entity match
            if entities:
                entity_overlap = len(set(entities) & set(entry.entity_refs))
                score += entity_overlap * 0.4

            # Brevity bonus for voice
            score += entry.brevity_score * 0.2

            # Recency bonus
            age_hours = (datetime.utcnow() - entry.last_accessed).total_seconds() / 3600
            recency_score = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
            score += recency_score * 0.1

            if score > 0:
                scored_entries.append((entry, score))

            # Check time budget
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > max_latency_ms * 0.8:  # Leave buffer
                break

        # Sort by score and return top results
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        results = [entry for entry, _ in scored_entries[:max_results]]

        # Update access times
        for entry in results:
            entry.last_accessed = datetime.utcnow()
            entry.voice_retrieval_count += 1

        return results

    def _generate_spoken_form(self, content: str) -> str:
        """Convert content to natural spoken form."""
        spoken = content

        # Replace abbreviations with spoken forms
        abbreviations = {
            "e.g.": "for example",
            "i.e.": "that is",
            "etc.": "and so on",
            "vs.": "versus",
            "w/": "with",
            "w/o": "without",
            "&": "and",
            "%": "percent",
            "$": "dollars",
        }

        for abbrev, spoken_form in abbreviations.items():
            spoken = spoken.replace(abbrev, spoken_form)

        # Remove markdown formatting
        import re
        spoken = re.sub(r'\*\*([^*]+)\*\*', r'\1', spoken)  # Bold
        spoken = re.sub(r'\*([^*]+)\*', r'\1', spoken)      # Italic
        spoken = re.sub(r'`([^`]+)`', r'\1', spoken)        # Code
        spoken = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', spoken)  # Links

        # Convert lists to spoken form
        spoken = re.sub(r'^\s*[-*]\s+', 'Next, ', spoken, flags=re.MULTILINE)
        spoken = re.sub(r'^\s*\d+\.\s+', 'Then, ', spoken, flags=re.MULTILINE)

        return spoken.strip()

    def _calculate_brevity(self, original: str, spoken: str) -> float:
        """Calculate brevity score (0-1, higher = more concise)."""
        spoken_words = len(spoken.split())

        # Ideal length for voice
        if spoken_words < BREVITY_IDEAL_MIN_WORDS:
            return 0.8  # Too short might lack context
        elif spoken_words <= BREVITY_IDEAL_MAX_WORDS:
            return 1.0  # Ideal range
        elif spoken_words <= BREVITY_IDEAL_MAX_WORDS * 2:
            return 0.7  # Moderately long
        else:
            return 0.4  # Too long for voice

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction (in production, use NLP)
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())

        # Remove stopwords
        keywords = [w for w in words if w not in STOPWORDS]

        # Return unique keywords, preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:10]  # Limit to top 10

    def _extract_entities(
        self,
        content: str,
        context: Optional[Dict] = None
    ) -> List[str]:
        """Extract entity references from content."""
        entities = []

        # Check context for known entities
        if context and "known_entities" in context:
            for entity in context["known_entities"]:
                if entity.lower() in content.lower():
                    entities.append(entity)

        # Simple proper noun detection (capitalized words)
        import re
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        entities.extend(proper_nouns)

        return list(set(entities))

    def _generate_phonetic_hints(self, content: str) -> List[str]:
        """Generate phonetic hints for complex terms."""
        hints = []

        # In production, use a pronunciation dictionary
        # For now, identify potentially complex terms
        import re
        complex_patterns = [
            r'\b[A-Z]{2,}\b',           # Acronyms
            r'\b\w*[0-9]+\w*\b',         # Words with numbers
            r'\b\w+(?:tion|sion)\b',     # -tion/-sion words
        ]

        for pattern in complex_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Placeholder hint generation
                hints.append(f"{match}: spell out")

        return hints[:5]  # Limit hints


class ProactiveEngine:
    """Prepare responses for anticipated queries."""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.preparations: Dict[str, ProactivePreparation] = {}
        self.pattern_hits: Dict[str, int] = {}  # Track pattern usage

    def anticipate_follow_ups(
        self,
        query: VoiceQuery,
        response: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Anticipate likely follow-up queries.

        Args:
            query: Original query
            response: Response given
            context: Current context

        Returns:
            List of anticipated follow-up queries
        """
        follow_ups = []

        # Common follow-up patterns
        if "meeting" in query.text.lower() or "meeting" in response.lower():
            follow_ups.extend([
                "When is it?",
                "Who's attending?",
                "What's the agenda?",
            ])

        if any(word in response.lower() for word in ["project", "task", "deadline"]):
            follow_ups.extend([
                "What's the status?",
                "When is it due?",
                "Who's responsible?",
            ])

        # Entity-based follow-ups
        for entity in context.get("mentioned_entities", []):
            follow_ups.append(f"Tell me more about {entity}")
            follow_ups.append(f"What's {entity}'s role?")

        # Topic continuation
        if context.get("current_topic"):
            follow_ups.append(f"What else about {context['current_topic']}?")

        return follow_ups[:5]  # Limit to top 5

    def prepare_response(
        self,
        trigger_patterns: List[str],
        response: str,
        context: Dict[str, Any],
        ttl_seconds: Optional[int] = None
    ) -> ProactivePreparation:
        """
        Prepare a response for anticipated queries.

        Args:
            trigger_patterns: Patterns that trigger this response
            response: Pre-computed response
            context: Required context
            ttl_seconds: Time-to-live for the preparation

        Returns:
            Proactive preparation record
        """
        ttl = ttl_seconds or self.config.prep_cache_ttl_seconds

        prep = ProactivePreparation(
            id=str(uuid4()),
            trigger_patterns=trigger_patterns,
            prepared_response=response,
            confidence=0.8,  # Default confidence
            required_entities=context.get("required_entities", []),
            required_topic=context.get("required_topic"),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl),
        )

        # Index by patterns
        for pattern in trigger_patterns:
            self.preparations[pattern.lower()] = prep

        return prep

    def get_prepared_response(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[ProactivePreparation]:
        """
        Check if we have a prepared response for this query.

        Args:
            query: Incoming query
            context: Current context

        Returns:
            Prepared response if available and valid
        """
        query_lower = query.lower()

        for pattern, prep in self.preparations.items():
            # Check expiration
            if datetime.utcnow() > prep.expires_at:
                continue

            # Check pattern match
            if pattern in query_lower or query_lower in pattern:
                # Verify context requirements
                if prep.required_entities:
                    active_entities = set(context.get("active_entities", []))
                    if not set(prep.required_entities) <= active_entities:
                        continue

                if prep.required_topic:
                    if context.get("current_topic") != prep.required_topic:
                        continue

                # Track usage
                prep.used_count += 1
                self.pattern_hits[pattern] = self.pattern_hits.get(pattern, 0) + 1

                return prep

        return None


class VoiceOrchestrator:
    """
    Main voice orchestration engine.

    Coordinates voice queries through the fastest available path
    while maintaining context and quality.
    """

    def __init__(
        self,
        config: Optional[VoiceConfig] = None,
        skill_executor: Optional[Callable] = None
    ):
        self.config = config or VoiceConfig()
        self.skill_executor = skill_executor

        self.intent_classifier = IntentClassifier()
        self.skill_router = VoiceSkillRouter(self.config)
        self.vnkg = VNKGManager()
        self.proactive = ProactiveEngine(self.config)

        # Tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.latency_stats: Dict[str, List[float]] = {}

    async def process_query(
        self,
        query: VoiceQuery,
        available_skills: Optional[List[str]] = None
    ) -> VoiceResponse:
        """
        Process a voice query and return response.

        Args:
            query: Incoming voice query
            available_skills: Skills available for routing

        Returns:
            Complete voice response
        """
        start_time = time.time()
        chunks: List[VoiceResponseChunk] = []

        # Default available skills
        if available_skills is None:
            available_skills = list(self.config.voice_skill_weights.keys())

        # 1. Check for prepared response (fastest path)
        context = self._build_context(query)
        prepared = self.proactive.get_prepared_response(query.text, context)

        if prepared:
            first_latency = int((time.time() - start_time) * 1000)
            chunk = VoiceResponseChunk(
                chunk_id=str(uuid4()),
                sequence=0,
                text=prepared.prepared_response,
                is_final=True,
                latency_ms=first_latency,
                confidence=prepared.confidence,
                source_skill="proactive_cache",
            )
            chunks.append(chunk)

            return self._build_response(
                query, chunks, start_time,
                VoiceProvider.PERSONAPLEX,
                ResponseMode.IMMEDIATE,
                VoiceIntent.QUICK_ANSWER,
                ["proactive_cache"],
            )

        # 2. Classify intent
        intent, intent_confidence = self.intent_classifier.classify(query)

        # 3. Try VNKG fast retrieval for simple queries
        if intent in [VoiceIntent.QUICK_ANSWER, VoiceIntent.RECALL]:
            vnkg_results = self.vnkg.retrieve_for_voice(
                query.text,
                entities=query.active_entities,
                max_latency_ms=DEFAULT_VNKG_LATENCY_BUDGET_MS,
            )

            if vnkg_results and vnkg_results[0].brevity_score >= MIN_VNKG_BREVITY_SCORE:
                first_latency = int((time.time() - start_time) * 1000)
                chunk = VoiceResponseChunk(
                    chunk_id=str(uuid4()),
                    sequence=0,
                    text=vnkg_results[0].spoken_form,
                    is_final=True,
                    latency_ms=first_latency,
                    confidence=0.85,
                    source_skill="vnkg",
                )
                chunks.append(chunk)

                return self._build_response(
                    query, chunks, start_time,
                    VoiceProvider.PERSONAPLEX,
                    ResponseMode.IMMEDIATE,
                    intent,
                    ["vnkg"],
                )

        # 4. Route to skills
        skill_priorities = self.skill_router.select_skills(
            query, intent, available_skills
        )

        # 5. Determine response mode
        response_mode = query.response_mode or self._select_response_mode(
            intent, intent_confidence
        )

        # 6. Execute skills based on response mode
        if response_mode == ResponseMode.STREAMING:
            chunks = await self._execute_streaming(
                query, skill_priorities, context
            )
        elif response_mode == ResponseMode.PROGRESSIVE:
            chunks = await self._execute_progressive(
                query, skill_priorities, context
            )
        else:
            chunks = await self._execute_immediate(
                query, skill_priorities, context
            )

        # 7. Prepare for follow-ups
        if self.config.enable_proactive_prep and chunks:
            full_response = " ".join(c.text for c in chunks)
            follow_ups = self.proactive.anticipate_follow_ups(
                query, full_response, context
            )

            # Prepare responses for likely follow-ups
            for follow_up in follow_ups[:2]:  # Top 2 only
                # In production, actually compute the response
                self.proactive.prepare_response(
                    trigger_patterns=[follow_up.lower()],
                    response=f"[Prepared response for: {follow_up}]",
                    context=context,
                )

        # 8. Build final response
        skills_used = list(set(c.source_skill for c in chunks if c.source_skill))

        return self._build_response(
            query, chunks, start_time,
            self.config.primary_provider,
            response_mode,
            intent,
            skills_used,
        )

    async def process_query_streaming(
        self,
        query: VoiceQuery,
        available_skills: Optional[List[str]] = None
    ) -> AsyncIterator[VoiceResponseChunk]:
        """
        Process query and yield response chunks as they're ready.

        This is the preferred method for voice interfaces.
        """
        start_time = time.time()

        # Default available skills
        if available_skills is None:
            available_skills = list(self.config.voice_skill_weights.keys())

        # Build context
        context = self._build_context(query)

        # Check proactive cache
        prepared = self.proactive.get_prepared_response(query.text, context)
        if prepared:
            latency = int((time.time() - start_time) * 1000)
            yield VoiceResponseChunk(
                chunk_id=str(uuid4()),
                sequence=0,
                text=prepared.prepared_response,
                is_final=True,
                latency_ms=latency,
                confidence=prepared.confidence,
                source_skill="proactive_cache",
            )
            return

        # Classify and route
        intent, _ = self.intent_classifier.classify(query)
        skill_priorities = self.skill_router.select_skills(
            query, intent, available_skills
        )

        # Stream execution
        sequence = 0
        for skill_name, priority in skill_priorities[:3]:  # Top 3 skills
            if priority < MIN_SKILL_PRIORITY_SCORE:  # Skip low-priority skills
                continue

            # Execute skill (placeholder - integrate with real skill executor)
            result = await self._execute_skill(skill_name, query, context)

            if result:
                latency = int((time.time() - start_time) * 1000)
                chunk = VoiceResponseChunk(
                    chunk_id=str(uuid4()),
                    sequence=sequence,
                    text=result,
                    is_final=False,
                    latency_ms=latency,
                    confidence=priority,
                    source_skill=skill_name,
                )
                yield chunk
                sequence += 1

                # Check if we should stop (good enough response)
                if priority >= HIGH_QUALITY_PRIORITY_SCORE and len(result) > MIN_RESPONSE_LENGTH_CHARS:
                    break

        # Send final chunk
        yield VoiceResponseChunk(
            chunk_id=str(uuid4()),
            sequence=sequence,
            text="",
            is_final=True,
            latency_ms=int((time.time() - start_time) * 1000),
        )

    def handle_interrupt(
        self,
        session_id: str,
        interrupt_point: int
    ) -> Dict[str, Any]:
        """
        Handle user interrupt during voice response.

        Args:
            session_id: Session being interrupted
            interrupt_point: Chunk sequence where interrupt occurred

        Returns:
            Saved context for resumption
        """
        if session_id not in self.active_sessions:
            return {}

        session = self.active_sessions[session_id]

        saved_context = {
            "interrupted_at": datetime.utcnow().isoformat(),
            "interrupt_point": interrupt_point,
            "partial_response": session.get("partial_response", ""),
            "pending_skills": session.get("pending_skills", []),
            "query_context": session.get("context", {}),
        }

        if self.config.interrupt_saves_context:
            session["saved_interrupt_context"] = saved_context

        return saved_context

    def resume_from_interrupt(
        self,
        session_id: str,
        continuation_query: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Resume processing from an interrupted point.

        Args:
            session_id: Session to resume
            continuation_query: Optional new query to continue with

        Returns:
            Resumed context or None if not available
        """
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        saved = session.get("saved_interrupt_context")

        if not saved:
            return None

        # Clear saved context after retrieval
        del session["saved_interrupt_context"]

        return saved

    def _build_context(self, query: VoiceQuery) -> Dict[str, Any]:
        """Build context dictionary from query."""
        return {
            "user_id": query.user_id,
            "session_id": query.session_id,
            "active_entities": query.active_entities,
            "current_topic": query.current_topic,
            "conversation_length": len(query.conversation_history),
            "language": query.detected_language,
        }

    def _select_response_mode(
        self,
        intent: VoiceIntent,
        confidence: float
    ) -> ResponseMode:
        """Select optimal response mode based on intent and confidence."""
        # High confidence simple queries -> immediate
        if intent == VoiceIntent.QUICK_ANSWER and confidence >= 0.8:
            return ResponseMode.IMMEDIATE

        # Complex queries -> streaming for perceived speed
        if intent == VoiceIntent.COMPLEX_QUERY:
            return ResponseMode.STREAMING

        # Commands -> interruptible (user might want to cancel)
        if intent == VoiceIntent.COMMAND:
            return ResponseMode.INTERRUPTIBLE

        # Default to streaming for best UX
        return self.config.default_response_mode

    async def _execute_streaming(
        self,
        query: VoiceQuery,
        skill_priorities: List[Tuple[str, float]],
        context: Dict[str, Any]
    ) -> List[VoiceResponseChunk]:
        """Execute skills with streaming response."""
        chunks = []
        sequence = 0
        start_time = time.time()

        for skill_name, priority in skill_priorities[:3]:
            if priority < MIN_SKILL_PRIORITY_SCORE:
                continue

            result = await self._execute_skill(skill_name, query, context)

            if result:
                latency = int((time.time() - start_time) * 1000)
                chunks.append(VoiceResponseChunk(
                    chunk_id=str(uuid4()),
                    sequence=sequence,
                    text=result,
                    is_final=False,
                    latency_ms=latency if sequence == 0 else None,
                    confidence=priority,
                    source_skill=skill_name,
                ))
                sequence += 1

        # Mark last chunk as final
        if chunks:
            chunks[-1].is_final = True

        return chunks

    async def _execute_progressive(
        self,
        query: VoiceQuery,
        skill_priorities: List[Tuple[str, float]],
        context: Dict[str, Any]
    ) -> List[VoiceResponseChunk]:
        """Execute skills with progressively detailed responses."""
        chunks = []
        start_time = time.time()

        # First: Quick summary
        quick_result = await self._execute_skill(
            skill_priorities[0][0], query, context, quick_mode=True
        )

        if quick_result:
            chunks.append(VoiceResponseChunk(
                chunk_id=str(uuid4()),
                sequence=0,
                text=quick_result,
                is_final=False,
                latency_ms=int((time.time() - start_time) * 1000),
                confidence=0.7,
                source_skill=skill_priorities[0][0],
            ))

        # Then: Detailed response
        detailed_result = await self._execute_skill(
            skill_priorities[0][0], query, context, quick_mode=False
        )

        if detailed_result and detailed_result != quick_result:
            chunks.append(VoiceResponseChunk(
                chunk_id=str(uuid4()),
                sequence=1,
                text=detailed_result,
                is_final=True,
                confidence=0.9,
                source_skill=skill_priorities[0][0],
            ))
        elif chunks:
            chunks[-1].is_final = True

        return chunks

    async def _execute_immediate(
        self,
        query: VoiceQuery,
        skill_priorities: List[Tuple[str, float]],
        context: Dict[str, Any]
    ) -> List[VoiceResponseChunk]:
        """Execute skills and return single complete response."""
        start_time = time.time()

        # Execute top skill
        if skill_priorities:
            result = await self._execute_skill(
                skill_priorities[0][0], query, context
            )

            if result:
                return [VoiceResponseChunk(
                    chunk_id=str(uuid4()),
                    sequence=0,
                    text=result,
                    is_final=True,
                    latency_ms=int((time.time() - start_time) * 1000),
                    confidence=skill_priorities[0][1],
                    source_skill=skill_priorities[0][0],
                )]

        return []

    async def _execute_skill(
        self,
        skill_name: str,
        query: VoiceQuery,
        context: Dict[str, Any],
        quick_mode: bool = False
    ) -> Optional[str]:
        """
        Execute a single skill.

        In production, this integrates with the skill orchestrator.
        """
        # Use provided executor if available
        if self.skill_executor:
            try:
                result = await self.skill_executor(
                    skill_name=skill_name,
                    query=query.text,
                    context=context,
                    quick_mode=quick_mode,
                )
                return result
            except Exception:
                pass

        # Placeholder response for testing
        return f"[{skill_name}]: Response to '{query.text[:30]}...'"

    def _build_response(
        self,
        query: VoiceQuery,
        chunks: List[VoiceResponseChunk],
        start_time: float,
        provider: VoiceProvider,
        response_mode: ResponseMode,
        intent: VoiceIntent,
        skills_used: List[str],
    ) -> VoiceResponse:
        """Build complete voice response from chunks."""
        total_latency = int((time.time() - start_time) * 1000)
        first_latency = chunks[0].latency_ms if chunks else total_latency

        # Calculate overall confidence
        if chunks:
            confidences = [c.confidence for c in chunks if c.confidence]
            overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        else:
            overall_confidence = 0.0

        return VoiceResponse(
            id=str(uuid4()),
            query_id=query.id,
            chunks=chunks,
            first_chunk_latency_ms=first_latency,
            total_latency_ms=total_latency,
            provider_used=provider,
            response_mode=response_mode,
            intent_detected=intent,
            overall_confidence=overall_confidence,
            skills_used=skills_used,
            context_tokens_used=0,  # Would be tracked in production
        )

    # Analytics methods

    def get_latency_stats(self) -> Dict[str, Any]:
        """Get latency statistics for voice responses."""
        all_latencies = []
        for latencies in self.latency_stats.values():
            all_latencies.extend(latencies)

        if not all_latencies:
            return {"message": "No latency data available"}

        return {
            "total_requests": len(all_latencies),
            "avg_latency_ms": sum(all_latencies) / len(all_latencies),
            "min_latency_ms": min(all_latencies),
            "max_latency_ms": max(all_latencies),
            "p50_latency_ms": sorted(all_latencies)[len(all_latencies) // 2],
            "p95_latency_ms": sorted(all_latencies)[int(len(all_latencies) * 0.95)],
            "under_250ms_rate": len([l for l in all_latencies if l < 250]) / len(all_latencies),
        }

    def get_intent_distribution(self) -> Dict[str, int]:
        """Get distribution of detected intents."""
        # Would track this in production
        return {}

    def get_vnkg_stats(self) -> Dict[str, Any]:
        """Get VNKG usage statistics."""
        entries = self.vnkg.entries

        if not entries:
            return {"message": "No VNKG entries"}

        return {
            "total_entries": len(entries),
            "avg_brevity_score": sum(e.brevity_score for e in entries.values()) / len(entries),
            "total_retrievals": sum(e.voice_retrieval_count for e in entries.values()),
            "keywords_indexed": len(self.vnkg.keyword_index),
            "entities_indexed": len(self.vnkg.entity_index),
        }
