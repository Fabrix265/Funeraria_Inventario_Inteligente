from slowapi import Limiter
from slowapi.util import InMemoryRateLimiter

limiter = Limiter(key_func=InMemoryRateLimiter())
