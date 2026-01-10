"""
Rate Limiter implementation using Token Bucket algorithm.

This module provides rate limiting functionality to control the rate of API requests
to prevent exceeding API rate limits.
"""

import threading
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for controlling API request rates.
    
    The token bucket algorithm allows for burst traffic while maintaining
    an average rate limit. Tokens are added to the bucket at a constant rate,
    and each request consumes one or more tokens.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize rate limiter with token bucket algorithm.
        
        Args:
            rate: Tokens added per second (requests per second)
            capacity: Maximum tokens in bucket (burst capacity)
        """
        if rate <= 0:
            raise ValueError("Rate must be positive")
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
            
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()
        self._lock = threading.Lock()
        
        logger.info(f"RateLimiter initialized: rate={rate} req/s, capacity={capacity}")
    
    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time since last update."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from bucket, blocking if necessary.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            True if tokens acquired, False if timeout occurred
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            raise ValueError(f"Requested tokens ({tokens}) exceeds capacity ({self.capacity})")
        
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    logger.debug(f"Acquired {tokens} token(s), {self.tokens:.2f} remaining")
                    return True
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning(f"Token acquisition timed out after {elapsed:.2f}s")
                    return False
            
            # Calculate wait time until enough tokens are available
            with self._lock:
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                # Cap wait time to avoid excessive blocking
                wait_time = min(wait_time, 0.1)
            
            time.sleep(wait_time)
    
    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        if tokens > self.capacity:
            return False
        
        with self._lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(f"Acquired {tokens} token(s) (non-blocking), {self.tokens:.2f} remaining")
                return True
            
            logger.debug(f"Failed to acquire {tokens} token(s), only {self.tokens:.2f} available")
            return False
    
    def get_available_tokens(self) -> int:
        """
        Get current number of available tokens.
        
        Returns:
            Number of available tokens (rounded down to integer)
        """
        with self._lock:
            self._refill_tokens()
            return int(self.tokens)
