# backend/core/cache.py
import redis
import json
import hashlib
from typing import Any, Optional
from .config import get_settings

settings = get_settings()


class RedisCacheManager:
    def __init__(self, url: str = None):
        self.url = url or settings.REDIS_URL
        self.client = redis.from_url(self.url, decode_responses=True)

    def _make_key(self, prefix: str, payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str)
        h = hashlib.sha1(raw.encode()).hexdigest()
        return f"{prefix}:{h}"

    def get(self, key: str):
        val = self.client.get(key)
        if val is None:
            return None
        try:
            return json.loads(val)
        except Exception:
            return val

    def set(self, key: str, value: Any, ex: int = 300):
        self.client.set(key, json.dumps(value, default=str), ex=ex)

    def ping(self) -> bool:
        return self.client.ping()


_cache = None


def get_cache_manager():
    global _cache
    if _cache is None:
        _cache = RedisCacheManager()
    return _cache
