"""
AegisMesh - High-Performance Anti-DDoS Rate Limiter (Token Bucket Algorithm).
"""

import time
import threading
from typing import Dict, Tuple

class TokenBucketRateLimiter:
    """
    Thread-safe in-memory Token Bucket rate limiter for Anti-DDoS and API throttle.
    """
    def __init__(self, rate_per_second: float = 10.0, burst_capacity: int = 20):
        self.rate = rate_per_second
        self.capacity = float(burst_capacity)
        self.buckets: Dict[str, Tuple[float, float]] = {}  # ip -> (tokens, last_updated)
        self.lock = threading.Lock()

    def allow_request(self, client_ip: str, cost: float = 1.0) -> Tuple[bool, float]:
        """
        Determines whether client is allowed or rate-limited.
        Returns: (allowed: bool, remaining_tokens: float)
        """
        now = time.time()
        with self.lock:
            if client_ip not in self.buckets:
                self.buckets[client_ip] = (self.capacity, now)

            tokens, last_time = self.buckets[client_ip]
            # Refill tokens based on elapsed time
            elapsed = now - last_time
            tokens = min(self.capacity, tokens + elapsed * self.rate)

            if tokens >= cost:
                tokens -= cost
                self.buckets[client_ip] = (tokens, now)
                return True, tokens
            else:
                self.buckets[client_ip] = (tokens, now)
                return False, tokens

    def reset_ip(self, client_ip: str) -> None:
        with self.lock:
            if client_ip in self.buckets:
                del self.buckets[client_ip]
