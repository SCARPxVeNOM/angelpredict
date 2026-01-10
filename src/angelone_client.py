"""
AngelOne SmartAPI Client Wrapper
Handles authentication, historical data fetching, market data, and order placement
"""
import pyotp
from SmartApi import SmartConnect
from logzero import logger
import time
from config import config
from src.rate_limiter import RateLimiter
from src.api_cache import APICache
from src.retry_logic import retry_with_backoff, RateLimitError, NetworkError


class AngelOneClient:
    """Wrapper class for AngelOne SmartAPI"""
    
    def __init__(self, api_key=None, username=None, password=None, mpin=None, totp_token=None, use_mpin=None, api_type='TRADING'):
        """
        Initialize AngelOne client
        
        Args:
            api_key: API key (defaults to config based on api_type)
            username: AngelOne client code
            password: AngelOne PIN/Password
            mpin: AngelOne MPIN (if using MPIN login)
            totp_token: TOTP token from QR code
            use_mpin: Whether to use MPIN instead of password (defaults to config)
            api_type: Type of API - 'TRADING', 'HISTORICAL', or 'MARKET' (defaults to 'TRADING')
        """
        self.api_type = api_type
        
        # Select API key based on type
        if api_key:
            self.api_key = api_key
        elif api_type == 'HISTORICAL':
            self.api_key = config.HISTORICAL_API_KEY
        elif api_type == 'MARKET':
            self.api_key = config.MARKET_API_KEY
        else:
            self.api_key = config.TRADING_API_KEY
        
        self.username = username or config.ANGELONE_USERNAME
        self.password = password or config.ANGELONE_PASSWORD
        self.mpin = mpin or config.ANGELONE_MPIN
        self.totp_token = totp_token or config.ANGELONE_TOTP_TOKEN
        self.use_mpin = use_mpin if use_mpin is not None else config.USE_MPIN
        
        self.smart_api = None
        self.auth_token = None
        self.refresh_token = None
        self.feed_token = None
        self.authenticated = False
        
        # Initialize rate limiter (3 requests per second)
        self.rate_limiter = RateLimiter(rate=3.0, capacity=10)
        
        # Initialize cache (60 second TTL, 1000 entries max)
        self.cache = APICache(max_size=1000, ttl_seconds=60)
        
        logger.info(f"AngelOneClient initialized with rate limiting and caching ({api_type} API)")
        
    def authenticate(self):
        """
        Authenticate with AngelOne SmartAPI
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Initialize SmartConnect
            self.smart_api = SmartConnect(self.api_key)
            
            # Generate TOTP (required for SmartAPI)
            if not self.totp_token:
                logger.error("TOTP token is required for SmartAPI authentication.")
                logger.error("Please enable TOTP at: https://smartapi.angelbroking.com/enable-totp")
                logger.error("Then add ANGELONE_TOTP_TOKEN to your .env file")
                return False
            
            try:
                totp = pyotp.TOTP(self.totp_token).now()
            except Exception as e:
                logger.error(f"Invalid TOTP token: {e}")
                logger.error("Please check your ANGELONE_TOTP_TOKEN in .env file")
                return False
            
            # Determine login credential (MPIN or password)
            # According to forum: LoginByPassword is deprecated, need to use MPIN
            if self.use_mpin and self.mpin:
                logger.info("Using MPIN for authentication (recommended)")
                login_credential = self.mpin
            elif self.mpin:
                # If MPIN is provided, prefer it over password
                logger.info("MPIN found, using MPIN for authentication")
                login_credential = self.mpin
                self.use_mpin = True
            else:
                logger.warning("Using password for authentication. Consider switching to MPIN.")
                logger.warning("Note: AngelOne is migrating to MPIN-based login.")
                login_credential = self.password
            
            # Generate session
            correlation_id = "trading_bot_001"
            data = self.smart_api.generateSession(
                self.username, 
                login_credential, 
                totp
            )
            
            if data['status'] == False:
                logger.error(f"Authentication failed: {data}")
                return False
            
            # Extract tokens
            self.auth_token = data['data']['jwtToken']
            self.refresh_token = data['data']['refreshToken']
            
            # Get feed token
            self.feed_token = self.smart_api.getfeedToken()
            
            # Get user profile
            profile = self.smart_api.getProfile(self.refresh_token)
            if profile['status']:
                logger.info("Authentication successful")
                self.authenticated = True
                return True
            else:
                logger.error(f"Failed to get profile: {profile}")
                return False
                
        except Exception as e:
            logger.exception(f"Authentication error: {e}")
            return False
    
    def refresh_session(self):
        """
        Refresh the authentication session using refresh token
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        try:
            if not self.refresh_token:
                logger.error("No refresh token available. Please authenticate first.")
                return False
            
            self.smart_api.generateToken(self.refresh_token)
            logger.info("Session refreshed successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Session refresh error: {e}")
            return False
    
    def get_historical_data(self, symbol_token, exchange, interval, from_date, to_date):
        """
        Fetch historical candle data with rate limiting, caching, and retry logic.
        
        Args:
            symbol_token: Symbol token ID
            exchange: Exchange (NSE, BSE, etc.)
            interval: Time interval (ONE_MINUTE, FIVE_MINUTE, ONE_HOUR, ONE_DAY, etc.)
            from_date: Start date in format "YYYY-MM-DD HH:mm"
            to_date: End date in format "YYYY-MM-DD HH:mm"
        
        Returns:
            dict: Historical data or None if error
        """
        try:
            # Lazy authentication - authenticate only when first API call is made
            if not self.authenticated:
                logger.info("Not authenticated. Attempting authentication before API call...")
                if not self.authenticate():
                    logger.error("Authentication failed. Cannot make API call.")
                    return None
            
            # Generate cache key
            cache_key = APICache.generate_key(
                "historical_data",
                symbol_token=symbol_token,
                exchange=exchange,
                interval=interval,
                from_date=from_date,
                to_date=to_date
            )
            
            # Check cache first
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {symbol_token}")
                return cached_data
            
            # Acquire rate limit token
            if not self.rate_limiter.acquire(tokens=1, timeout=10.0):
                logger.error(f"Rate limit timeout for {symbol_token}")
                raise RateLimitError("Rate limit timeout")
            
            historic_param = {
                "exchange": exchange,
                "symboltoken": str(symbol_token),
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            # Make API call with retry logic
            @retry_with_backoff(
                max_retries=3,
                initial_delay=1.0,
                max_delay=10.0,
                exponential_base=2.0,
                retry_on=(RateLimitError, NetworkError, Exception)
            )
            def _fetch_data():
                response = self.smart_api.getCandleData(historic_param)
                
                # Check for rate limit error in response
                if isinstance(response, dict) and response.get('message'):
                    msg = str(response.get('message', '')).lower()
                    if 'rate' in msg or 'limit' in msg or 'exceeded' in msg:
                        logger.warning(f"Rate limit detected for {symbol_token}")
                        raise RateLimitError(response.get('message'))
                
                return response
            
            response = _fetch_data()
            
            if response and 'data' in response:
                data = response['data']
                # Cache the successful response
                self.cache.set(cache_key, data)
                return data
            else:
                logger.error(f"Failed to get historical data: {response}")
                return None
                
        except RateLimitError as e:
            logger.error(f"Rate limit error for {symbol_token}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error fetching historical data for {symbol_token}: {e}")
            return None
    
    def get_market_data(self, symbol_token, exchange):
        """
        Get current market data (LTP - Last Traded Price)
        
        Args:
            symbol_token: Symbol token ID
            exchange: Exchange (NSE, BSE, etc.)
        
        Returns:
            float: Current price or None if error
        """
        try:
            # Lazy authentication - authenticate only when first API call is made
            if not self.authenticated:
                logger.info("Not authenticated. Attempting authentication before API call...")
                if not self.authenticate():
                    logger.error("Authentication failed. Cannot make API call.")
                    return None
            
            # Use market quote API to get current price
            # Note: This is a simplified version. Actual implementation may vary
            # based on AngelOne API documentation
            
            # For now, we'll use historical data with latest timestamp
            # In production, use proper market data API endpoint
            from datetime import datetime, timedelta
            to_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            from_date = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            
            data = self.get_historical_data(
                symbol_token, 
                exchange, 
                "ONE_MINUTE", 
                from_date, 
                to_date
            )
            
            if data and len(data) > 0:
                # Get the last candle's close price
                last_candle = data[-1]
                if isinstance(last_candle, list) and len(last_candle) >= 4:
                    return float(last_candle[4])  # Close price is typically at index 4
                elif isinstance(last_candle, dict) and 'close' in last_candle:
                    return float(last_candle['close'])
            
            return None
            
        except Exception as e:
            logger.exception(f"Error fetching market data for {symbol_token}: {e}")
            return None
    
    def place_order(self, order_params):
        """
        Place a buy/sell order
        
        Args:
            order_params: Dictionary containing order parameters:
                - variety: "NORMAL"
                - tradingsymbol: Trading symbol (e.g., "SBIN-EQ")
                - symboltoken: Symbol token ID
                - transactiontype: "BUY" or "SELL"
                - exchange: "NSE" or "BSE"
                - ordertype: "LIMIT", "MARKET", etc.
                - producttype: "INTRADAY", "DELIVERY", etc.
                - duration: "DAY", "IOC", etc.
                - price: Order price
                - quantity: Number of shares
                - squareoff: Square off value (optional)
                - stoploss: Stop loss value (optional)
        
        Returns:
            dict: Order response with order ID or None if error
        """
        try:
            # Lazy authentication - authenticate only when first API call is made
            if not self.authenticated:
                logger.info("Not authenticated. Attempting authentication before API call...")
                if not self.authenticate():
                    logger.error("Authentication failed. Cannot make API call.")
                    return None
            
            # Ensure required fields are present
            required_fields = [
                'variety', 'tradingsymbol', 'symboltoken', 'transactiontype',
                'exchange', 'ordertype', 'producttype', 'duration', 'price', 'quantity'
            ]
            
            for field in required_fields:
                if field not in order_params:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Place order
            response = self.smart_api.placeOrderFullResponse(order_params)
            
            if response and response.get('status'):
                logger.info(f"Order placed successfully: {response}")
                return response
            else:
                logger.error(f"Order placement failed: {response}")
                return None
                
        except Exception as e:
            logger.exception(f"Error placing order: {e}")
            return None
    
    def get_order_status(self, order_id):
        """
        Get order status
        
        Args:
            order_id: Order ID
        
        Returns:
            dict: Order status or None if error
        """
        try:
            if not self.authenticated:
                logger.error("Not authenticated. Please authenticate first.")
                return None
            
            # Note: Actual implementation depends on AngelOne API
            # This is a placeholder
            logger.warning("get_order_status not fully implemented")
            return None
            
        except Exception as e:
            logger.exception(f"Error getting order status: {e}")
            return None
    
    def terminate_session(self):
        """
        Terminate the session and logout
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            if not self.smart_api:
                return True
            
            result = self.smart_api.terminateSession(self.username)
            if result:
                logger.info("Session terminated successfully")
                self.authenticated = False
                return True
            else:
                logger.error("Failed to terminate session")
                return False
                
        except Exception as e:
            logger.exception(f"Error terminating session: {e}")
            return False

