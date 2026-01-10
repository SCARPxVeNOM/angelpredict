"""
Property-based tests for APICache using Hypothesis.

Feature: api-rate-limiting
"""

import time
from hypothesis import given, strategies as st, settings
from src.api_cache import APICache


class TestAPICacheProperties:
    """Property-based tests for APICache."""
    
    @given(
        ttl=st.integers(min_value=1, max_value=5),
        max_size=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_hit_within_ttl(self, ttl: int, max_size: int):
        """
        **Feature: api-rate-limiting, Property 3: Cache hit returns stale data within TTL**
        
        For any cached entry, if the entry age is less than TTL seconds,
        retrieving it should return the cached value without making an API call.
        
        **Validates: Requirements 3.2**
        """
        cache = APICache(max_size=max_size, ttl_seconds=ttl)
        
        # Store a value
        key = "test_key"
        value = {"data": "test_value", "timestamp": time.time()}
        cache.set(key, value)
        
        # Retrieve immediately (should hit)
        result = cache.get(key)
        assert result is not None, "Cache should return value immediately after set"
        assert result == value, "Cached value should match original"
        
        # Wait for half the TTL
        wait_time = ttl / 2.0
        time.sleep(wait_time)
        
        # Should still be in cache
        result = cache.get(key)
        assert result is not None, f"Cache should return value after {wait_time}s (TTL={ttl}s)"
        assert result == value, "Cached value should still match original"
        
        # Verify stats show cache hit
        stats = cache.get_stats()
        assert stats['hits'] >= 2, "Should have at least 2 cache hits"
    
    @given(
        ttl=st.integers(min_value=1, max_value=3),
        max_size=st.integers(min_value=10, max_value=100)
    )
    @settings(max_examples=50, deadline=None)
    def test_cache_miss_after_ttl(self, ttl: int, max_size: int):
        """
        **Feature: api-rate-limiting, Property 4: Cache miss triggers API call**
        
        For any cache key, if no entry exists or the entry is older than TTL seconds,
        a cache lookup should return None (triggering a fresh API call).
        
        **Validates: Requirements 3.3**
        """
        cache = APICache(max_size=max_size, ttl_seconds=ttl)
        
        # Store a value
        key = "test_key"
        value = {"data": "test_value"}
        cache.set(key, value)
        
        # Wait for TTL to expire (add small buffer)
        time.sleep(ttl + 0.2)
        
        # Should be expired
        result = cache.get(key)
        assert result is None, f"Cache should return None after TTL ({ttl}s) expires"
        
        # Verify stats show cache miss
        stats = cache.get_stats()
        assert stats['misses'] >= 1, "Should have at least 1 cache miss"
    
    @given(
        max_size=st.integers(min_value=5, max_value=20),
        num_entries=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=100, deadline=None)
    def test_lru_eviction_maintains_size_limit(self, max_size: int, num_entries: int):
        """
        **Feature: api-rate-limiting, Property 12: LRU eviction maintains size limit**
        
        For any cache with max size N, after any number of insertions,
        the cache size should never exceed N entries.
        
        **Validates: Requirements 3.4**
        """
        cache = APICache(max_size=max_size, ttl_seconds=60)
        
        # Add more entries than max_size
        for i in range(num_entries):
            key = f"key_{i}"
            value = {"data": f"value_{i}"}
            cache.set(key, value)
            
            # Verify size never exceeds max_size
            stats = cache.get_stats()
            assert stats['size'] <= max_size, \
                f"Cache size ({stats['size']}) exceeded max_size ({max_size})"
        
        # Final size should be exactly max_size (or less if num_entries < max_size)
        final_stats = cache.get_stats()
        expected_size = min(num_entries, max_size)
        assert final_stats['size'] == expected_size, \
            f"Final cache size should be {expected_size}, got {final_stats['size']}"
    
    @given(
        max_size=st.integers(min_value=10, max_value=30)
    )
    @settings(max_examples=100, deadline=None)
    def test_lru_evicts_least_recently_used(self, max_size: int):
        """
        Test that LRU eviction removes the least recently used entries.
        """
        cache = APICache(max_size=max_size, ttl_seconds=60)
        
        # Fill cache to capacity
        for i in range(max_size):
            cache.set(f"key_{i}", {"data": i})
        
        # Access first half of entries (making them recently used)
        for i in range(max_size // 2):
            cache.get(f"key_{i}")
        
        # Add new entries to trigger eviction
        num_new = max_size // 4
        for i in range(num_new):
            cache.set(f"new_key_{i}", {"data": f"new_{i}"})
        
        # The first half (recently accessed) should still be in cache
        for i in range(max_size // 2):
            result = cache.get(f"key_{i}")
            assert result is not None, \
                f"Recently accessed key_{i} should still be in cache"
        
        # Some of the second half (not accessed) should have been evicted
        evicted_count = 0
        for i in range(max_size // 2, max_size):
            result = cache.get(f"key_{i}")
            if result is None:
                evicted_count += 1
        
        assert evicted_count >= num_new, \
            f"At least {num_new} old entries should have been evicted"
    
    @given(
        ttl=st.integers(min_value=1, max_value=5),
        max_size=st.integers(min_value=10, max_value=50)
    )
    @settings(max_examples=100, deadline=None)
    def test_cache_key_generation_consistency(self, ttl: int, max_size: int):
        """
        Test that cache key generation is consistent for same parameters.
        """
        cache = APICache(max_size=max_size, ttl_seconds=ttl)
        
        # Generate keys with same parameters
        key1 = APICache.generate_key("endpoint", symbol="AAPL", exchange="NSE")
        key2 = APICache.generate_key("endpoint", symbol="AAPL", exchange="NSE")
        
        assert key1 == key2, "Same parameters should generate same key"
        
        # Different parameters should generate different keys
        key3 = APICache.generate_key("endpoint", symbol="GOOGL", exchange="NSE")
        assert key1 != key3, "Different parameters should generate different keys"
        
        # Parameter order shouldn't matter
        key4 = APICache.generate_key("endpoint", exchange="NSE", symbol="AAPL")
        assert key1 == key4, "Parameter order should not affect key generation"
    
    def test_cache_stats_accuracy(self):
        """
        Test that cache statistics are accurately tracked.
        """
        cache = APICache(max_size=10, ttl_seconds=60)
        
        # Initial stats
        stats = cache.get_stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        assert stats['size'] == 0
        
        # Add entries
        for i in range(5):
            cache.set(f"key_{i}", {"data": i})
        
        stats = cache.get_stats()
        assert stats['size'] == 5
        
        # Cache hits
        for i in range(3):
            cache.get(f"key_{i}")
        
        stats = cache.get_stats()
        assert stats['hits'] == 3
        
        # Cache misses
        cache.get("nonexistent")
        cache.get("also_nonexistent")
        
        stats = cache.get_stats()
        assert stats['misses'] == 2
        
        # Hit rate calculation
        total = stats['hits'] + stats['misses']
        expected_hit_rate = round((stats['hits'] / total) * 100, 2)
        assert stats['hit_rate'] == expected_hit_rate
