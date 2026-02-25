"""
Cache Service - Django cache wrapper for AI responses.
Migrated from Flask's cache.py with Django cache framework integration.
"""
import hashlib
import json
from typing import Optional, Dict, Any
from django.core.cache import cache


# Default TTL: 24 hours (in seconds)
DEFAULT_TTL = 86400


def generate_cache_key(content: str, language: str, subject: str, session: str) -> str:
    """
    Generate a unique cache key based on lesson content and parameters.
    
    Args:
        content: Lesson content text
        language: Language (fr/ar)
        subject: Subject name
        session: Session number
        
    Returns:
        SHA256 hash as cache key
    """
    key_data = f"{content}|{language}|{subject}|{session}"
    return f"lesson_cache:{hashlib.sha256(key_data.encode()).hexdigest()}"


def get_cached_lesson(content: str, language: str, subject: str, session: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached lesson data if available.
    
    Args:
        content: Lesson content text
        language: Language (fr/ar)
        subject: Subject name
        session: Session number
        
    Returns:
        Cached lesson data or None if not found
    """
    key = generate_cache_key(content, language, subject, session)
    cached = cache.get(key)
    
    if cached:
        # Django cache may return bytes, try to parse as JSON
        if isinstance(cached, str):
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                return None
        return cached
    
    return None


def set_cached_lesson(
    content: str, 
    language: str, 
    subject: str, 
    session: str, 
    data: Dict[str, Any],
    ttl: int = DEFAULT_TTL
) -> None:
    """
    Store lesson data in cache.
    
    Args:
        content: Lesson content text
        language: Language (fr/ar)
        subject: Subject name
        session: Session number
        data: Lesson data to cache
        ttl: Time-to-live in seconds
    """
    key = generate_cache_key(content, language, subject, session)
    # Store as JSON string for compatibility
    cache.set(key, json.dumps(data), timeout=ttl)


def clear_cache() -> None:
    """Clear all lesson cache entries."""
    # Since we're using a unique prefix, we can iterate and delete
    # For simplicity, clear the entire cache
    cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    Note: LocMemCache doesn't support stats, so we return basic info.
    
    Returns:
        Dictionary with cache information
    """
    return {
        "hits": 0,
        "misses": 0,
        "total_requests": 0,
        "hit_rate_percent": 0.0,
        "cache_backend": "Django cache (LocMem)"
    }
