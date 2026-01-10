"""
Stock Analyzer
Analyzes Nifty 50 stocks to find those trading 5% below their 20 EMA
"""
from logzero import logger
from config import config
from src.nifty50_fetcher import Nifty50Fetcher
from src.ema_calculator import EMACalculator


class StockAnalyzer:
    """Analyzes stocks for trading opportunities"""
    
    def __init__(self, angelone_client, nifty50_fetcher=None, ema_calculator=None):
        """
        Initialize stock analyzer
        
        Args:
            angelone_client: AngelOneClient instance
            nifty50_fetcher: Nifty50Fetcher instance (optional, will create if not provided)
            ema_calculator: EMACalculator instance (optional, will create if not provided)
        """
        self.client = angelone_client
        self.nifty50_fetcher = nifty50_fetcher or Nifty50Fetcher()
        self.ema_calculator = ema_calculator or EMACalculator(angelone_client)
        self.fall_threshold = config.FALL_THRESHOLD
    
    def analyze_all_stocks(self):
        """
        Analyze all Nifty 50 stocks and find those 5% below 20 EMA
        
        Returns:
            list: List of eligible companies sorted by fall percentage (highest first)
                Each item: {
                    'symbol': str,
                    'name': str,
                    'token': str,
                    'exchange': str,
                    'current_price': float,
                    'ema': float,
                    'fall_percentage': float
                }
        """
        eligible_stocks = []
        companies = self.nifty50_fetcher.get_all_companies()
        
        logger.info(f"Analyzing {len(companies)} Nifty 50 companies...")
        
        for company in companies:
            symbol = company.get('symbol')
            name = company.get('name')
            token = company.get('token')
            exchange = company.get('exchange', 'NSE')
            
            try:
                # Get EMA and current price
                ema_data = self.ema_calculator.get_ema_for_symbol(
                    symbol_token=token,
                    exchange=exchange
                )
                
                if not ema_data['success']:
                    logger.warning(f"Failed to get EMA data for {symbol}")
                    continue
                
                ema = ema_data['ema']
                current_price = ema_data['current_price']
                
                if ema is None or current_price is None:
                    continue
                
                # Calculate percentage below EMA
                fall_percentage = self.ema_calculator.get_price_below_ema_percentage(
                    ema, current_price
                )
                
                if fall_percentage is None:
                    continue
                
                # Check if fall percentage meets threshold (>= 5%)
                if fall_percentage >= self.fall_threshold:
                    eligible_stocks.append({
                        'symbol': symbol,
                        'name': name,
                        'token': token,
                        'exchange': exchange,
                        'current_price': current_price,
                        'ema': ema,
                        'fall_percentage': fall_percentage
                    })
                    
                    logger.info(
                        f"{symbol} ({name}): Price={current_price:.2f}, "
                        f"EMA={ema:.2f}, Fall={fall_percentage:.2f}%"
                    )
                else:
                    logger.debug(
                        f"{symbol}: Fall={fall_percentage:.2f}% "
                        f"(below threshold {self.fall_threshold}%)"
                    )
                    
            except Exception as e:
                logger.exception(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by fall percentage (highest first)
        eligible_stocks.sort(key=lambda x: x['fall_percentage'], reverse=True)
        
        logger.info(
            f"Found {len(eligible_stocks)} eligible stocks "
            f"(>= {self.fall_threshold}% below EMA)"
        )
        
        return eligible_stocks
    
    def get_top_n_stocks(self, n=5):
        """
        Get top N stocks that are 5% below EMA, sorted by fall percentage
        
        Args:
            n: Number of top stocks to return (default: 5)
        
        Returns:
            list: Top N eligible stocks
        """
        eligible_stocks = self.analyze_all_stocks()
        return eligible_stocks[:n]
    
    def analyze_single_stock(self, symbol):
        """
        Analyze a single stock
        
        Args:
            symbol: Trading symbol
        
        Returns:
            dict: Stock analysis data or None if error
        """
        company = self.nifty50_fetcher.get_company_by_symbol(symbol)
        
        if not company:
            logger.error(f"Company not found: {symbol}")
            return None
        
        token = company.get('token')
        exchange = company.get('exchange', 'NSE')
        name = company.get('name')
        
        try:
            # Get EMA and current price
            ema_data = self.ema_calculator.get_ema_for_symbol(
                symbol_token=token,
                exchange=exchange
            )
            
            if not ema_data['success']:
                return None
            
            ema = ema_data['ema']
            current_price = ema_data['current_price']
            
            if ema is None or current_price is None:
                return None
            
            # Calculate percentage below EMA
            fall_percentage = self.ema_calculator.get_price_below_ema_percentage(
                ema, current_price
            )
            
            return {
                'symbol': symbol,
                'name': name,
                'token': token,
                'exchange': exchange,
                'current_price': current_price,
                'ema': ema,
                'fall_percentage': fall_percentage,
                'is_eligible': fall_percentage >= self.fall_threshold if fall_percentage else False
            }
            
        except Exception as e:
            logger.exception(f"Error analyzing {symbol}: {e}")
            return None



