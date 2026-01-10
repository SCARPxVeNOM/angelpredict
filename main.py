"""
Main Entry Point
Initializes AngelOne client, starts Flask API server and scheduler
"""
import signal
import sys
from logzero import logger
from config import config
from src.angelone_client import AngelOneClient
from src.scheduler import TradingScheduler
from api.flask_api import TradingAPI


class TradingBot:
    """Main trading bot application"""
    
    def __init__(self):
        """Initialize trading bot"""
        self.client = None
        self.scheduler = None
        self.api = None
        self.running = False
    
    def initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing Trading Bot...")
            
            # Initialize AngelOne client
            logger.info("Initializing AngelOne client...")
            self.client = AngelOneClient()
            
            # Authenticate
            logger.info("Authenticating with AngelOne...")
            if not self.client.authenticate():
                logger.warning("Authentication failed. The bot will continue but may have limited functionality.")
                logger.warning("Note: Some features require authentication. Check your credentials in .env file")
                # Don't return False - allow bot to run in limited mode
                # return False
            
            # Initialize scheduler
            logger.info("Initializing scheduler...")
            self.scheduler = TradingScheduler(self.client)
            
            # Initialize Flask API
            logger.info("Initializing Flask API...")
            self.api = TradingAPI(self.client, self.scheduler)
            
            logger.info("Trading Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.exception(f"Error initializing trading bot: {e}")
            return False
    
    def start(self):
        """Start the trading bot"""
        try:
            if not self.initialize():
                logger.error("Failed to initialize trading bot")
                return False
            
            # DON'T start scheduler automatically - only manual execution via API
            logger.info("Scheduler initialized but NOT started (manual execution only)")
            logger.info("Use POST /api/run-now to manually trigger the algorithm")
            # self.scheduler.start()  # DISABLED - no automatic execution
            
            # Start Flask API server (runs in main thread)
            logger.info("Starting Flask API server...")
            logger.info(f"API will be available at http://{config.FLASK_HOST}:{config.FLASK_PORT}")
            logger.info("API Endpoints:")
            logger.info("  GET  /api/health - Health check")
            logger.info("  GET  /api/eligible-companies - Get eligible companies")
            logger.info("  GET  /api/allocated-today - Get today's allocations")
            logger.info("  GET  /api/orders - Get order history")
            logger.info("  GET  /api/status - Get system status")
            logger.info("  GET  /api/top-stocks - Get top N stocks")
            logger.info("  POST /api/run-now - Manually trigger algorithm")
            logger.info("  POST /api/backtest - Run backtest simulation")
            
            self.running = True
            
            # Run Flask server (blocking)
            self.api.run()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            self.stop()
        except Exception as e:
            logger.exception(f"Error starting trading bot: {e}")
            self.stop()
    
    def stop(self):
        """Stop the trading bot"""
        try:
            logger.info("Stopping Trading Bot...")
            
            if self.scheduler:
                self.scheduler.stop()
            
            if self.client:
                self.client.terminate_session()
            
            self.running = False
            logger.info("Trading Bot stopped")
            
        except Exception as e:
            logger.exception(f"Error stopping trading bot: {e}")


def signal_handler(sig, frame):
    """Handle interrupt signals"""
    logger.info("Interrupt signal received")
    if bot:
        bot.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start bot
    bot = TradingBot()
    bot.start()

