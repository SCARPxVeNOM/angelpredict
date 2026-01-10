# Implementation Plan

- [x] 1. Implement core rate limiting infrastructure


  - Create RateLimiter class with token bucket algorithm
  - Implement token acquisition with blocking and timeout support
  - Add per-endpoint rate limit tracking
  - _Requirements: 1.1, 1.2, 1.3, 1.5_






- [ ] 1.1 Write property test for rate limit enforcement
  - **Property 1: Rate limit enforcement**
  - **Validates: Requirements 1.1**

- [ ] 2. Implement caching layer
  - Create APICache class with LRU eviction


  - Implement get/set operations with TTL support
  - Add cache statistics tracking (hits, misses, size)
  - Generate cache keys from request parameters

  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_



- [ ] 2.1 Write property test for cache TTL behavior
  - **Property 3: Cache hit returns stale data within TTL**
  - **Property 4: Cache miss triggers API call**
  - **Validates: Requirements 3.2, 3.3**

- [x] 2.2 Write property test for LRU eviction


  - **Property 12: LRU eviction maintains size limit**
  - **Validates: Requirements 3.4**

- [ ] 3. Implement retry logic with exponential backoff
  - Create retry_with_backoff function
  - Implement exponential delay calculation
  - Add configurable retry parameters (max attempts, delays)
  - Handle specific exception types for retry
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 3.1 Write property test for exponential backoff
  - **Property 5: Exponential backoff increases delay**
  - **Property 6: Maximum retries respected**
  - **Validates: Requirements 4.2, 4.3, 4.4**

- [ ] 4. Implement circuit breaker pattern
  - Create CircuitBreaker class with state management (CLOSED, OPEN, HALF_OPEN)
  - Implement failure rate tracking over time window
  - Add automatic state transitions based on failure threshold
  - Implement recovery timeout and test request logic
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 4.1 Write property test for circuit breaker state transitions
  - **Property 8: Circuit breaker opens on high failure rate**
  - **Property 9: Circuit breaker blocks requests when open**
  - **Property 10: Circuit breaker recovery attempt**
  - **Validates: Requirements 6.1, 6.2, 6.3**



- [ ] 5. Implement request batching system
  - Create RequestBatcher class with async queue
  - Implement batch collection with timeout
  - Add batch splitting for oversized batches

  - Distribute responses to individual requests
  - Handle partial batch failures
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 5.1 Write property test for request batching
  - **Property 2: Request batching reduces API calls**


  - **Validates: Requirements 2.1, 2.3**

- [ ] 6. Integrate rate limiting into angelone_client.py
  - Add RateLimiter instance to AngelOneClient class
  - Wrap get_historical_data method with rate limiting
  - Wrap other API methods (get_ltp, place_order) with rate limiting
  - Add rate limit error handling and logging
  - _Requirements: 1.1, 1.4_

- [ ] 7. Integrate caching into angelone_client.py
  - Add APICache instance to AngelOneClient class
  - Check cache before making API calls in get_historical_data
  - Store successful responses in cache
  - Implement cache key generation from request parameters
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 8. Integrate retry logic into angelone_client.py
  - Wrap API calls with retry_with_backoff
  - Configure retry for rate limit and network errors
  - Add retry event logging
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 9. Integrate circuit breaker into angelone_client.py
  - Add CircuitBreaker instance to AngelOneClient class
  - Wrap API calls with circuit breaker
  - Return cached data when circuit is open
  - Add circuit breaker state logging
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 10. Implement metrics collection system
  - Create MetricsCollector class
  - Add request recording (endpoint, duration, success, cached)
  - Add rate limit event recording
  - Add circuit breaker event recording
  - Implement metrics summary generation
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 10.1 Write property test for metrics accuracy
  - **Property 11: Metrics accuracy**
  - **Validates: Requirements 8.1, 8.2**

- [ ] 11. Add configuration for rate limiting parameters
  - Add rate limiting config to config/config.py
  - Add environment variable support for all parameters
  - Document configuration options
  - _Requirements: 1.1, 3.2, 3.4, 4.2, 4.3, 6.1, 6.3_

- [ ] 12. Implement frontend request debouncing
  - Create useDebounce hook in TypeScript
  - Create useDebouncedCallback hook
  - Apply debouncing to stock data fetch requests
  - Add cleanup for unmounted components
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 12.1 Write property test for debounce behavior
  - **Property 7: Debouncing delays execution**
  - **Validates: Requirements 5.2**

- [ ] 13. Implement frontend error handling for rate limiting
  - Add 429 error handling in API client
  - Display user-friendly rate limit messages
  - Show cached data with staleness indicator
  - Implement automatic retry after rate limit recovery
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 14. Update Flask API endpoints with batching support
  - Modify /api/stocks endpoint to support batch requests
  - Integrate RequestBatcher for concurrent stock requests
  - Return batch responses with proper error handling
  - _Requirements: 2.1, 2.4, 2.5_

- [ ] 15. Add comprehensive logging for rate limiting events
  - Log all rate limit errors with timestamp and endpoint
  - Log circuit breaker state changes
  - Log cache hit/miss statistics
  - Log batch processing metrics
  - _Requirements: 1.4, 8.1, 8.2_

- [ ] 16. Write integration tests for end-to-end flow
  - Test frontend request → backend → Angel One API flow
  - Test rate limiting under concurrent load
  - Test cache effectiveness with repeated requests
  - Test circuit breaker during simulated API failures
  - _Requirements: All_

- [ ] 17. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
