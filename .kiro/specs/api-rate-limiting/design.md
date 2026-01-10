# Design Document: API Rate Limiting System

## Overview

This design implements a comprehensive rate limiting, caching, and request optimization system to prevent Angel One API rate limit violations. The solution includes backend rate limiting with token bucket algorithm, request batching, multi-layer caching, exponential backoff retry logic, circuit breaker pattern, and frontend debouncing. The design ensures the system remains responsive while respecting API constraints.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React/TS)                      │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Debouncer    │  │ Request Queue│  │  Error Handler  │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Flask/Python)                    │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Rate Limiter   │  │ Request      │  │  Cache Layer    │ │
│  │ (Token Bucket) │  │ Batcher      │  │  (LRU Cache)    │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Circuit        │  │ Retry Logic  │  │  Metrics        │ │
│  │ Breaker        │  │ (Exp Backoff)│  │  Collector      │ │
│  └────────────────┘  └──────────────┘  └─────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ Rate-Limited Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Angel One API                           │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Frontend Request** → Debouncer delays and deduplicates requests
2. **Backend Reception** → Request enters rate limiter queue
3. **Cache Check** → System checks if fresh cached data exists
4. **Rate Limiting** → Token bucket algorithm controls request rate
5. **Batching** → Multiple requests combined where possible
6. **Circuit Breaker** → Prevents requests during API failures
7. **API Call** → Actual request to Angel One with retry logic
8. **Response Caching** → Store response for future requests
9. **Metrics Collection** → Log usage statistics

## Components and Interfaces

### 1. Rate Limiter (Backend)

**Purpose**: Control the rate of outgoing API requests using token bucket algorithm

**Class**: `RateLimiter`

```python
class RateLimiter:
    def __init__(self, rate: float, capacity: int):
        """
        Initialize rate limiter with token bucket algorithm
        
        Args:
            rate: Tokens added per second (requests per second)
            capacity: Maximum tokens in bucket (burst capacity)
        """
        
    def acquire(self, tokens: int = 1, timeout: float = None) -> bool:
        """
        Acquire tokens from bucket, blocking if necessary
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (None = wait forever)
            
        Returns:
            True if tokens acquired, False if timeout
        """
        
    def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking
        
        Returns:
            True if tokens acquired, False otherwise
        """
        
    def get_available_tokens(self) -> int:
        """Get current number of available tokens"""
```

**Configuration**:
- Rate: 3 requests/second per endpoint
- Capacity: 10 tokens (allows bursts)
- Separate limiters for each API key

### 2. Request Batcher (Backend)

**Purpose**: Combine multiple individual requests into batch API calls

**Class**: `RequestBatcher`

```python
class RequestBatcher:
    def __init__(self, max_batch_size: int = 50, max_wait_ms: int = 500):
        """
        Initialize request batcher
        
        Args:
            max_batch_size: Maximum items per batch
            max_wait_ms: Maximum time to wait for more requests
        """
        
    async def add_request(self, symbol_token: str, exchange: str) -> dict:
        """
        Add request to batch queue
        
        Args:
            symbol_token: Stock symbol token
            exchange: Exchange identifier
            
        Returns:
            Response data for this symbol
        """
        
    async def _process_batch(self, batch: List[dict]) -> List[dict]:
        """
        Process a batch of requests
        
        Args:
            batch: List of request parameters
            
        Returns:
            List of responses
        """
```

### 3. Cache Layer (Backend)

**Purpose**: Store API responses to reduce redundant calls

**Class**: `APICache`

```python
class APICache:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 60):
        """
        Initialize LRU cache with TTL
        
        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries
        """
        
    def get(self, key: str) -> Optional[dict]:
        """
        Get cached value if exists and not expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        
    def set(self, key: str, value: dict) -> None:
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Data to cache
        """
        
    def invalidate(self, key: str) -> None:
        """Remove entry from cache"""
        
    def clear(self) -> None:
        """Clear all cache entries"""
        
    def get_stats(self) -> dict:
        """Get cache statistics (hits, misses, size)"""
```

**Cache Key Format**: `{endpoint}:{symbol_token}:{exchange}:{params_hash}`

### 4. Circuit Breaker (Backend)

**Purpose**: Prevent requests during sustained API failures

