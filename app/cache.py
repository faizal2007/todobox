"""Caching configuration for TodoBox application

This module provides a flexible caching layer with fallback support.
Uses Redis when available, falls back to in-memory SimpleCache.

Cache Configuration:
- Redis: Production caching with distributed support
- SimpleCache: Development/fallback in-memory caching
- FileSystemCache: Persistent caching option

Cache Invalidation:
- Automatic expiration via timeout
- Manual invalidation via cache.delete()
- Pattern-based invalidation via cache.delete_many()
"""

from flask_caching import Cache
from flask import Flask
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global cache instance
cache: Optional[Cache] = None


def init_cache(app: Flask) -> Cache:
    """Initialize cache with optimal configuration
    
    Args:
        app: Flask application instance
        
    Returns:
        Cache instance configured for the environment
        
    Cache Selection:
    1. Redis (if available) - recommended for production
    2. SimpleCache - fallback for development
    3. FileSystemCache - option for persistent cache
    """
    global cache
    
    # Try Redis first (production)
    try:
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'todobox_',
            'CACHE_REDIS_DB': 0
        }
        cache = Cache(app, config=config)
        logger.info("✓ Cache initialized with Redis")
        return cache
    except Exception as e:
        logger.warning(f"Redis cache failed ({e}), falling back to SimpleCache")
    
    # Fallback to SimpleCache (development)
    try:
        config = {
            'CACHE_TYPE': 'simple',
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'todobox_'
        }
        cache = Cache(app, config=config)
        logger.info("✓ Cache initialized with SimpleCache (development)")
        return cache
    except Exception as e:
        logger.error(f"Cache initialization failed: {e}")
        # Create dummy cache that doesn't cache anything
        config = {
            'CACHE_TYPE': 'null'
        }
        cache = Cache(app, config=config)
        return cache


# Cache timeout constants (in seconds)
CACHE_TIMEOUT = {
    'STATIC': 86400 * 30,     # 30 days for static assets
    'STATUS': 86400,           # 24 hours for status (rarely changes)
    'USER': 3600,              # 1 hour for user data
    'TODO_COUNT': 300,         # 5 minutes for todo counts
    'ACHIEVEMENT': 1800,       # 30 minutes for achievements
    'API_RESPONSE': 600,       # 10 minutes for API responses
    'SHORT': 60,               # 1 minute for frequently changing data
}


class CacheKeyGenerator:
    """Helper class to generate consistent cache keys
    
    Usage:
        key = CacheKeyGenerator.user_by_id(user_id=123)
        key = CacheKeyGenerator.status_by_name(name='Done')
        key = CacheKeyGenerator.todo_count(user_id=123)
    """
    
    PREFIX = 'todobox'
    
    @staticmethod
    def user_by_id(user_id: int) -> str:
        """Cache key for user by ID"""
        return f'{CacheKeyGenerator.PREFIX}:user:{user_id}'
    
    @staticmethod
    def user_by_email(email: str) -> str:
        """Cache key for user by email"""
        return f'{CacheKeyGenerator.PREFIX}:user_email:{email.lower()}'
    
    @staticmethod
    def status_by_id(status_id: int) -> str:
        """Cache key for status by ID"""
        return f'{CacheKeyGenerator.PREFIX}:status_id:{status_id}'
    
    @staticmethod
    def status_by_name(name: str) -> str:
        """Cache key for status by name"""
        return f'{CacheKeyGenerator.PREFIX}:status_name:{name.lower()}'
    
    @staticmethod
    def all_statuses() -> str:
        """Cache key for all statuses"""
        return f'{CacheKeyGenerator.PREFIX}:statuses:all'
    
    @staticmethod
    def todo_count(user_id: int) -> str:
        """Cache key for todo count for a user"""
        return f'{CacheKeyGenerator.PREFIX}:todo_count:{user_id}'
    
    @staticmethod
    def todo_count_by_status(user_id: int, status_id: int) -> str:
        """Cache key for todo count by status"""
        return f'{CacheKeyGenerator.PREFIX}:todo_count:{user_id}:status:{status_id}'
    
    @staticmethod
    def achievement_modal(todo_id: int) -> str:
        """Cache key for achievement modal data"""
        return f'{CacheKeyGenerator.PREFIX}:achievement:{todo_id}'
    
    @staticmethod
    def user_todos_list(user_id: int, date_range: str = 'all') -> str:
        """Cache key for user's todos list
        
        Args:
            user_id: User ID
            date_range: 'today', 'tomorrow', 'later', 'all'
        """
        return f'{CacheKeyGenerator.PREFIX}:todos:{user_id}:{date_range}'


def invalidate_user_cache(user_id: int) -> None:
    """Invalidate all cache entries for a user
    
    Called when user data changes:
    - Profile update
    - Settings change
    - Account deletion
    """
    if cache is None:
        return
    
    keys = [
        CacheKeyGenerator.user_by_id(user_id),
        CacheKeyGenerator.todo_count(user_id),
        CacheKeyGenerator.user_todos_list(user_id, 'today'),
        CacheKeyGenerator.user_todos_list(user_id, 'tomorrow'),
        CacheKeyGenerator.user_todos_list(user_id, 'later'),
    ]
    
    for key in keys:
        cache.delete(key)
    
    logger.debug(f"Invalidated cache for user {user_id}")


def invalidate_todo_cache(user_id: int, todo_id: int) -> None:
    """Invalidate cache entries related to a todo
    
    Called when todo data changes:
    - Todo created/updated/deleted
    - Status changed
    - Reminder set
    """
    if cache is None:
        return
    
    keys = [
        CacheKeyGenerator.todo_count(user_id),
        CacheKeyGenerator.user_todos_list(user_id, 'today'),
        CacheKeyGenerator.user_todos_list(user_id, 'tomorrow'),
        CacheKeyGenerator.user_todos_list(user_id, 'later'),
        CacheKeyGenerator.achievement_modal(todo_id),
    ]
    
    for key in keys:
        cache.delete(key)
    
    logger.debug(f"Invalidated cache for todo {todo_id} (user {user_id})")


def invalidate_status_cache() -> None:
    """Invalidate all status cache entries
    
    Called when status data changes (rare - mainly for admin operations)
    """
    if cache is None:
        return
    
    cache.delete(CacheKeyGenerator.all_statuses())
    logger.debug("Invalidated status cache")


__all__ = [
    'init_cache',
    'cache',
    'CACHE_TIMEOUT',
    'CacheKeyGenerator',
    'invalidate_user_cache',
    'invalidate_todo_cache',
    'invalidate_status_cache'
]
