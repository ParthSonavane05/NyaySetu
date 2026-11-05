"""Rate-limiting helper backed by Redis sliding-window counters."""

from __future__ import annotations

from redis.asyncio import Redis

from app.core.errors import RateLimitedError


async def check_rate_limit(
    redis: Redis,  # type: ignore[type-arg]
    *,
    key: str,
    limit: int,
    window_seconds: int = 60,
) -> None:
    """Increment counter for *key*; raise RateLimitedError if *limit* exceeded.

    Uses a simple fixed-window counter with TTL.
    """
    pipe = redis.pipeline(transaction=True)
    pipe.incr(key)
    pipe.expire(key, window_seconds, nx=True)
    results = await pipe.execute()
    current: int = results[0]
    if current > limit:
        raise RateLimitedError()


def ip_key(ip: str) -> str:
    return f"rl:ip:{ip}"


def user_key(user_id: str) -> str:
    return f"rl:user:{user_id}"