**Class**: `CircuitBreaker`

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: float = 0.5, 
                 recovery_timeout: int = 30,
                 window_size: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Failure rate to open circuit (0.0-1.0)
            recovery_timeout: Seconds before attempting recovery
            window_size: Time window for failure rate calculation
        """
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        
    def get_state(self) -> str:
        """Get current state: CLOSED, OPEN, or HALF_OPEN"""
        
    def reset(self) -> None:
        """Manually reset circuit breaker"""
```

### 5. Retry Logic with Exponential Backoff (Backend)

**Purpose**: Retry failed requests with increasing delays

**Function**: `retry_with_backoff`

```python
def retry_with_backoff(
    func: Callable,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 32.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
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
```

### 6. Request Debouncer (Frontend)

**Purpose**: Delay and deduplicate rapid frontend requests

**Hook**: `useDebounce`

```typescript
function useDebounce<T>(value: T, delay: number): T {
  /**
   * Debounce a value
   * 
   * @param value - Value to debounce
   * @param delay - Delay in milliseconds
   * @returns Debounced value
   */
}

function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  /**
   * Debounce a callback function
   * 
   * @param callback - Function to debounce
   * @param delay - Delay in milliseconds
   * @returns Debounced function
   */
}
```

### 7. Metrics Collector (Backend)

**Purpose**: Track API usage and performance metrics

**Class**: `MetricsCollector`

```python
class MetricsCollector:
    def __init__(self):
        """Initialize metrics collector"""
        
    def record_request(self, endpoint: str, duration: float, 
                      success: bool, cached: bool) -> None:
        """Record API request metrics"""
        
    def record_rate_limit(self, endpoint: str) -> None:
        """Record rate limit event"""
        
    def record_circuit_breaker_open(self, endpoint: str) -> None:
        """Record circuit breaker opening"""
        
    def get_summary(self, time_window: int = 3600) -> dict:
        """
        Get metrics summary
        
        Args:
            time_window: Time window in seconds
            
        Returns:
            Dictionary with metrics summary
        """
```

## Data Models

### Cache Entry

```python
@dataclass
class CacheEntry:
    key: str
    value: dict
    timestamp: float
    ttl: int
    access_count: int
    last_accessed: float
```

### Rate Limit State

```python
@dataclass
class RateLimitState:
    tokens: float
    last_update: float
    rate: float
    capacity: int
    endpoint: str
```

### Circuit Breaker State

```python
@dataclass
class CircuitBreakerState:
    state: str  # CLOSED, OPEN, HALF_OPEN
    failure_count: int
    success_count: int
    last_failure_time: float
    last_state_change: float
```

### Batch Request

```python
@dataclass
class BatchRequest:
    id: str
    symbol_token: str
    exchange: str
    params: dict
    timestamp: float
    future: asyncio.Future
```

### API Metrics

```python
@dataclass
class APIMetrics:
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    cache_hits: int
    cache_misses: int
    rate_limit_events: int
    circuit_breaker_opens: int
    average_response_time: float
    p95_response_time: float
    p99_response_time: float
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Rate limit enforcement

*For any* sequence of API requests, the number of requests sent to Angel One API within any 1-second window should not exceed 3 requests per endpoint
**Validates: Requirements 1.1**

### Property 2: Request batching reduces API calls

*For any* set of N concurrent requests for different symbols, the number of actual API calls should be less than or equal to ceiling(N / 50)
**Validates: Requirements 2.1, 2.3**

### Property 3: Cache hit returns stale data within TTL

*For any* cached entry, if the entry age is less than 60 seconds, retrieving it should return the cached value without making an API call
**Validates: Requirements 3.2**

### Property 4: Cache miss triggers API call

*For any* cache key, if no entry exists or the entry is older than 60 seconds, a cache lookup should trigger a fresh API call
**Validates: Requirements 3.3**

### Property 5: Exponential backoff increases delay

*For any* sequence of retry attempts, the delay before retry N should be greater than the delay before retry N-1, up to the maximum delay
**Validates: Requirements 4.2, 4.3**

### Property 6: Maximum retries respected

*For any* failing API call, the system should attempt at most 5 retries before returning an error
**Validates: Requirements 4.4**

### Property 7: Debouncing delays execution

*For any* debounced function call, if another call occurs within the debounce window, the first call should be cancelled and only the last call should execute
**Validates: Requirements 5.2**

### Property 8: Circuit breaker opens on high failure rate

*For any* 60-second window, if the failure rate exceeds 50%, the circuit breaker should transition to OPEN state
**Validates: Requirements 6.1**

### Property 9: Circuit breaker blocks requests when open

*For any* request made while the circuit is OPEN, the request should be rejected without calling the API
**Validates: Requirements 6.2**

### Property 10: Circuit breaker recovery attempt

*For any* circuit breaker in OPEN state for 30 seconds, the next request should transition to HALF_OPEN and allow one test request
**Validates: Requirements 6.3**

### Property 11: Metrics accuracy

*For any* time window, the sum of cache hits and cache misses should equal the total number of requests received
**Validates: Requirements 8.1, 8.2**

### Property 12: LRU eviction maintains size limit

*For any* cache with max size N, after any number of insertions, the cache size should never exceed N entries
**Validates: Requirements 3.4**

## Error Handling

### Error Types

1. **RateLimitError**: Raised when rate limit is exceeded
   - HTTP 429 status code
   - Includes retry-after header
   - Logged with timestamp and endpoint

2. **CircuitBreakerOpenError**: Raised when circuit is open
   - HTTP 503 status code
   - Includes estimated recovery time
   - Returns cached data if available

3. **BatchTimeoutError**: Raised when batch processing times out
   - Falls back to individual requests
   - Logs timeout event

4. **CacheError**: Raised on cache operation failures
   - Non-fatal, continues without cache
   - Logs error details

### Error Recovery Strategies

1. **Rate Limit Errors**:
   - Queue request for delayed execution
   - Return cached data if available
   - Display user-friendly message

2. **API Failures**:
   - Retry with exponential backoff
   - Fall back to cached data
   - Open circuit breaker if sustained

3. **Timeout Errors**:
   - Cancel pending requests
   - Return partial results
   - Log timeout for monitoring

4. **Network Errors**:
   - Retry with backoff
   - Use cached data
   - Display offline indicator

## Testing Strategy

### Unit Testing

**Backend Components**:
- `RateLimiter`: Test token acquisition, blocking, timeout
- `RequestBatcher`: Test batch formation, splitting, timeout
- `APICache`: Test get/set, TTL expiration, LRU eviction
- `CircuitBreaker`: Test state transitions, failure counting
- `retry_with_backoff`: Test retry logic, delay calculation
- `MetricsCollector`: Test metric recording, aggregation

**Frontend Components**:
- `useDebounce`: Test delay, cancellation, value updates
- `useDebouncedCallback`: Test function debouncing
- Error handlers: Test error display, recovery

### Property-Based Testing

Property-based tests will use **Hypothesis** (Python) and **fast-check** (TypeScript) libraries.

Each property test should run a minimum of 100 iterations to ensure comprehensive coverage.

**Backend Properties** (Python/Hypothesis):
- Rate limit enforcement across random request patterns
- Batch size constraints with varying input sizes
- Cache TTL behavior with random timestamps
- Exponential backoff delay progression
- Circuit breaker state transitions with random failure patterns
- LRU eviction with random access patterns

**Frontend Properties** (TypeScript/fast-check):
- Debounce cancellation with rapid inputs
- Request deduplication

### Integration Testing

- End-to-end flow: Frontend → Backend → Angel One API
- Rate limiting under load
- Cache effectiveness with real data
- Circuit breaker behavior during API outages
- Metrics collection accuracy

### Load Testing

- Simulate 100 concurrent frontend requests
- Verify rate limiting prevents API overload
- Measure cache hit rate
- Test circuit breaker under sustained failures

## Implementation Notes

### Configuration

All rate limiting parameters should be configurable via environment variables:

```python
# config/config.py additions
RATE_LIMIT_REQUESTS_PER_SECOND = 3
RATE_LIMIT_BURST_CAPACITY = 10
CACHE_TTL_SECONDS = 60
CACHE_MAX_SIZE = 1000
BATCH_MAX_SIZE = 50
BATCH_MAX_WAIT_MS = 500
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 0.5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 30
RETRY_MAX_ATTEMPTS = 5
RETRY_INITIAL_DELAY = 1.0
RETRY_MAX_DELAY = 32.0
DEBOUNCE_DELAY_MS = 300
```

### Performance Considerations

1. **Memory Usage**: Cache limited to 1000 entries (~10MB estimated)
2. **CPU Usage**: Token bucket algorithm is O(1)
3. **Latency**: Batching adds max 500ms delay
4. **Throughput**: Rate limiting caps at 3 req/sec per endpoint

### Monitoring and Observability

1. **Metrics Dashboard**: Display real-time API usage
2. **Alerts**: Trigger on high rate limit events
3. **Logs**: Structured logging with correlation IDs
4. **Tracing**: Track request flow through components

### Backward Compatibility

- Existing API endpoints remain unchanged
- Rate limiting is transparent to callers
- Graceful degradation if components fail
- Feature flags for gradual rollout
