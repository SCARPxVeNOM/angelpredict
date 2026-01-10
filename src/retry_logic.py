"""
Retry logic with exponential backoff.

This module provides retry functionality for handling transient failures
with exponentially increasing delays between attempts.
"""

import time
import logging
from typing import Callable, Tuple, Type, Any
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying a function with exponential backoff.
    
    Args:
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        retry_on: Exception types to retry on
        
    Returns:
        Decorated function that retries on failure
        
    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0)
        def fetch_data():
            # API call that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Reset success - log if this was a retry
                    if attempt > 0:
                        logger.info(
                            f"{func.__name__} succeeded on attempt {attempt + 1}/{max_retries + 1}"
                        )
                    
                    return result
                    
                except retry_on as e:
                    last_exception = e
                    
                    # If this was the last attempt, raise the exception
                    if attempt >= max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


class RetryableError(Exception):
    """Base exception for errors that should trigger retries."""
    pass


class RateLimitError(RetryableError):
    """Exception raised when API rate limit is exceeded."""
    pass


class NetworkError(RetryableError):
    """Exception raised for network-related failures."""
    pass


def execute_with_retry(
    func: Callable,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Execute a function with retry logic (non-decorator version).
    
    Args:
        func: Function to execute
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        retry_on: Exception types to retry on
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func()
            
            if attempt > 0:
                logger.info(
                    f"Function succeeded on attempt {attempt + 1}/{max_retries + 1}"
                )
            
            return result
            
        except retry_on as e:
            last_exception = e
            
            if attempt >= max_retries:
                logger.error(
                    f"Function failed after {max_retries + 1} attempts: {e}"
                )
                raise
            
            delay = min(
                initial_delay * (exponential_base ** attempt),
                max_delay
            )
            
            logger.warning(
                f"Function failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            time.sleep(delay)
    
    if last_exception:
        raise last_exception
