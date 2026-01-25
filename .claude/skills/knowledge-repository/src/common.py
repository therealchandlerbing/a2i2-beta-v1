"""
Arcus Knowledge Repository - Common Constants and Utilities

Shared constants and utility functions used across multiple modules.
"""

# =============================================================================
# STOPWORDS
# =============================================================================

# Common English stopwords for text processing
# Used by: embeddings.py, voice_orchestrator.py
STOPWORDS = frozenset({
    # Articles
    "a", "an", "the",
    # Conjunctions
    "and", "or", "but",
    # Prepositions
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    # Verbs (common forms)
    "is", "was", "are", "were", "been", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might", "must",
    # Pronouns
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    # Common words with low information value
    "about", "which", "while", "where", "there", "when", "who", "what", "how",
})


# =============================================================================
# TEXT PROCESSING UTILITIES
# =============================================================================

def remove_stopwords(words: list, min_length: int = 4) -> list:
    """
    Remove stopwords and short words from a list of words.

    Args:
        words: List of words to filter
        min_length: Minimum word length to keep

    Returns:
        Filtered list of words
    """
    return [w for w in words if w.lower() not in STOPWORDS and len(w) >= min_length]


def extract_keywords(text: str, min_length: int = 4, max_keywords: int = 10) -> list:
    """
    Extract keywords from text by removing stopwords.

    Args:
        text: Input text
        min_length: Minimum word length
        max_keywords: Maximum number of keywords to return

    Returns:
        List of unique keywords
    """
    import re
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    # Remove stopwords and short words
    keywords = []
    seen = set()
    for w in words:
        if w not in STOPWORDS and len(w) >= min_length and w not in seen:
            seen.add(w)
            keywords.append(w)
            if len(keywords) >= max_keywords:
                break

    return keywords
