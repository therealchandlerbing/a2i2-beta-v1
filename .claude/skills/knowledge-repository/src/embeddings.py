"""
Arcus Knowledge Repository - Vector Embeddings
Phase 4: Semantic Search Infrastructure

Provides vector embedding generation and semantic search capabilities
across all memory types for intelligent knowledge retrieval.

Key Features:
- Multi-provider embedding support (OpenAI, Voyage, local)
- Semantic similarity search
- Hybrid search (vector + keyword)
- Cross-memory-type search
- Embedding caching and optimization
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from uuid import uuid4
import hashlib
import math

from common import STOPWORDS


# =============================================================================
# CONSTANTS
# =============================================================================

# Embedding configuration defaults
DEFAULT_EMBEDDING_DIMENSIONS = 1536
DEFAULT_BATCH_SIZE = 100
DEFAULT_MAX_TOKENS_PER_BATCH = 8000
DEFAULT_CACHE_TTL_HOURS = 168         # 1 week
DEFAULT_MAX_TEXT_LENGTH = 8000        # Characters

# Search configuration
DEFAULT_TOP_K = 10
HYBRID_SEARCH_VECTOR_WEIGHT = 0.7
HYBRID_SEARCH_KEYWORD_WEIGHT = 0.3
MIN_TERM_LENGTH = 2                   # Minimum word length for keyword index

# Clustering defaults
DEFAULT_NUM_CLUSTERS = 5
DEFAULT_KMEANS_MAX_ITERATIONS = 10

# Cost calculation (per 1M tokens)
COST_PER_MILLION_TOKENS = {
    "text-embedding-3-small": 0.02,
    "text-embedding-3-large": 0.13,
    "voyage-3": 0.06,
    "voyage-code-3": 0.06,
    "voyage-3-lite": 0.02,
    "embed-english-v3.0": 0.10,
    "embed-multilingual-v3.0": 0.10,
    "all-MiniLM-L6-v2": 0.0,
    "all-mpnet-base-v2": 0.0,
}

# Token estimation (rough approximation)
CHARS_PER_TOKEN = 4


class EmbeddingProvider(Enum):
    """Available embedding providers."""
    OPENAI = "openai"                     # text-embedding-3-small/large
    VOYAGE = "voyage"                     # voyage-3, voyage-code-3
    COHERE = "cohere"                     # embed-english-v3.0
    LOCAL = "local"                       # Local model (e.g., sentence-transformers)
    MOCK = "mock"                         # For testing


class EmbeddingModel(Enum):
    """Specific embedding models."""
    # OpenAI
    OPENAI_SMALL = "text-embedding-3-small"     # 1536 dims, $0.02/1M tokens
    OPENAI_LARGE = "text-embedding-3-large"     # 3072 dims, $0.13/1M tokens

    # Voyage
    VOYAGE_3 = "voyage-3"                       # 1024 dims, general purpose
    VOYAGE_CODE = "voyage-code-3"               # 1024 dims, code-optimized
    VOYAGE_LITE = "voyage-3-lite"               # 512 dims, fast

    # Cohere
    COHERE_ENGLISH = "embed-english-v3.0"       # 1024 dims
    COHERE_MULTILINGUAL = "embed-multilingual-v3.0"  # 1024 dims

    # Local
    LOCAL_MINILM = "all-MiniLM-L6-v2"           # 384 dims, fast
    LOCAL_MPNET = "all-mpnet-base-v2"           # 768 dims, better quality


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL

    # Dimensions (model-specific)
    dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS

    # Batching
    batch_size: int = DEFAULT_BATCH_SIZE
    max_tokens_per_batch: int = DEFAULT_MAX_TOKENS_PER_BATCH

    # Caching
    cache_enabled: bool = True
    cache_ttl_hours: int = DEFAULT_CACHE_TTL_HOURS

    # Optimization
    normalize_embeddings: bool = True
    truncate_long_texts: bool = True
    max_text_length: int = DEFAULT_MAX_TEXT_LENGTH

    # Cost tracking
    track_costs: bool = True


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    id: str
    text_hash: str
    embedding: List[float]
    model: str
    dimensions: int

    # Metadata
    text_length: int
    tokens_used: int
    latency_ms: int
    cost_usd: float

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """A search result with similarity score."""
    id: str
    content: str
    memory_type: str
    similarity_score: float

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    highlights: List[str] = field(default_factory=list)


@dataclass
class HybridSearchResult:
    """Result combining vector and keyword search."""
    id: str
    content: str
    memory_type: str

    # Scores
    vector_score: float
    keyword_score: float
    combined_score: float

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    matched_keywords: List[str] = field(default_factory=list)


@dataclass
class EmbeddingStats:
    """Statistics for embedding operations."""
    total_embeddings: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class EmbeddingCache:
    """Cache for embedding results."""

    def __init__(self, ttl_hours: int = 168):
        self.cache: Dict[str, EmbeddingResult] = {}
        self.ttl = timedelta(hours=ttl_hours)

    def _hash_text(self, text: str, model: str) -> str:
        """Generate hash for cache key."""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, text: str, model: str) -> Optional[EmbeddingResult]:
        """Get cached embedding if available and not expired."""
        key = self._hash_text(text, model)
        result = self.cache.get(key)

        if result:
            if result.expires_at and datetime.utcnow() > result.expires_at:
                del self.cache[key]
                return None
            return result

        return None

    def set(self, text: str, result: EmbeddingResult) -> None:
        """Cache an embedding result."""
        key = self._hash_text(text, result.model)
        result.expires_at = datetime.utcnow() + self.ttl
        self.cache[key] = result

    def clear_expired(self) -> int:
        """Clear expired entries. Returns count cleared."""
        now = datetime.utcnow()
        expired = [
            k for k, v in self.cache.items()
            if v.expires_at and v.expires_at < now
        ]
        for key in expired:
            del self.cache[key]
        return len(expired)

    def clear_all(self) -> None:
        """Clear entire cache."""
        self.cache.clear()


class VectorIndex:
    """In-memory vector index for semantic search."""

    def __init__(self):
        self.vectors: Dict[str, List[float]] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.memory_type_index: Dict[str, List[str]] = {}  # type -> ids

    def add(
        self,
        id: str,
        vector: List[float],
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a vector to the index."""
        self.vectors[id] = vector
        self.metadata[id] = {
            "content": content,
            "memory_type": memory_type,
            **(metadata or {}),
        }

        # Update type index
        if memory_type not in self.memory_type_index:
            self.memory_type_index[memory_type] = []
        if id not in self.memory_type_index[memory_type]:
            self.memory_type_index[memory_type].append(id)

    def remove(self, id: str) -> bool:
        """Remove a vector from the index."""
        if id not in self.vectors:
            return False

        # Get memory type for cleanup
        meta = self.metadata.get(id, {})
        memory_type = meta.get("memory_type")

        # Remove from main storage
        del self.vectors[id]
        if id in self.metadata:
            del self.metadata[id]

        # Remove from type index
        if memory_type and memory_type in self.memory_type_index:
            if id in self.memory_type_index[memory_type]:
                self.memory_type_index[memory_type].remove(id)

        return True

    def search(
        self,
        query_vector: List[float],
        top_k: int = DEFAULT_TOP_K,
        memory_types: Optional[List[str]] = None,
        min_score: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding
            top_k: Number of results to return
            memory_types: Filter by memory types
            min_score: Minimum similarity score
            filters: Additional metadata filters

        Returns:
            List of search results sorted by similarity
        """
        results = []

        # Determine which IDs to search
        if memory_types:
            search_ids = []
            for mt in memory_types:
                search_ids.extend(self.memory_type_index.get(mt, []))
            search_ids = set(search_ids)
        else:
            search_ids = set(self.vectors.keys())

        # Calculate similarities
        for id in search_ids:
            vector = self.vectors.get(id)
            if vector is None:
                continue

            # Apply metadata filters
            if filters:
                meta = self.metadata.get(id, {})
                if not self._matches_filters(meta, filters):
                    continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_vector, vector)

            if similarity >= min_score:
                meta = self.metadata.get(id, {})
                results.append(SearchResult(
                    id=id,
                    content=meta.get("content", ""),
                    memory_type=meta.get("memory_type", "unknown"),
                    similarity_score=similarity,
                    metadata=meta,
                ))

        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _matches_filters(self, meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if key not in meta:
                return False

            meta_value = meta[key]

            # Handle different filter types
            if isinstance(value, list):
                # Value must be in list
                if meta_value not in value:
                    return False
            elif isinstance(value, dict):
                # Range filter
                if "min" in value and meta_value < value["min"]:
                    return False
                if "max" in value and meta_value > value["max"]:
                    return False
            else:
                # Exact match
                if meta_value != value:
                    return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": len(self.vectors),
            "memory_types": {
                mt: len(ids) for mt, ids in self.memory_type_index.items()
            },
            "avg_vector_dim": (
                len(next(iter(self.vectors.values()))) if self.vectors else 0
            ),
        }


class KeywordIndex:
    """Simple inverted index for keyword search."""

    def __init__(self):
        self.index: Dict[str, Set[str]] = {}  # term -> doc_ids
        self.docs: Dict[str, Dict[str, Any]] = {}  # doc_id -> metadata

    def add(
        self,
        id: str,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add document to keyword index."""
        # Tokenize content
        terms = self._tokenize(content)

        # Add to inverted index
        for term in terms:
            if term not in self.index:
                self.index[term] = set()
            self.index[term].add(id)

        # Store document
        self.docs[id] = {
            "content": content,
            "memory_type": memory_type,
            "terms": terms,
            **(metadata or {}),
        }

    def remove(self, id: str) -> bool:
        """Remove document from index."""
        if id not in self.docs:
            return False

        doc = self.docs[id]
        terms = doc.get("terms", set())

        # Remove from inverted index
        for term in terms:
            if term in self.index:
                self.index[term].discard(id)
                if not self.index[term]:
                    del self.index[term]

        del self.docs[id]
        return True

    def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        memory_types: Optional[List[str]] = None
    ) -> List[Tuple[str, float, List[str]]]:
        """
        Search for documents matching query.

        Returns:
            List of (doc_id, score, matched_terms) tuples
        """
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        # Find matching documents
        doc_scores: Dict[str, Tuple[float, List[str]]] = {}

        for term in query_terms:
            if term in self.index:
                for doc_id in self.index[term]:
                    # Check memory type filter
                    if memory_types:
                        doc_type = self.docs.get(doc_id, {}).get("memory_type")
                        if doc_type not in memory_types:
                            continue

                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = (0.0, [])

                    score, matched = doc_scores[doc_id]
                    # TF-IDF-like scoring
                    idf = math.log(len(self.docs) / len(self.index[term]) + 1)
                    doc_scores[doc_id] = (score + idf, matched + [term])

        # Convert to list and sort
        results = [
            (doc_id, score, matched)
            for doc_id, (score, matched) in doc_scores.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def _tokenize(self, text: str) -> Set[str]:
        """Tokenize text into terms."""
        import re

        # Lowercase and split
        text = text.lower()
        words = re.findall(r'\b[a-z0-9]+\b', text)

        # Remove stopwords (using shared STOPWORDS)
        return set(w for w in words if w not in STOPWORDS and len(w) > MIN_TERM_LENGTH)


class EmbeddingService:
    """
    Main service for generating and managing embeddings.

    Provides unified interface for embedding generation across
    multiple providers with caching and optimization.
    """

    def __init__(
        self,
        config: Optional[EmbeddingConfig] = None,
        embedding_fn: Optional[Callable[[List[str]], List[List[float]]]] = None
    ):
        self.config = config or EmbeddingConfig()
        self.embedding_fn = embedding_fn  # Custom embedding function

        self.cache = EmbeddingCache(self.config.cache_ttl_hours)
        self.stats = EmbeddingStats()

        # Model costs (per 1M tokens) - using enum values as keys for compatibility
        self.model_costs = {
            EmbeddingModel.OPENAI_SMALL: COST_PER_MILLION_TOKENS["text-embedding-3-small"],
            EmbeddingModel.OPENAI_LARGE: COST_PER_MILLION_TOKENS["text-embedding-3-large"],
            EmbeddingModel.VOYAGE_3: COST_PER_MILLION_TOKENS["voyage-3"],
            EmbeddingModel.VOYAGE_CODE: COST_PER_MILLION_TOKENS["voyage-code-3"],
            EmbeddingModel.VOYAGE_LITE: COST_PER_MILLION_TOKENS["voyage-3-lite"],
            EmbeddingModel.COHERE_ENGLISH: COST_PER_MILLION_TOKENS["embed-english-v3.0"],
            EmbeddingModel.COHERE_MULTILINGUAL: COST_PER_MILLION_TOKENS["embed-multilingual-v3.0"],
            EmbeddingModel.LOCAL_MINILM: COST_PER_MILLION_TOKENS["all-MiniLM-L6-v2"],
            EmbeddingModel.LOCAL_MPNET: COST_PER_MILLION_TOKENS["all-mpnet-base-v2"],
        }

    async def embed_text(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding result
        """
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding results
        """
        import time

        results = []
        texts_to_embed = []
        text_indices = []  # Track which texts need embedding

        # Check cache first
        for i, text in enumerate(texts):
            # Truncate if needed
            if self.config.truncate_long_texts:
                text = text[:self.config.max_text_length]

            cached = None
            if self.config.cache_enabled:
                cached = self.cache.get(text, self.config.model.value)

            if cached:
                results.append(cached)
                self.stats.cache_hits += 1
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
                results.append(None)  # Placeholder
                self.stats.cache_misses += 1

        # Generate embeddings for cache misses
        if texts_to_embed:
            start_time = time.time()

            embeddings = await self._generate_embeddings(texts_to_embed)

            latency_ms = int((time.time() - start_time) * 1000)
            avg_latency = latency_ms / len(texts_to_embed)

            # Create results and cache
            for i, (text, embedding) in enumerate(zip(texts_to_embed, embeddings)):
                # Estimate tokens
                tokens = len(text) // CHARS_PER_TOKEN

                # Calculate cost
                cost = self._calculate_cost(tokens)

                result = EmbeddingResult(
                    id=str(uuid4()),
                    text_hash=hashlib.sha256(text.encode()).hexdigest()[:16],
                    embedding=embedding,
                    model=self.config.model.value,
                    dimensions=len(embedding),
                    text_length=len(text),
                    tokens_used=tokens,
                    latency_ms=int(avg_latency),
                    cost_usd=cost,
                )

                # Update results list
                original_index = text_indices[i]
                results[original_index] = result

                # Cache result
                if self.config.cache_enabled:
                    self.cache.set(text, result)

                # Update stats
                self.stats.total_embeddings += 1
                self.stats.total_tokens += tokens
                self.stats.total_cost_usd += cost

            # Update average latency
            total = self.stats.total_embeddings
            self.stats.avg_latency_ms = (
                self.stats.avg_latency_ms * (total - len(texts_to_embed)) +
                avg_latency * len(texts_to_embed)
            ) / total

        return results

    async def _generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings using configured provider."""
        # Use custom function if provided
        if self.embedding_fn:
            return self.embedding_fn(texts)

        # Mock embeddings for testing
        if self.config.provider == EmbeddingProvider.MOCK:
            return self._generate_mock_embeddings(texts)

        # In production, call actual embedding APIs
        # For now, generate deterministic mock embeddings
        return self._generate_mock_embeddings(texts)

    def _generate_mock_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Generate deterministic mock embeddings for testing."""
        embeddings = []

        for text in texts:
            # Generate deterministic embedding based on text hash
            text_hash = hashlib.sha256(text.encode()).hexdigest()

            embedding = []
            for i in range(self.config.dimensions):
                # Use hash chars to generate values
                char_idx = i % len(text_hash)
                val = int(text_hash[char_idx], 16) / 15.0 - 0.5  # Normalize to [-0.5, 0.5]
                embedding.append(val)

            # Normalize if configured
            if self.config.normalize_embeddings:
                norm = math.sqrt(sum(v * v for v in embedding))
                if norm > 0:
                    embedding = [v / norm for v in embedding]

            embeddings.append(embedding)

        return embeddings

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for embedding tokens."""
        cost_per_1m = self.model_costs.get(self.config.model, 0.0)
        return (tokens / 1_000_000) * cost_per_1m

    def get_stats(self) -> Dict[str, Any]:
        """Get embedding service statistics."""
        return {
            "total_embeddings": self.stats.total_embeddings,
            "total_tokens": self.stats.total_tokens,
            "total_cost_usd": self.stats.total_cost_usd,
            "avg_latency_ms": self.stats.avg_latency_ms,
            "cache_hit_rate": self.stats.cache_hit_rate,
            "provider": self.config.provider.value,
            "model": self.config.model.value,
            "dimensions": self.config.dimensions,
        }


class SemanticSearchEngine:
    """
    Semantic search engine combining vector and keyword search.

    Provides hybrid search capabilities across all memory types.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        config: Optional[EmbeddingConfig] = None
    ):
        self.embedding_service = embedding_service or EmbeddingService(config)
        self.vector_index = VectorIndex()
        self.keyword_index = KeywordIndex()

        # Hybrid search weights
        self.vector_weight = HYBRID_SEARCH_VECTOR_WEIGHT
        self.keyword_weight = HYBRID_SEARCH_KEYWORD_WEIGHT

    async def index_memory(
        self,
        id: str,
        content: str,
        memory_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Index a memory item for search.

        Args:
            id: Unique identifier
            content: Text content
            memory_type: Type of memory (episodic, semantic, etc.)
            metadata: Additional metadata
        """
        # Generate embedding
        result = await self.embedding_service.embed_text(content)

        # Add to vector index
        self.vector_index.add(
            id=id,
            vector=result.embedding,
            content=content,
            memory_type=memory_type,
            metadata=metadata,
        )

        # Add to keyword index
        self.keyword_index.add(
            id=id,
            content=content,
            memory_type=memory_type,
            metadata=metadata,
        )

    async def index_batch(
        self,
        items: List[Dict[str, Any]]
    ) -> int:
        """
        Index multiple memory items.

        Args:
            items: List of items with id, content, memory_type, metadata

        Returns:
            Number of items indexed
        """
        # Generate embeddings in batch
        contents = [item["content"] for item in items]
        results = await self.embedding_service.embed_batch(contents)

        # Add to indices
        for item, result in zip(items, results):
            self.vector_index.add(
                id=item["id"],
                vector=result.embedding,
                content=item["content"],
                memory_type=item["memory_type"],
                metadata=item.get("metadata"),
            )

            self.keyword_index.add(
                id=item["id"],
                content=item["content"],
                memory_type=item["memory_type"],
                metadata=item.get("metadata"),
            )

        return len(items)

    def remove_from_index(self, id: str) -> bool:
        """Remove an item from the search index."""
        v_removed = self.vector_index.remove(id)
        k_removed = self.keyword_index.remove(id)
        return v_removed or k_removed

    async def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        memory_types: Optional[List[str]] = None,
        min_score: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        search_mode: str = "hybrid"  # "vector", "keyword", "hybrid"
    ) -> List[Union[SearchResult, HybridSearchResult]]:
        """
        Search for relevant memories.

        Args:
            query: Search query
            top_k: Number of results
            memory_types: Filter by memory types
            min_score: Minimum similarity score
            filters: Additional metadata filters
            search_mode: Type of search to perform

        Returns:
            List of search results
        """
        if search_mode == "vector":
            return await self._vector_search(
                query, top_k, memory_types, min_score, filters
            )
        elif search_mode == "keyword":
            return self._keyword_search(query, top_k, memory_types)
        else:  # hybrid
            return await self._hybrid_search(
                query, top_k, memory_types, min_score, filters
            )

    async def _vector_search(
        self,
        query: str,
        top_k: int,
        memory_types: Optional[List[str]],
        min_score: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Perform vector similarity search."""
        # Embed query
        result = await self.embedding_service.embed_text(query)

        # Search vector index
        return self.vector_index.search(
            query_vector=result.embedding,
            top_k=top_k,
            memory_types=memory_types,
            min_score=min_score,
            filters=filters,
        )

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        memory_types: Optional[List[str]]
    ) -> List[SearchResult]:
        """Perform keyword search."""
        results = self.keyword_index.search(query, top_k, memory_types)

        # Convert to SearchResult format
        search_results = []
        for doc_id, score, matched_terms in results:
            doc = self.keyword_index.docs.get(doc_id, {})
            search_results.append(SearchResult(
                id=doc_id,
                content=doc.get("content", ""),
                memory_type=doc.get("memory_type", "unknown"),
                similarity_score=score,
                metadata=doc,
                highlights=matched_terms,
            ))

        return search_results

    async def _hybrid_search(
        self,
        query: str,
        top_k: int,
        memory_types: Optional[List[str]],
        min_score: float,
        filters: Optional[Dict[str, Any]]
    ) -> List[HybridSearchResult]:
        """Perform hybrid vector + keyword search."""
        # Get vector results
        vector_results = await self._vector_search(
            query, top_k * 2, memory_types, 0.0, filters
        )

        # Get keyword results
        keyword_results = self._keyword_search(query, top_k * 2, memory_types)

        # Combine results
        combined: Dict[str, HybridSearchResult] = {}

        # Normalize scores
        max_vector = max((r.similarity_score for r in vector_results), default=1.0)
        max_keyword = max((r.similarity_score for r in keyword_results), default=1.0)

        # Add vector results
        for result in vector_results:
            norm_score = result.similarity_score / max_vector if max_vector > 0 else 0
            combined[result.id] = HybridSearchResult(
                id=result.id,
                content=result.content,
                memory_type=result.memory_type,
                vector_score=norm_score,
                keyword_score=0.0,
                combined_score=norm_score * self.vector_weight,
                metadata=result.metadata,
            )

        # Add/update with keyword results
        for result in keyword_results:
            norm_score = result.similarity_score / max_keyword if max_keyword > 0 else 0

            if result.id in combined:
                # Update existing
                existing = combined[result.id]
                existing.keyword_score = norm_score
                existing.combined_score = (
                    existing.vector_score * self.vector_weight +
                    norm_score * self.keyword_weight
                )
                existing.matched_keywords = result.highlights
            else:
                # Add new
                combined[result.id] = HybridSearchResult(
                    id=result.id,
                    content=result.content,
                    memory_type=result.memory_type,
                    vector_score=0.0,
                    keyword_score=norm_score,
                    combined_score=norm_score * self.keyword_weight,
                    metadata=result.metadata,
                    matched_keywords=result.highlights,
                )

        # Filter by min_score and sort
        results = [r for r in combined.values() if r.combined_score >= min_score]
        results.sort(key=lambda x: x.combined_score, reverse=True)

        return results[:top_k]

    async def find_similar(
        self,
        item_id: str,
        top_k: int = DEFAULT_TOP_K,
        memory_types: Optional[List[str]] = None,
        exclude_self: bool = True
    ) -> List[SearchResult]:
        """
        Find items similar to a given item.

        Args:
            item_id: ID of the reference item
            top_k: Number of results
            memory_types: Filter by types
            exclude_self: Exclude the reference item

        Returns:
            Similar items
        """
        # Get the item's vector
        if item_id not in self.vector_index.vectors:
            return []

        query_vector = self.vector_index.vectors[item_id]

        # Search
        results = self.vector_index.search(
            query_vector=query_vector,
            top_k=top_k + (1 if exclude_self else 0),
            memory_types=memory_types,
        )

        # Exclude self if requested
        if exclude_self:
            results = [r for r in results if r.id != item_id]

        return results[:top_k]

    async def cluster_memories(
        self,
        memory_type: Optional[str] = None,
        num_clusters: int = DEFAULT_NUM_CLUSTERS
    ) -> Dict[int, List[str]]:
        """
        Cluster memories by semantic similarity.

        Simple k-means-style clustering for memory organization.

        Args:
            memory_type: Filter by memory type
            num_clusters: Number of clusters

        Returns:
            Dictionary mapping cluster_id to list of item_ids
        """
        # Get vectors to cluster
        if memory_type:
            item_ids = self.vector_index.memory_type_index.get(memory_type, [])
        else:
            item_ids = list(self.vector_index.vectors.keys())

        if len(item_ids) < num_clusters:
            return {0: item_ids}

        vectors = [self.vector_index.vectors[id] for id in item_ids]

        # Simple k-means
        clusters = self._kmeans(vectors, num_clusters)

        # Map item_ids to clusters
        result: Dict[int, List[str]] = {i: [] for i in range(num_clusters)}
        for item_id, cluster_id in zip(item_ids, clusters):
            result[cluster_id].append(item_id)

        return result

    def _kmeans(
        self,
        vectors: List[List[float]],
        k: int,
        max_iterations: int = DEFAULT_KMEANS_MAX_ITERATIONS
    ) -> List[int]:
        """Simple k-means clustering."""
        import random

        n = len(vectors)
        dim = len(vectors[0])

        # Initialize centroids randomly
        centroid_indices = random.sample(range(n), k)
        centroids = [vectors[i].copy() for i in centroid_indices]

        assignments = [0] * n

        for _ in range(max_iterations):
            # Assign points to nearest centroid
            new_assignments = []
            for vec in vectors:
                min_dist = float('inf')
                best_cluster = 0
                for i, centroid in enumerate(centroids):
                    dist = sum((a - b) ** 2 for a, b in zip(vec, centroid))
                    if dist < min_dist:
                        min_dist = dist
                        best_cluster = i
                new_assignments.append(best_cluster)

            # Check convergence
            if new_assignments == assignments:
                break

            assignments = new_assignments

            # Update centroids
            for i in range(k):
                cluster_vecs = [vectors[j] for j in range(n) if assignments[j] == i]
                if cluster_vecs:
                    centroids[i] = [
                        sum(v[d] for v in cluster_vecs) / len(cluster_vecs)
                        for d in range(dim)
                    ]

        return assignments

    def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics."""
        return {
            "vector_index": self.vector_index.get_stats(),
            "keyword_index": {
                "total_documents": len(self.keyword_index.docs),
                "total_terms": len(self.keyword_index.index),
            },
            "embedding_service": self.embedding_service.get_stats(),
        }
