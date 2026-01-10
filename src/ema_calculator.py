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


class EMACalculator:
    """Calculates EMA for stocks"""
    
    def __init__(self, angelone_client):
        """
        Initialize EMA calculator
        
        Args:
            angelone_client: AngelOneClient instance
        """
        self.client = angelone_client
        self.ema_period = config.EMA_PERIOD
    
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
    
    def get_ema_for_symbol(self, symbol_token, exchange, hours_back=25):
        """
        Get EMA and current price for a symbol
        
        Args:
            symbol_token: Symbol token ID
            exchange: Exchange (NSE, BSE)
            hours_back: Number of hours of historical data to fetch (default: 25 to ensure 20+ data points)
        
        Returns:
            dict: {
                'ema': float,
                'current_price': float,
                'data_points': int,
                'success': bool
            }
        """
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(hours=hours_back)
            
            # Format dates for API
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            # Fetch historical data
            historical_data = self.client.get_historical_data(
                symbol_token=symbol_token,
                exchange=exchange,
                interval=config.EMA_TIMEFRAME,
                from_date=from_date_str,
                to_date=to_date_str
            )
            
            if not historical_data:
                logger.warning(f"No historical data for token {symbol_token}")
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
            
            for candle in historical_data:
                if isinstance(candle, list) and len(candle) >= 5:
                    # Candle format: [timestamp, open, high, low, close, volume]
                    close_price = float(candle[4])  # Close price at index 4
                    closing_prices.append(close_price)
                    current_price = close_price  # Last candle's close is current price
                elif isinstance(candle, dict):
                    # If data is in dict format
                    if 'close' in candle:
                        close_price = float(candle['close'])
                        closing_prices.append(close_price)
                        current_price = close_price
            
            if len(closing_prices) < self.ema_period:
                logger.warning(
                    f"Insufficient data points for token {symbol_token}: "
                    f"{len(closing_prices)} < {self.ema_period}"
                )
                return {
                    'ema': None,
                    'current_price': current_price,
                    'data_points': len(closing_prices),
                    'success': False
                }
            
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

