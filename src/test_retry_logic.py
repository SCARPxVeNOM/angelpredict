"""
Property-based tests for retry logic using Hypothesis.

Feature: api-rate-limiting
"""

import time
from hypothesis import given, strategies as st, settings
from src.retry_logic import retry_with_backoff, execute_with_retry, RetryableError
import pytest


class TestRetryLogicProperties:
    """Property-based tests for retry logic."""
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5),
        initial_delay=st.floats(min_value=0.1, max_value=1.0),
        exponential_base=st.floats(min_value=1.5, max_value=3.0)
    )
    @settings(max_examples=50, deadline=None)
    def test_exponential_backoff_increases_delay(
        self, max_retries: int, initial_delay: float, exponential_base: float
    ):
        """
        **Feature: api-rate-limiting, Property 5: Exponential backoff increases delay**
        
        For any sequence of retry attempts, the delay before retry N should be
        greater than the delay before retry N-1, up to the maximum delay.
        
        **Validates: Requirements 4.2, 4.3**
        """
        delays = []
        attempt_count = [0]
        
        @retry_with_backoff(
            max_retries=max_retries,
            initial_delay=initial_delay,
            max_delay=32.0,
            exponential_base=exponential_base,
            retry_on=(RetryableError,)
        )
        def failing_function():
            attempt_count[0] += 1
            start_time = time.time()
            
            # Record delay (except for first attempt)
            if len(delays) > 0:
                actual_delay = start_time - delays[-1]
                delays.append(actual_delay)
            else:
                delays.append(start_time)
            
            # Always fail to trigger retries
            raise RetryableError("Test error")
        
        # Execute and expect failure after all retries
        with pytest.raises(RetryableError):
            failing_function()
        
        # Verify exponential increase in delays
        # We should have max_retries delays (excluding the first attempt)
        if len(delays) > 2:
            for i in range(1, len(delays) - 1):
                # Each delay should be greater than or equal to the previous
                # (allowing small tolerance for timing precision)
                assert delays[i] >= delays[i-1] * 0.9, \
                    f"Delay {i} ({delays[i]:.3f}s) should be >= delay {i-1} ({delays[i-1]:.3f}s)"
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_maximum_retries_respected(self, max_retries: int):
        """
        **Feature: api-rate-limiting, Property 6: Maximum retries respected**
        
        For any failing API call, the system should attempt at most max_retries
        before returning an error.
        
        **Validates: Requirements 4.4**
        """
        attempt_count = [0]
        
        @retry_with_backoff(
            max_retries=max_retries,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            retry_on=(RetryableError,)
        )
        def failing_function():
            attempt_count[0] += 1
            raise RetryableError("Test error")
        
        # Execute and expect failure
        with pytest.raises(RetryableError):
            failing_function()
        
        # Verify total attempts = max_retries + 1 (initial attempt + retries)
        expected_attempts = max_retries + 1
        assert attempt_count[0] == expected_attempts, \
            f"Expected {expected_attempts} attempts, got {attempt_count[0]}"
    
    @given(
        max_retries=st.integers(min_value=2, max_value=5),
        success_on_attempt=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=100, deadline=None)
    def test_retry_stops_on_success(self, max_retries: int, success_on_attempt: int):
        """
        Test that retries stop immediately upon success.
        """
        # Ensure success_on_attempt is within max_retries
        success_on_attempt = min(success_on_attempt, max_retries)
        
        attempt_count = [0]
        
        @retry_with_backoff(
            max_retries=max_retries,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            retry_on=(RetryableError,)
        )
        def sometimes_failing_function():
            attempt_count[0] += 1
            if attempt_count[0] < success_on_attempt:
                raise RetryableError("Test error")
            return "success"
        
        # Execute and expect success
        result = sometimes_failing_function()
        assert result == "success"
        
        # Verify it stopped after success
        assert attempt_count[0] == success_on_attempt, \
            f"Should stop after {success_on_attempt} attempts, but made {attempt_count[0]}"
    
    @given(
        initial_delay=st.floats(min_value=0.1, max_value=0.5),
        max_delay=st.floats(min_value=1.0, max_value=5.0)
    )
    @settings(max_examples=50, deadline=None)
    def test_delay_never_exceeds_max(self, initial_delay: float, max_delay: float):
        """
        Test that retry delays never exceed the maximum delay.
        """
        delays = []
        
        def failing_function():
            if len(delays) > 0:
                delays.append(time.time())
            else:
                delays.append(time.time())
            raise RetryableError("Test error")
        
        # Execute with retry
        with pytest.raises(RetryableError):
            execute_with_retry(
                failing_function,
                max_retries=5,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=2.0,
                retry_on=(RetryableError,)
            )
        
        # Calculate actual delays between attempts
        if len(delays) > 1:
            actual_delays = [delays[i] - delays[i-1] for i in range(1, len(delays))]
            
            # All delays should be <= max_delay (with small tolerance)
            for delay in actual_delays:
                assert delay <= max_delay + 0.2, \
                    f"Delay {delay:.2f}s exceeded max_delay {max_delay:.2f}s"
    
    def test_retry_on_specific_exceptions(self):
        """
        Test that retry only occurs for specified exception types.
        """
        attempt_count = [0]
        
        @retry_with_backoff(
            max_retries=3,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            retry_on=(RetryableError,)
        )
        def function_with_different_errors():
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                raise RetryableError("Retryable error")
            else:
                raise ValueError("Non-retryable error")
        
        # Should retry on RetryableError, then fail on ValueError
        with pytest.raises(ValueError):
            function_with_different_errors()
        
        # Should have made 2 attempts (1 initial + 1 retry)
        assert attempt_count[0] == 2
    
    def test_execute_with_retry_function(self):
        """
        Test the non-decorator execute_with_retry function.
        """
        attempt_count = [0]
        
        def failing_function():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise RetryableError("Test error")
            return "success"
        
        result = execute_with_retry(
            failing_function,
            max_retries=5,
            initial_delay=0.1,
            max_delay=1.0,
            exponential_base=2.0,
            retry_on=(RetryableError,)
        )
        
        assert result == "success"
        assert attempt_count[0] == 3
