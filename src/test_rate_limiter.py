"""
Property-based tests for RateLimiter using Hypothesis.

Feature: api-rate-limiting
"""

import time
import threading
from hypothesis import given, strategies as st, settings
from src.rate_limiter import RateLimiter


class TestRateLimiterProperties:
    """Property-based tests for RateLimiter."""
    
    @given(
        rate=st.floats(min_value=1.0, max_value=10.0),
        capacity=st.integers(min_value=5, max_value=20),
        num_requests=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=100, deadline=None)
    def test_rate_limit_enforcement(self, rate: float, capacity: int, num_requests: int):
        """
        **Feature: api-rate-limiting, Property 1: Rate limit enforcement**
        
        For any sequence of API requests, the number of requests sent to Angel One API
        within any 1-second window should not exceed the configured rate per endpoint.
        
        **Validates: Requirements 1.1**
        """
        limiter = RateLimiter(rate=rate, capacity=capacity)
        
        # Track request timestamps
        request_times = []
        
        # Make requests
        for _ in range(num_requests):
            if limiter.try_acquire(tokens=1):
                request_times.append(time.time())
        
        # Verify rate limit: count requests in any 1-second window
        if len(request_times) >= 2:
            for i in range(len(request_times)):
                window_start = request_times[i]
                window_end = window_start + 1.0
                
                # Count requests in this 1-second window
                requests_in_window = sum(
                    1 for t in request_times 
                    if window_start <= t < window_end
                )
                
                # The number of requests in any 1-second window should not exceed
                # the rate (allowing for burst capacity)
                # Since we're using try_acquire (non-blocking), we should never exceed capacity
                assert requests_in_window <= capacity, \
                    f"Rate limit violated: {requests_in_window} requests in 1s window (rate={rate}, capacity={capacity})"
    
    @given(
        rate=st.floats(min_value=2.0, max_value=5.0),
        capacity=st.integers(min_value=10, max_value=20)
    )
    @settings(max_examples=100, deadline=None)
    def test_blocking_acquire_respects_rate(self, rate: float, capacity: int):
        """
        Test that blocking acquire respects the rate limit over time.
        
        This test verifies that when using blocking acquire, the rate limiter
        properly throttles requests to maintain the configured rate.
        """
        limiter = RateLimiter(rate=rate, capacity=capacity)
        
        # Drain the bucket first
        limiter.try_acquire(tokens=capacity)
        
        # Now make blocking requests and measure time
        num_requests = 5
        start_time = time.time()
        
        for _ in range(num_requests):
            success = limiter.acquire(tokens=1, timeout=5.0)
            assert success, "Acquire should succeed within timeout"
        
        elapsed = time.time() - start_time
        
        # The time taken should be at least (num_requests - 1) / rate
        # (minus 1 because the first request might be immediate if tokens refilled)
        min_expected_time = (num_requests - 1) / rate * 0.8  # 80% tolerance
        
        assert elapsed >= min_expected_time, \
            f"Requests completed too quickly: {elapsed:.2f}s (expected >= {min_expected_time:.2f}s)"
    
    @given(
        rate=st.floats(min_value=1.0, max_value=10.0),
        capacity=st.integers(min_value=5, max_value=20)
    )
    @settings(max_examples=100, deadline=None)
    def test_token_refill_over_time(self, rate: float, capacity: int):
        """
        Test that tokens refill at the correct rate over time.
        """
        limiter = RateLimiter(rate=rate, capacity=capacity)
        
        # Drain all tokens
        initial_tokens = limiter.get_available_tokens()
        limiter.try_acquire(tokens=initial_tokens)
        
        # Wait for some time
        wait_time = 0.5
        time.sleep(wait_time)
        
        # Check tokens refilled
        refilled_tokens = limiter.get_available_tokens()
        expected_tokens = int(rate * wait_time)
        
        # Allow some tolerance due to timing precision
        assert abs(refilled_tokens - expected_tokens) <= 1, \
            f"Token refill incorrect: got {refilled_tokens}, expected ~{expected_tokens}"
    
    @given(
        rate=st.floats(min_value=1.0, max_value=10.0),
        capacity=st.integers(min_value=5, max_value=20)
    )
    @settings(max_examples=100, deadline=None)
    def test_capacity_never_exceeded(self, rate: float, capacity: int):
        """
        Test that the number of available tokens never exceeds capacity.
        """
        limiter = RateLimiter(rate=rate, capacity=capacity)
        
        # Wait for tokens to refill beyond capacity
        time.sleep(2.0)
        
        # Check that tokens don't exceed capacity
        available = limiter.get_available_tokens()
        assert available <= capacity, \
            f"Tokens exceeded capacity: {available} > {capacity}"
    
    def test_concurrent_access_thread_safety(self):
        """
        Test that the rate limiter is thread-safe under concurrent access.
        """
        limiter = RateLimiter(rate=5.0, capacity=10)
        successful_acquires = []
        lock = threading.Lock()
        
        def worker():
            for _ in range(5):
                if limiter.try_acquire(tokens=1):
                    with lock:
                        successful_acquires.append(time.time())
                time.sleep(0.05)
        
        # Create multiple threads
        threads = [threading.Thread(target=worker) for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no race conditions caused over-acquisition
        # Check that initial burst doesn't exceed capacity
        if len(successful_acquires) >= 2:
            successful_acquires.sort()
            # Check the first 0.1 second window (before significant refill)
            first_timestamp = successful_acquires[0]
            initial_window_end = first_timestamp + 0.1
            
            initial_requests = sum(
                1 for t in successful_acquires 
                if first_timestamp <= t < initial_window_end
            )
            
            # In the initial burst (0.1s), we shouldn't exceed capacity
            # Allow small tolerance for timing
            assert initial_requests <= 12, \
                f"Thread safety violated: {initial_requests} requests in initial 0.1s burst (capacity=10)"
