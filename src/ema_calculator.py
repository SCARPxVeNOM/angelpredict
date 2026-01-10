"""
EMA Calculator
Calculates 20-period Exponential Moving Average from hourly candle data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from logzero import logger
from config import config
from src.angelone_client import AngelOneClient
import time


class EMACalculator:
    """Calculates EMA for stocks"""
    
    def __init__(self, angelone_client):
        """
        Initialize EMA calculator
        
        Args:
            angelone_client: AngelOneClient instance (can be TRADING, HISTORICAL, or MARKET type)
        """
        self.client = angelone_client
        self.ema_period = config.EMA_PERIOD
        # Try to use HISTORICAL client for better historical data access
        # If the passed client is already HISTORICAL type, use it; otherwise create a new one
        if angelone_client.api_type != 'HISTORICAL':
            try:
                from src.angelone_client import AngelOneClient
                self.historical_client = AngelOneClient(api_type='HISTORICAL')
                # DON'T authenticate on initialization - use lazy authentication
                # Authentication will happen automatically on first API call
                logger.info("HISTORICAL API client initialized (lazy authentication)")
                self.client = self.historical_client
            except Exception as e:
                logger.warning(f"Could not create HISTORICAL client, using provided client: {e}")
                self.historical_client = None
        else:
            self.historical_client = None
    
    def calculate_ema(self, prices):
        """
        Calculate EMA from a list of prices
        
        Args:
            prices: List of closing prices
        
        Returns:
            float: EMA value or None if insufficient data
        """
        try:
            if len(prices) < self.ema_period:
                logger.warning(f"Insufficient data points: {len(prices)} < {self.ema_period}")
                return None
            
            # Convert to pandas Series for easier calculation
            series = pd.Series(prices)
            
            # Calculate EMA using pandas
            ema = series.ewm(span=self.ema_period, adjust=False).mean()
            
            # Return the last EMA value
            return float(ema.iloc[-1])
            
        except Exception as e:
            logger.exception(f"Error calculating EMA: {e}")
            return None
    
    def get_ema_for_symbol(self, symbol_token, exchange, days_back=30):
        """
        Get EMA and current price for a symbol
        
        Args:
            symbol_token: Symbol token ID
            exchange: Exchange (NSE, BSE)
            days_back: Number of days of historical data to fetch (default: 30 to ensure enough data)
                      Market is open ~6.5 hours/day, so 30 days = ~195 hourly candles (more than enough)
        
        Returns:
            dict: {
                'ema': float,
                'current_price': float,
                'data_points': int,
                'success': bool
            }
        """
        try:
            # Calculate date range - fetch more days to account for weekends/holidays
            # Market hours: 9:15 AM to 3:30 PM IST (~6.5 hours/day)
            # Using 30 days ensures we have enough data even with weekends/holidays
            # This gives us ~195 trading hours (30 days * 6.5 hours) which is more than enough
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            # Format dates for API
            # Set from_date to market open time (9:15 AM) to ensure we capture full trading day
            from_date = from_date.replace(hour=9, minute=15, second=0, microsecond=0)
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            logger.debug(f"Fetching historical data for token {symbol_token}: {from_date_str} to {to_date_str}")
            
            # Fetch historical data with the configured timeframe
            historical_data = self.client.get_historical_data(
                symbol_token=symbol_token,
                exchange=exchange,
                interval=config.EMA_TIMEFRAME,
                from_date=from_date_str,
                to_date=to_date_str
            )
            
            if not historical_data:
                logger.warning(
                    f"No historical data for token {symbol_token} using {config.EMA_TIMEFRAME} timeframe. "
                    f"Date range: {from_date_str} to {to_date_str}"
                )
                # Try fallback to daily candles if hourly doesn't work
                if config.EMA_TIMEFRAME != "ONE_DAY":
                    logger.info(f"Attempting fallback to ONE_DAY timeframe for token {symbol_token}")
                    historical_data = self.client.get_historical_data(
                        symbol_token=symbol_token,
                        exchange=exchange,
                        interval="ONE_DAY",
                        from_date=from_date_str,
                        to_date=to_date_str
                    )
                    
                    if historical_data:
                        logger.info(f"Fallback to ONE_DAY returned {len(historical_data)} candles for token {symbol_token}")
                        if len(historical_data) >= self.ema_period:
                            logger.info(f"Successfully fetched {len(historical_data)} daily candles for token {symbol_token}")
                        else:
                            logger.warning(
                                f"Fallback to ONE_DAY returned insufficient data for token {symbol_token}: "
                                f"{len(historical_data)} < {self.ema_period}. "
                                f"Date range: {from_date_str} to {to_date_str}. "
                                f"This might indicate the token is invalid, delisted, or API has no data for this period."
                            )
                            return {
                                'ema': None,
                                'current_price': None,
                                'data_points': len(historical_data),
                                'success': False
                            }
                    else:
                        logger.warning(
                            f"Fallback to ONE_DAY also failed for token {symbol_token} - no data returned. "
                            f"Date range: {from_date_str} to {to_date_str}. "
                            f"This might indicate the token is invalid, delisted, or API has no data."
                        )
                        return {
                            'ema': None,
                            'current_price': None,
                            'data_points': 0,
                            'success': False
                        }
                else:
                    return {
                        'ema': None,
                        'current_price': None,
                        'data_points': 0,
                        'success': False
                    }
            
            # Parse candle data
            # Format: [timestamp, open, high, low, close, volume]
            closing_prices = []
            current_price = None
            
            logger.debug(f"Received {len(historical_data)} candles for token {symbol_token}")
            
            for candle in historical_data:
                if isinstance(candle, list) and len(candle) >= 5:
                    # Candle format: [timestamp, open, high, low, close, volume]
                    try:
                        close_price = float(candle[4])  # Close price at index 4
                        closing_prices.append(close_price)
                        current_price = close_price  # Last candle's close is current price
                    except (ValueError, IndexError, TypeError) as e:
                        logger.warning(f"Error parsing candle data: {candle}, error: {e}")
                        continue
                elif isinstance(candle, dict):
                    # If data is in dict format
                    try:
                        if 'close' in candle:
                            close_price = float(candle['close'])
                            closing_prices.append(close_price)
                            current_price = close_price
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing candle dict: {candle}, error: {e}")
                        continue
                else:
                    logger.warning(f"Unexpected candle format: {type(candle)}, value: {candle}")
            
            logger.debug(f"Parsed {len(closing_prices)} closing prices for token {symbol_token}")
            
            # If we don't have enough data points, try fallback to daily candles
            if len(closing_prices) < self.ema_period:
                logger.warning(
                    f"Insufficient data points for token {symbol_token}: "
                    f"{len(closing_prices)} < {self.ema_period} using {config.EMA_TIMEFRAME} timeframe. "
                    f"Date range: {from_date_str} to {to_date_str}. "
                    f"Attempting fallback to ONE_DAY timeframe."
                )
                
                # Try fallback to daily candles if we're using hourly
                if config.EMA_TIMEFRAME != "ONE_DAY":
                    logger.info(f"Attempting fallback to ONE_DAY timeframe for token {symbol_token}")
                    daily_data = self.client.get_historical_data(
                        symbol_token=symbol_token,
                        exchange=exchange,
                        interval="ONE_DAY",
                        from_date=from_date_str,
                        to_date=to_date_str
                    )
                    
                    if daily_data and len(daily_data) >= self.ema_period:
                        logger.info(f"Successfully fetched {len(daily_data)} daily candles for token {symbol_token}")
                        # Parse daily candles
                        closing_prices = []
                        for candle in daily_data:
                            if isinstance(candle, list) and len(candle) >= 5:
                                try:
                                    close_price = float(candle[4])
                                    closing_prices.append(close_price)
                                    current_price = close_price
                                except (ValueError, IndexError, TypeError):
                                    continue
                            elif isinstance(candle, dict) and 'close' in candle:
                                try:
                                    close_price = float(candle['close'])
                                    closing_prices.append(close_price)
                                    current_price = close_price
                                except (ValueError, TypeError):
                                    continue
                        
                        # Check again after parsing daily candles
                        if len(closing_prices) < self.ema_period:
                            logger.warning(
                                f"Insufficient daily candles for token {symbol_token}: "
                                f"{len(closing_prices)} < {self.ema_period}"
                            )
                            return {
                                'ema': None,
                                'current_price': current_price,
                                'data_points': len(closing_prices),
                                'success': False
                            }
                    else:
                        logger.warning(
                            f"Fallback to ONE_DAY also insufficient for token {symbol_token}: "
                            f"{len(daily_data) if daily_data else 0} candles received"
                        )
                        return {
                            'ema': None,
                            'current_price': current_price if 'current_price' in locals() else None,
                            'data_points': len(closing_prices),
                            'success': False
                        }
                else:
                    # Already using daily candles, no fallback available
                    return {
                        'ema': None,
                        'current_price': current_price,
                        'data_points': len(closing_prices),
                        'success': False
                    }
            
            logger.debug(
                f"Token {symbol_token}: Received {len(closing_prices)} data points "
                f"(need {self.ema_period} for EMA calculation)"
            )
            
            # Calculate EMA
            ema_value = self.calculate_ema(closing_prices)
            
            if ema_value is None:
                return {
                    'ema': None,
                    'current_price': current_price,
                    'data_points': len(closing_prices),
                    'success': False
                }
            
            return {
                'ema': ema_value,
                'current_price': current_price,
                'data_points': len(closing_prices),
                'success': True
            }
            
        except Exception as e:
            logger.exception(f"Error getting EMA for token {symbol_token}: {e}")
            return {
                'ema': None,
                'current_price': None,
                'data_points': 0,
                'success': False
            }
    
    def get_price_below_ema_percentage(self, ema, current_price):
        """
        Calculate percentage by which current price is below EMA
        
        Args:
            ema: EMA value
            current_price: Current price
        
        Returns:
            float: Percentage below EMA (positive if below, negative if above)
        """
        try:
            if ema is None or current_price is None or ema == 0:
                return None
            
            # Calculate percentage: ((EMA - Price) / EMA) * 100
            percentage = ((ema - current_price) / ema) * 100
            return percentage
            
        except Exception as e:
            logger.exception(f"Error calculating percentage: {e}")
            return None



