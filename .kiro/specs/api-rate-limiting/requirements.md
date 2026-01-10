# Requirements Document

## Introduction

The automatic trading system is experiencing API rate limit errors from the Angel One broker API. The error `'Access denied because of exceeding access rate'` occurs when the frontend makes multiple concurrent requests to fetch stock data, which triggers excessive backend calls to the Angel One API. This feature will implement comprehensive rate limiting, request batching, caching, and retry mechanisms to prevent API rate limit violations while maintaining system responsiveness.

## Glossary

- **Angel One API**: The broker's REST API used to fetch historical market data, current prices, and place orders
- **Rate Limit**: The maximum number of API requests allowed within a specific time window
- **Request Batching**: Combining multiple individual requests into a single batch request
- **Caching Layer**: In-memory storage of API responses to reduce redundant API calls
- **Exponential Backoff**: A retry strategy where wait time increases exponentially between retry attempts
- **Circuit Breaker**: A pattern that prevents requests when failure rate exceeds a threshold
- **Token Bucket**: A rate limiting algorithm that allows bursts while maintaining average rate
- **Frontend Service**: The React/TypeScript application making API requests to the backend
- **Backend Service**: The Flask Python API that interfaces with Angel One API
- **EMA Calculator**: Component that fetches historical data to calculate Exponential Moving Averages

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want the backend to implement rate limiting for Angel One API calls, so that the system does not exceed the broker's API rate limits.

#### Acceptance Criteria

1. WHEN the system makes API calls to Angel One THEN the Backend Service SHALL enforce a maximum rate of 3 requests per second per API endpoint
2. WHEN the rate limit is approached THEN the Backend Service SHALL queue additional requests for delayed execution
3. WHEN a request is queued THEN the Backend Service SHALL process queued requests in FIFO order once capacity is available
4. WHEN the Angel One API returns a rate limit error THEN the Backend Service SHALL log the error with timestamp and affected endpoint
5. WHERE multiple API keys are configured THEN the Backend Service SHALL track rate limits independently for each API key

### Requirement 2

**User Story:** As a developer, I want the system to batch multiple stock data requests into fewer API calls, so that we minimize the total number of requests to the Angel One API.

#### Acceptance Criteria

1. WHEN the Frontend Service requests data for multiple stocks simultaneously THEN the Backend Service SHALL batch these requests into a single API call where possible
2. WHEN batching requests THEN the Backend Service SHALL wait a maximum of 500 milliseconds to collect additional requests before executing the batch
3. WHEN a batch contains more than 50 symbols THEN the Backend Service SHALL split the batch into multiple API calls with rate limiting applied
4. WHEN batch processing completes THEN the Backend Service SHALL distribute individual responses to the corresponding frontend requests
5. WHEN a single item in a batch fails THEN the Backend Service SHALL return partial results for successful items and error details for failed items

### Requirement 3

**User Story:** As a system operator, I want the backend to cache API responses, so that repeated requests for the same data do not trigger additional API calls.

#### Acceptance Criteria

1. WHEN the Backend Service receives a request for stock data THEN the Backend Service SHALL check the cache before making an API call
2. WHEN cached data exists and is less than 60 seconds old THEN the Backend Service SHALL return the cached data without making an API call
3. WHEN cached data is older than 60 seconds THEN the Backend Service SHALL fetch fresh data from the Angel One API and update the cache
4. WHEN the cache size exceeds 1000 entries THEN the Backend Service SHALL evict the least recently used entries
5. WHEN the system restarts THEN the Backend Service SHALL initialize with an empty cache

### Requirement 4

**User Story:** As a system administrator, I want the backend to implement exponential backoff retry logic, so that temporary API failures are handled gracefully without overwhelming the API.

#### Acceptance Criteria

1. WHEN an API call fails with a rate limit error THEN the Backend Service SHALL retry the request after an exponentially increasing delay
2. WHEN the first retry occurs THEN the Backend Service SHALL wait 1 second before retrying
3. WHEN subsequent retries occur THEN the Backend Service SHALL double the wait time for each retry up to a maximum of 32 seconds
4. WHEN 5 retry attempts have failed THEN the Backend Service SHALL return an error to the caller and log the failure
5. WHEN a retry succeeds THEN the Backend Service SHALL reset the retry counter for that endpoint

### Requirement 5

**User Story:** As a developer, I want the frontend to implement request debouncing, so that rapid user interactions do not trigger excessive backend requests.

#### Acceptance Criteria

1. WHEN a user action triggers a data fetch THEN the Frontend Service SHALL wait 300 milliseconds before sending the request
2. WHEN additional user actions occur within the debounce window THEN the Frontend Service SHALL cancel the pending request and restart the timer
3. WHEN the debounce timer expires THEN the Frontend Service SHALL send a single request with the latest parameters
4. WHEN critical real-time data is requested THEN the Frontend Service SHALL bypass debouncing for high-priority requests
5. WHEN the component unmounts THEN the Frontend Service SHALL cancel any pending debounced requests

### Requirement 6

**User Story:** As a system operator, I want the backend to implement a circuit breaker pattern, so that the system stops making requests when the API is consistently failing.

#### Acceptance Criteria

1. WHEN the failure rate exceeds 50 percent over a 60 second window THEN the Backend Service SHALL open the circuit and reject new requests
2. WHILE the circuit is open THEN the Backend Service SHALL return cached data if available or an error message if no cache exists
3. WHEN the circuit has been open for 30 seconds THEN the Backend Service SHALL transition to half-open state and allow one test request
4. IF the test request succeeds THEN the Backend Service SHALL close the circuit and resume normal operation
5. IF the test request fails THEN the Backend Service SHALL reopen the circuit for another 30 seconds

### Requirement 7

**User Story:** As a developer, I want the system to provide clear error messages and fallback behavior, so that users understand when rate limiting is occurring and the system remains functional.

#### Acceptance Criteria

1. WHEN a rate limit error occurs THEN the Backend Service SHALL return a 429 status code with a descriptive error message
2. WHEN the Frontend Service receives a 429 error THEN the Frontend Service SHALL display a user-friendly message indicating temporary unavailability
3. WHEN cached data is available during rate limiting THEN the Frontend Service SHALL display the cached data with a staleness indicator
4. WHEN no cached data is available THEN the Frontend Service SHALL display the last known state with a warning message
5. WHEN the system recovers from rate limiting THEN the Frontend Service SHALL automatically refresh the data and remove warning indicators

### Requirement 8

**User Story:** As a system administrator, I want comprehensive monitoring and logging of API usage, so that I can identify patterns and optimize request behavior.

#### Acceptance Criteria

1. WHEN any API request is made THEN the Backend Service SHALL log the endpoint, timestamp, response time, and result status
2. WHEN rate limiting is triggered THEN the Backend Service SHALL increment a rate limit counter metric
3. WHEN the system operates for 1 hour THEN the Backend Service SHALL generate a summary report of API usage statistics
4. WHEN cache hit rate falls below 30 percent THEN the Backend Service SHALL log a warning about inefficient caching
5. WHEN viewing logs THEN the System Administrator SHALL see aggregated metrics including total requests, cache hits, rate limit events, and average response time
