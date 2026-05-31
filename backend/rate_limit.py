"""In-memory per-key rate limiter.

Fixed-window counter (not token bucket): every identifier gets a
fresh N-request budget each window. Simple, allocation-light, and
fine for a single-instance deployment.

Trade-off: horizontal scale silently defeats the limit. If you scale
to multiple instances, swap for Redis / Upstash keeping the same
return shape.

Pattern lifted from a production WhatsApp CRM reference codebase.
"""

import time
from dataclasses import dataclass, field


@dataclass
class RateLimitOptions:
    """Configuration for a rate limit budget."""
    limit: int
    window_seconds: int


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    success: bool
    remaining: int
    reset_at: float  # Unix timestamp when the bucket refills
    limit: int


class _Entry:
    __slots__ = ("count", "reset_at")
    count: int
    reset_at: float

    def __init__(self, reset_at: float) -> None:
        self.count = 1
        self.reset_at = reset_at


# In-memory storage
_buckets: dict[str, _Entry] = {}
_SWEEP_EVERY = 1000
_calls_since_sweep = 0


def _sweep_expired(now: float) -> None:
    """Remove expired entries."""
    global _buckets
    for k in list(_buckets.keys()):
        if _buckets[k].reset_at <= now:
            del _buckets[k]


def check_rate_limit(
    key: str,
    options: RateLimitOptions,
) -> RateLimitResult:
    """Check if a request should be rate-limited.

    Args:
        key: Unique identifier (e.g., "send:user_123").
        options: Budget configuration.

    Returns:
        RateLimitResult with success flag and remaining budget.
    """
    global _calls_since_sweep
    now = time.time()

    _calls_since_sweep += 1
    if _calls_since_sweep >= _SWEEP_EVERY:
        _calls_since_sweep = 0
        _sweep_expired(now)

    entry = _buckets.get(key)

    if entry is None or entry.reset_at <= now:
        # Fresh window
        _buckets[key] = _Entry(now + options.window_seconds)
        return RateLimitResult(
            success=True,
            remaining=options.limit - 1,
            reset_at=now + options.window_seconds,
            limit=options.limit,
        )

    if entry.count >= options.limit:
        return RateLimitResult(
            success=False,
            remaining=0,
            reset_at=entry.reset_at,
            limit=options.limit,
        )

    entry.count += 1
    return RateLimitResult(
        success=True,
        remaining=options.limit - entry.count,
        reset_at=entry.reset_at,
        limit=options.limit,
    )


def build_rate_limit_response(result: RateLimitResult) -> tuple[dict, int, dict]:
    """Build a standard 429 response dict + status + headers.

    Returns:
        (body_dict, status_code, headers_dict)
    """
    retry_after = max(1, int(result.reset_at - time.time()))
    return (
        {
            "error": "Rate limit exceeded",
            "retry_after_seconds": retry_after,
        },
        429,
        {
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(int(result.reset_at)),
        },
    )


# ── Preconfigured budgets ──

RATE_LIMITS = {
    "send": RateLimitOptions(limit=60, window_seconds=60),
    "broadcast": RateLimitOptions(limit=5, window_seconds=60),
    "webhook": RateLimitOptions(limit=300, window_seconds=60),
    "auth": RateLimitOptions(limit=30, window_seconds=60),
}


def reset_rate_limits_for_tests() -> None:
    """Clear all rate limit state. For tests only."""
    _buckets.clear()
    globals()["_calls_since_sweep"] = 0
