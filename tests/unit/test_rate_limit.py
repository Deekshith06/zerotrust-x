from zerotrust_x.rate_limit import LocalRateLimiter, RateLimitKey


def test_local_rate_limiter_blocks_burst_per_context():
    limiter = LocalRateLimiter(limit=2, window_seconds=60)
    key = RateLimitKey("graph", "TENANT_A", "analyst", "127.0.0.1")
    assert limiter.allow(key)
    assert limiter.allow(key)
    assert not limiter.allow(key)
    other = RateLimitKey("graph", "TENANT_B", "analyst", "127.0.0.1")
    assert limiter.allow(other)
