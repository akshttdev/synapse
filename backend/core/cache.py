# backend/core/cache.py
"""
Redis cache manager
"""

import redis
import json
import hashlib
from typing import Optional, Any
from functools import lru_cache
import logging

from core.config import get_settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self, redis_url: str, ttl: int = 3600):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl
        logger.info(f"✓ Cache manager initialized (TTL={ttl}s)")
    
    def _make_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        try:
            ttl = ttl or self.ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        try:
            for key in self.redis_client.scan_iter(match=f"*{pattern}*"):
                self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")


@lru_cache()
def get_cache_manager() -> CacheManager:
    """Get cached cache manager instance"""
    settings = get_settings()
    return CacheManager(
        redis_url=settings.REDIS_URL,
        ttl=settings.CACHE_TTL
    )