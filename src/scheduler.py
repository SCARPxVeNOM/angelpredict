"""
Scheduler
Schedules daily execution of trading algorithm at market close (3:30 PM IST)
"""
import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from logzero import logger
from config import config
from src.angelone_client import AngelOneClient
from src.stock_analyzer import StockAnalyzer
from src.order_manager import OrderManager
from src.allocation_tracker import AllocationTracker
from src.nifty50_fetcher import Nifty50Fetcher


class TradingScheduler:
    """Schedules and executes trading algorithm"""
    
    def __init__(self, angelone_client):
        """
        Initialize trading scheduler
        
        Args:
            angelone_client: AngelOneClient instance
        """
        self.client = angelone_client
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone(config.MARKET_TIMEZONE))
        self.allocation_tracker = AllocationTracker()
        self.nifty50_fetcher = Nifty50Fetcher()
        self.stock_analyzer = StockAnalyzer(
            angelone_client=self.client,
            nifty50_fetcher=self.nifty50_fetcher
        )
        self.order_manager = OrderManager(
            angelone_client=self.client,
            allocation_tracker=self.allocation_tracker,
            nifty50_fetcher=self.nifty50_fetcher
        )
        self.last_execution_time = None
        self.last_execution_result = None
    
    def execute_trading_algorithm(self):
        """
        Execute the main trading algorithm:
        1. Reset daily allocations if new day
        2. Fetch Nifty 50 list
        3. Analyze stocks
        4. Select top 5 eligible companies
        5. Place orders for non-allocated companies
        6. Update allocation tracker
        7. Log results
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting trading algorithm execution")
            logger.info("=" * 60)
            
            self.last_execution_time = datetime.now(pytz.timezone(config.MARKET_TIMEZONE))
            
            # Reset daily allocations if new day
            self.allocation_tracker.reset_daily_allocations()
            
            # Ensure client is authenticated (lazy authentication)
            # This will only authenticate when actually needed
            if not self.client.authenticated:
                logger.info("Client not authenticated, will authenticate on first API call")
                logger.info("Lazy authentication enabled - no API calls until data is requested")
            
            # Analyze all stocks
            logger.info("Analyzing Nifty 50 stocks...")
            eligible_stocks = self.stock_analyzer.analyze_all_stocks()
            
            if not eligible_stocks:
                logger.warning("No eligible stocks found (>= 5% below EMA)")
                self.last_execution_result = {
                    'success': True,
                    'eligible_stocks': 0,
                    'orders_placed': 0,
                    'message': 'No eligible stocks found'
                }
                return
            
            # Get top 5 stocks
            top_stocks = eligible_stocks[:config.MAX_COMPANIES]
            logger.info(f"Top {len(top_stocks)} eligible stocks:")
            for i, stock in enumerate(top_stocks, 1):
                logger.info(
                    f"  {i}. {stock['symbol']} ({stock['name']}): "
                    f"Fall={stock['fall_percentage']:.2f}%, "
                    f"Price={stock['current_price']:.2f}"
                )
            
            # Place orders
            logger.info("Placing orders...")
            order_results = self.order_manager.place_orders_for_stocks(
                top_stocks,
                max_stocks=config.MAX_COMPANIES
            )
            
            # Get order summary
            summary = self.order_manager.get_order_summary(order_results)
            
            logger.info("=" * 60)
            logger.info("Trading algorithm execution completed")
            logger.info(f"Eligible stocks: {len(eligible_stocks)}")
            logger.info(f"Orders placed: {summary['successful']}")
            logger.info(f"Orders failed: {summary['failed']}")
            logger.info(f"Total amount allocated: ₹{summary['total_amount']:.2f}")
            logger.info("=" * 60)
            
            self.last_execution_result = {
                'success': True,
                'execution_time': self.last_execution_time.isoformat(),
                'eligible_stocks': len(eligible_stocks),
                'top_stocks': top_stocks,
                'order_summary': summary,
                'orders': order_results
            }
            
        except Exception as e:
            logger.exception(f"Error executing trading algorithm: {e}")
            self.last_execution_result = {
                'success': False,
                'error': str(e),
                'execution_time': datetime.now(pytz.timezone(config.MARKET_TIMEZONE)).isoformat()
            }
    
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule daily execution at market close (3:30 PM IST)
            self.scheduler.add_job(
                func=self.execute_trading_algorithm,
                trigger=CronTrigger(
                    hour=config.MARKET_CLOSE_HOUR,
                    minute=config.MARKET_CLOSE_MINUTE,
                    timezone=pytz.timezone(config.MARKET_TIMEZONE)
                ),
                id='daily_trading_algorithm',
                name='Daily Trading Algorithm at Market Close',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info(
                f"Scheduler started. Algorithm will run daily at "
                f"{config.MARKET_CLOSE_HOUR:02d}:{config.MARKET_CLOSE_MINUTE:02d} IST"
            )
            
        except Exception as e:
            logger.exception(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.exception(f"Error stopping scheduler: {e}")
    
    def run_now(self):
        """
        Execute the algorithm immediately (for testing)
        """
        logger.info("Running algorithm immediately (manual trigger)")
        self.execute_trading_algorithm()
    
    def get_status(self):
        """
        Get scheduler status
        
        Returns:
            dict: Status information
        """
        return {
            'scheduler_running': self.scheduler.running if self.scheduler else False,
            'last_execution_time': self.last_execution_time.isoformat() if self.last_execution_time else None,
            'last_execution_result': self.last_execution_result,
            'next_run_time': self.scheduler.get_job('daily_trading_algorithm').next_run_time.isoformat() if self.scheduler and self.scheduler.get_job('daily_trading_algorithm') else None
        }





