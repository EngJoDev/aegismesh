"""
AegisMesh - Semantic & In-Memory Response Caching Engine.
"""

import hashlib
import time
import threading
from typing import Dict, Any, Optional, Tuple

class SemanticCache:
    """
    In-memory response cache with TTL expiration and request hashing.
    Drastically reduces AI API costs and latency.
    """
    def __init__(self, default_ttl_seconds: int = 300, max_entries: int = 1000):
        self.default_ttl = default_ttl_seconds
        self.max_entries = max_entries
        self.cache: Dict[str, Tuple[Any, float]] = {}  # hash -> (response_data, expires_at)
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def _hash_request(self, method: str, path: str, body: str) -> str:
        content = f"{method.upper()}:{path}:{body.strip()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, method: str, path: str, body: str) -> Optional[Any]:
        key = self._hash_request(method, path, body)
        now = time.time()
        with self.lock:
            if key in self.cache:
                data, expires_at = self.cache[key]
                if now < expires_at:
                    self.hits += 1
                    return data
                else:
                    del self.cache[key]
            self.misses += 1
            return None

    def set(self, method: str, path: str, body: str, response_data: Any, ttl: Optional[int] = None) -> None:
        key = self._hash_request(method, path, body)
        expires_at = time.time() + (ttl or self.default_ttl)
        with self.lock:
            if len(self.cache) >= self.max_entries:
                # Evict oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = (response_data, expires_at)

    def stats(self) -> Dict[str, Any]:
        with self.lock:
            total = self.hits + self.misses
            ratio = round((self.hits / total * 100), 2) if total > 0 else 0.0
            return {
                "total_entries": len(self.cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio_percent": ratio
            }
