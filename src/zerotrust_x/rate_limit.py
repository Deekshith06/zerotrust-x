"""Rate-limit contracts with a deterministic process-local implementation."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic
from typing import Protocol


@dataclass(frozen=True)
class RateLimitKey:
    scope: str
    tenant_id: str | None
    subject: str | None
    client_ip: str | None

    def value(self) -> str:
        return ":".join(
            str(part or "-") for part in (self.scope, self.tenant_id, self.subject, self.client_ip)
        )


class RateLimiter(Protocol):
    def allow(self, key: RateLimitKey) -> bool: ...


class LocalRateLimiter:
    """Single-process sliding-window limiter; not a distributed control."""

    def __init__(self, limit: int = 120, window_seconds: float = 60.0):
        if limit < 1 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: RateLimitKey) -> bool:
        now = monotonic()
        bucket = self._requests[key.value()]
        cutoff = now - self.window_seconds
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


class DistributedRateLimiter:
    """Integration contract for Redis or another shared backend."""

    def allow(self, key: RateLimitKey) -> bool:
        raise NotImplementedError("configure a shared rate-limit backend")
