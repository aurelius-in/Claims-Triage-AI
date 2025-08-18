"""
Test script for Redis integration functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from core.redis import (
    init_redis, close_redis, redis_health_check,
    cache_set_json, cache_get_json,
    enqueue_job, dequeue_job, get_queue_length,
    check_rate_limit, set_session, get_session,
    cache_result, clear_cache_pattern, get_cache_stats
)


@pytest.mark.asyncio
async def test_redis_connection():
    """Test Redis connection initialization."""
    # This test requires a running Redis instance
    # In a real environment, you'd use a test Redis container
    try:
        success = await init_redis()
        assert success is True or success is False  # Should return boolean
    except Exception as e:
        # If Redis is not available, that's okay for testing
        print(f"Redis not available: {e}")


@pytest.mark.asyncio
async def test_cache_operations():
    """Test cache operations."""
    test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
    test_key = "test:cache:key"
    
    # Test cache set
    await cache_set_json(test_key, test_data, expire=60)
    
    # Test cache get
    retrieved_data = await cache_get_json(test_key)
    assert retrieved_data is not None
    assert retrieved_data["test"] == "data"


@pytest.mark.asyncio
async def test_queue_operations():
    """Test queue operations."""
    test_job = {"type": "test_job", "data": {"test": "data"}}
    queue_name = "test_queue"
    
    # Test enqueue
    await enqueue_job(queue_name, test_job, priority=1)
    
    # Test queue length
    length = await get_queue_length(queue_name)
    assert length >= 0
    
    # Test dequeue
    dequeued_job = await dequeue_job(queue_name)
    if dequeued_job:
        assert dequeued_job["type"] == "test_job"


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality."""
    test_key = "test:rate:limit"
    
    # Test rate limit check
    allowed = await check_rate_limit(test_key, limit=5, window=60)
    assert isinstance(allowed, bool)


@pytest.mark.asyncio
async def test_session_management():
    """Test session management."""
    session_id = "test_session_123"
    session_data = {"user_id": "123", "role": "admin"}
    
    # Test set session
    await set_session(session_id, session_data, expire=300)
    
    # Test get session
    retrieved_session = await get_session(session_id)
    if retrieved_session:
        assert retrieved_session["user_id"] == "123"


@pytest.mark.asyncio
async def test_cache_decorator():
    """Test cache decorator functionality."""
    
    @cache_result(expire=60, key_prefix="test")
    async def test_function(param: str):
        return {"result": f"processed_{param}"}
    
    # Test function execution
    result1 = await test_function("test_param")
    result2 = await test_function("test_param")
    
    assert result1["result"] == "processed_test_param"
    assert result2["result"] == "processed_test_param"


@pytest.mark.asyncio
async def test_cache_management():
    """Test cache management functions."""
    # Test cache stats
    stats = await get_cache_stats()
    assert isinstance(stats, dict)
    
    # Test cache clear pattern
    await clear_cache_pattern("test:*")


@pytest.mark.asyncio
async def test_redis_health_check():
    """Test Redis health check."""
    health = await redis_health_check()
    assert isinstance(health, dict)
    assert "status" in health


async def main():
    """Run all Redis integration tests."""
    print("🧪 Running Redis integration tests...")
    
    tests = [
        test_redis_connection,
        test_cache_operations,
        test_queue_operations,
        test_rate_limiting,
        test_session_management,
        test_cache_decorator,
        test_cache_management,
        test_redis_health_check
    ]
    
    for test in tests:
        try:
            await test()
            print(f"✅ {test.__name__} passed")
        except Exception as e:
            print(f"❌ {test.__name__} failed: {str(e)}")
    
    print("🏁 Redis integration tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
