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
import time


class Backtester:
    """Simulates trading algorithm for historical dates"""
    
    def __init__(self, angelone_client):
        """
        Initialize backtester
        
        Args:
            angelone_client: AngelOneClient instance (for reference, we'll create separate clients)
        """
        # Use the provided client if HISTORICAL/MARKET clients fail
        self.fallback_client = angelone_client
        
        # Create separate clients for Historical and Market APIs
        self.historical_client = None
        self.market_client = None
        
        try:
            self.historical_client = AngelOneClient(api_type='HISTORICAL')
            # DON'T authenticate on initialization - use lazy authentication
            # Authentication will happen automatically on first API call
            logger.info("Historical API client initialized (lazy authentication)")
            self.historical_client = self.historical_client
        except Exception as e:
            logger.warning(f"Failed to initialize Historical client: {e}. Will use fallback client.")
            self.historical_client = None
        
        try:
            self.market_client = AngelOneClient(api_type='MARKET')
            # DON'T authenticate on initialization - use lazy authentication
            # Authentication will happen automatically on first API call
            logger.info("Market API client initialized (lazy authentication)")
            self.market_client = self.market_client
        except Exception as e:
            logger.warning(f"Failed to initialize Market client: {e}. Will use fallback client.")
            self.market_client = None
        
        # Use fallback client if HISTORICAL client is not available
        if self.historical_client is None:
            logger.info("Using fallback client for historical data")
            self.historical_client = self.fallback_client
        
        if self.market_client is None:
            logger.info("Using fallback client for market data")
            self.market_client = self.fallback_client
        
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
            
            # Calculate date range for historical data
            # For daily candles: Need at least 20 trading days, so fetch 50 calendar days
            to_date = target_date.replace(hour=15, minute=30)  # Market close time
            from_date = to_date - timedelta(days=50)  # 50 days back to ensure enough trading days
            
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            logger.info(f"Fetching historical data from {from_date_str} to {to_date_str} using {config.EMA_TIMEFRAME} timeframe")
            
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
                    
                    # Check if meets threshold (>= 3%)
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
                        logger.debug(
                            f"✓ {symbol}: Price={current_price:.2f}, EMA={ema:.2f}, "
                            f"Fall={fall_percentage:.2f}% (ELIGIBLE)"
                        )
                        
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
            start_date: Start date (default: today)
        
        Returns:
            dict: Complete backtest results
        """
        try:
            logger.info(f"Starting backtest for {days} days...")
            
            # Calculate dates (excluding weekends)
            if start_date is None:
                start_date = datetime.now(pytz.timezone(config.MARKET_TIMEZONE))
            
            # Go backward from start_date to get past trading days
            dates = []
            current_date = start_date - timedelta(days=1)  # Start from yesterday
            days_checked = 0
            max_days_to_check = days * 3  # Check up to 3x days to account for weekends
            
            # Get last N trading days (excluding weekends and today)
            while len(dates) < days and days_checked < max_days_to_check:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() < 5:  # Monday=0, Friday=4
                    dates.append(current_date)
                current_date -= timedelta(days=1)  # Go backward
                days_checked += 1
            
            # Reverse to get chronological order (oldest first)
            dates.reverse()
            
            if len(dates) == 0:
                logger.warning("No trading days found in the specified range")
                return {
                    'error': 'No trading days found',
                    'period': 'N/A',
                    'total_days': 0,
                    'simulated_days': 0,
                    'total_orders': 0,
                    'total_allocated': 0,
                    'average_daily_allocation': 0,
                    'unique_stocks': 0,
                    'average_orders_per_day': 0,
                    'results': []
                }
            
            logger.info(f"Backtesting dates: {[d.strftime('%Y-%m-%d') for d in dates]}")
            
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
            error_msg = str(e)
            if not self.historical_client or not self.historical_client.authenticated:
                error_msg = "Historical API authentication required. Please check HISTORICAL_API_KEY and HISTORICAL_SECRET_KEY in environment variables."
            return {
                'error': error_msg,
                'period': 'N/A',
                'total_days': 0,
                'simulated_days': 0,
                'total_orders': 0,
                'total_allocated': 0,
                'average_daily_allocation': 0,
                'unique_stocks': 0,
                'average_orders_per_day': 0,
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
            
            # Also save to a "latest" file for easy access
            latest_filename = "data/backtest_results_latest.json"
            with open(latest_filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Latest backtest results saved to {latest_filename}")
            
            # Save backtest orders separately for dashboard display
            self._save_backtest_orders(results)
            
            return filename
            
        except Exception as e:
            logger.exception(f"Error saving results: {e}")
            return None
    
    def _save_backtest_orders(self, results):
        """
        Save backtest orders to a separate file for dashboard display
        
        Args:
            results: Backtest results dictionary
        """
        try:
            orders_file = "data/backtest_orders.json"
            
            # Extract all orders from results
            all_orders = []
            order_id = 1
            
            if 'results' in results:
                for day_result in results['results']:
                    if 'orders' in day_result and not day_result.get('error'):
                        for order in day_result['orders']:
                            all_orders.append({
                                'id': f"backtest_{order_id}",
                                'order_id': f"backtest_{order_id}",
                                'timestamp': f"{order['date']}T15:30:00",  # Market close time
                                'date': order['date'],
                                'symbol': order['symbol'],
                                'name': order.get('name', order['symbol']),
                                'quantity': order['quantity'],
                                'price': order['price'],
                                'amount': order['amount'],
                                'status': 'backtest',
                                'ema': order.get('ema', 0),
                                'fall_percentage': order.get('fall_percentage', 0)
                            })
                            order_id += 1
            
            # Save to file
            with open(orders_file, 'w') as f:
                json.dump(all_orders, f, indent=2)
            
            logger.info(f"Saved {len(all_orders)} backtest orders to {orders_file}")
            
        except Exception as e:
            logger.exception(f"Error saving backtest orders: {e}")


