"""
Quick script to run backtest simulation
Usage: python run_backtest.py [days]
"""
import sys
from src.angelone_client import AngelOneClient
from src.backtester import Backtester
from logzero import logger
import json

def main():
    # Get number of days from command line or default to 7
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    
    logger.info(f"Starting backtest for {days} days...")
    
    # Initialize client (authentication will be attempted)
    client = AngelOneClient()
    
    # Try to authenticate (may fail if credentials not set, but that's ok for simulation)
    try:
        if not client.authenticate():
            logger.warning("Authentication failed. Running simulation with mock data.")
    except Exception as e:
        logger.warning(f"Authentication error: {e}. Running simulation anyway.")
    
    # Create backtester
    backtester = Backtester(client)
    
    # Run backtest
    results = backtester.run_backtest(days=days)
    
    # Save results
    filename = backtester.save_results(results)
    
    # Print summary
    print("\n" + "="*60)
    print("BACKTEST RESULTS SUMMARY")
    print("="*60)
    print(f"Period: {results.get('period', 'N/A')}")
    print(f"Simulated Days: {results.get('simulated_days', 0)}/{results.get('total_days', 0)}")
    print(f"Total Orders: {results.get('total_orders', 0)}")
    print(f"Total Allocated: ₹{results.get('total_allocated', 0):,.2f}")
    print(f"Average Daily Allocation: ₹{results.get('average_daily_allocation', 0):,.2f}")
    print(f"Unique Stocks: {results.get('unique_stocks', 0)}")
    print(f"Average Orders/Day: {results.get('average_orders_per_day', 0):.2f}")
    print("="*60)
    print(f"\nDetailed results saved to: {filename}")
    print("\nYou can also view results in the frontend Backtest panel!")

if __name__ == "__main__":
    main()




