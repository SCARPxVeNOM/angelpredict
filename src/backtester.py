"""
Backtesting Module
Simulates trading algorithm execution for past dates to evaluate performance
"""
from datetime import datetime, timedelta
import pytz
from logzero import logger
from config import config
from src.stock_analyzer import StockAnalyzer
from src.order_manager import OrderManager
from src.allocation_tracker import AllocationTracker
from src.nifty50_fetcher import Nifty50Fetcher
from src.angelone_client import AngelOneClient
from src.ema_calculator import EMACalculator
import json
import os


class Backtester:
    """Simulates trading algorithm for historical dates"""
    
    def __init__(self, angelone_client):
        """
        Initialize backtester
        
        Args:
            angelone_client: AngelOneClient instance (for reference, we'll create separate clients)
        """
        # Create separate clients for Historical and Market APIs
        self.historical_client = AngelOneClient(api_type='HISTORICAL')
        self.market_client = AngelOneClient(api_type='MARKET')
        
        # Authenticate both clients
        logger.info("Authenticating Historical API client...")
        if not self.historical_client.authenticate():
            logger.warning("Historical API authentication failed. Backtest may have limited functionality.")
        
        logger.info("Authenticating Market API client...")
        if not self.market_client.authenticate():
            logger.warning("Market API authentication failed. Backtest may have limited functionality.")
        
        self.nifty50_fetcher = Nifty50Fetcher()
        self.results = []
    
    def simulate_date(self, target_date):
        """
        Simulate algorithm execution for a specific date
        
        Args:
            target_date: datetime object for the date to simulate
        
        Returns:
            dict: Simulation results for that date
        """
        try:
            logger.info(f"Simulating date: {target_date.strftime('%Y-%m-%d')}")
            
            # Create EMA calculator with Historical API client for historical data
            ema_calculator = EMACalculator(self.historical_client)
            
            # Create stock analyzer with Historical client for historical data
            stock_analyzer = StockAnalyzer(
                angelone_client=self.historical_client,
                nifty50_fetcher=self.nifty50_fetcher,
                ema_calculator=ema_calculator
            )
            
            # Get all companies
            companies = self.nifty50_fetcher.get_all_companies()
            
            # Analyze stocks for this specific date
            eligible_stocks = []
            
            # Calculate date range for historical data (25 hours before target date)
            to_date = target_date.replace(hour=15, minute=30)  # Market close time
            from_date = to_date - timedelta(hours=25)
            
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            logger.info(f"Fetching historical data from {from_date_str} to {to_date_str}")
            
            for company in companies:
                symbol = company.get('symbol')
                name = company.get('name')
                token = company.get('token')
                exchange = company.get('exchange', 'NSE')
                
                try:
                    # Fetch historical data for this date
                    historical_data = self.historical_client.get_historical_data(
                        symbol_token=token,
                        exchange=exchange,
                        interval=config.EMA_TIMEFRAME,
                        from_date=from_date_str,
                        to_date=to_date_str
                    )
                    
                    if not historical_data or len(historical_data) < config.EMA_PERIOD:
                        continue
                    
                    # Parse candle data to get closing prices
                    closing_prices = []
                    current_price = None
                    
                    for candle in historical_data:
                        if isinstance(candle, list) and len(candle) >= 5:
                            close_price = float(candle[4])  # Close price
                            closing_prices.append(close_price)
                            current_price = close_price
                    
                    if len(closing_prices) < config.EMA_PERIOD:
                        continue
                    
                    # Calculate EMA
                    ema = ema_calculator.calculate_ema(closing_prices)
                    
                    if ema is None or current_price is None:
                        continue
                    
                    # Calculate fall percentage
                    fall_percentage = ema_calculator.get_price_below_ema_percentage(ema, current_price)
                    
                    if fall_percentage is None:
                        continue
                    
                    # Check if meets threshold (>= 5%)
                    if fall_percentage >= config.FALL_THRESHOLD:
                        eligible_stocks.append({
                            'symbol': symbol,
                            'name': name,
                            'token': token,
                            'exchange': exchange,
                            'current_price': current_price,
                            'ema': ema,
                            'fall_percentage': fall_percentage
                        })
                        
                except Exception as e:
                    logger.debug(f"Error analyzing {symbol} for {target_date.strftime('%Y-%m-%d')}: {e}")
                    continue
            
            # Sort by fall percentage (highest first)
            eligible_stocks.sort(key=lambda x: x['fall_percentage'], reverse=True)
            
            # Get top 5 stocks
            top_stocks = eligible_stocks[:config.MAX_COMPANIES]
            
            # Calculate allocation
            total_allocated = 0
            orders = []
            
            for stock in top_stocks:
                quantity = int(config.ALLOCATION_PER_COMPANY / stock['current_price'])
                amount = quantity * stock['current_price']
                total_allocated += amount
                
                orders.append({
                    'date': target_date.strftime('%Y-%m-%d'),
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'price': stock['current_price'],
                    'quantity': quantity,
                    'amount': amount,
                    'ema': stock['ema'],
                    'fall_percentage': stock['fall_percentage']
                })
            
            # Calculate metrics
            result = {
                'date': target_date.strftime('%Y-%m-%d'),
                'eligible_stocks': len(eligible_stocks),
                'selected_stocks': len(top_stocks),
                'orders': orders,
                'total_allocated': round(total_allocated, 2),
                'available_capital': round(config.TOTAL_CAPITAL - total_allocated, 2),
                'capital_utilization': round((total_allocated / config.TOTAL_CAPITAL) * 100, 2) if config.TOTAL_CAPITAL > 0 else 0
            }
            
            logger.info(
                f"Date {target_date.strftime('%Y-%m-%d')}: "
                f"{len(eligible_stocks)} eligible, {len(top_stocks)} selected, "
                f"₹{total_allocated:.2f} allocated"
            )
            
            return result
            
        except Exception as e:
            logger.exception(f"Error simulating date {target_date}: {e}")
            return {
                'date': target_date.strftime('%Y-%m-%d'),
                'error': str(e),
                'eligible_stocks': 0,
                'selected_stocks': 0,
                'orders': [],
                'total_allocated': 0
            }
    
    def run_backtest(self, days=7, start_date=None):
        """
        Run backtest for specified number of days
        
        Args:
            days: Number of days to simulate (default: 7)
            start_date: Start date (default: today - days)
        
        Returns:
            dict: Complete backtest results
        """
        try:
            logger.info(f"Starting backtest for {days} days...")
            
            # Calculate dates (excluding weekends)
            if start_date is None:
                start_date = datetime.now(pytz.timezone(config.MARKET_TIMEZONE))
            
            dates = []
            current_date = start_date - timedelta(days=days)
            
            # Get last 7 trading days (excluding weekends)
            while len(dates) < days:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() < 5:  # Monday=0, Friday=4
                    dates.append(current_date)
                current_date += timedelta(days=1)
                if current_date >= start_date:
                    break
            
            # Simulate each date
            results = []
            total_allocated = 0
            total_orders = 0
            all_stocks = set()
            
            for date in dates:
                result = self.simulate_date(date)
                results.append(result)
                
                if 'error' not in result:
                    total_allocated += result['total_allocated']
                    total_orders += len(result['orders'])
                    for order in result['orders']:
                        all_stocks.add(order['symbol'])
            
            # Calculate summary statistics
            summary = {
                'period': f"{dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}",
                'total_days': len(dates),
                'simulated_days': len([r for r in results if 'error' not in r]),
                'total_orders': total_orders,
                'total_allocated': round(total_allocated, 2),
                'average_daily_allocation': round(total_allocated / len(dates), 2) if dates else 0,
                'unique_stocks': len(all_stocks),
                'average_orders_per_day': round(total_orders / len(dates), 2) if dates else 0,
                'results': results
            }
            
            logger.info(f"Backtest completed: {total_orders} orders, ₹{total_allocated:.2f} allocated")
            
            return summary
            
        except Exception as e:
            logger.exception(f"Error running backtest: {e}")
            return {
                'error': str(e),
                'results': []
            }
    
    def save_results(self, results, filename=None):
        """
        Save backtest results to JSON file
        
        Args:
            results: Backtest results dictionary
            filename: Output filename (default: backtest_results.json)
        """
        try:
            if filename is None:
                filename = f"data/backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Backtest results saved to {filename}")
            return filename
            
        except Exception as e:
            logger.exception(f"Error saving results: {e}")
            return None

