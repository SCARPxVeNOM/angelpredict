"""
Test script to debug why Reliance isn't showing up in scan
"""
from src.angelone_client import AngelOneClient
from src.stock_analyzer import StockAnalyzer
from src.nifty50_fetcher import Nifty50Fetcher
from src.ema_calculator import EMACalculator
from logzero import logger
from config import config

def test_reliance():
    """Test Reliance stock specifically"""
    
    print("\n" + "="*80)
    print("TESTING RELIANCE STOCK SCAN")
    print("="*80)
    
    # Initialize client
    print("\n1. Initializing AngelOne client...")
    client = AngelOneClient()
    
    # Initialize components
    print("2. Initializing components...")
    nifty50_fetcher = Nifty50Fetcher()
    ema_calculator = EMACalculator(client)
    stock_analyzer = StockAnalyzer(client, nifty50_fetcher, ema_calculator)
    
    # Get Reliance company info
    print("\n3. Getting Reliance company info...")
    reliance = nifty50_fetcher.get_company_by_symbol('RELIANCE')
    
    if not reliance:
        print("❌ ERROR: Reliance not found in Nifty 50 list!")
        return
    
    print(f"✓ Found: {reliance}")
    
    # Get EMA data
    print("\n4. Fetching EMA data for Reliance...")
    token = reliance.get('token')
    exchange = reliance.get('exchange', 'NSE')
    
    ema_data = ema_calculator.get_ema_for_symbol(token, exchange)
    
    print(f"\nEMA Data:")
    print(f"  Success: {ema_data['success']}")
    print(f"  Current Price: ₹{ema_data['current_price']}")
    print(f"  20 EMA: ₹{ema_data['ema']}")
    print(f"  Data Points: {ema_data['data_points']}")
    
    if not ema_data['success']:
        print("\n❌ ERROR: Failed to get EMA data!")
        return
    
    # Calculate fall percentage
    print("\n5. Calculating fall percentage...")
    fall_percentage = ema_calculator.get_price_below_ema_percentage(
        ema_data['ema'],
        ema_data['current_price']
    )
    
    print(f"\nFall Percentage: {fall_percentage:.2f}%")
    print(f"Threshold: {config.FALL_THRESHOLD}%")
    
    # Check if eligible
    print("\n6. Checking eligibility...")
    if fall_percentage >= config.FALL_THRESHOLD:
        print(f"✅ ELIGIBLE: {fall_percentage:.2f}% >= {config.FALL_THRESHOLD}%")
    else:
        print(f"❌ NOT ELIGIBLE: {fall_percentage:.2f}% < {config.FALL_THRESHOLD}%")
        print(f"\nREASON: Price is only {fall_percentage:.2f}% below EMA, needs to be >= {config.FALL_THRESHOLD}%")
    
    # Show calculation details
    print("\n7. Calculation Details:")
    print(f"  Formula: ((EMA - Price) / EMA) * 100")
    print(f"  = (({ema_data['ema']:.2f} - {ema_data['current_price']:.2f}) / {ema_data['ema']:.2f}) * 100")
    print(f"  = {fall_percentage:.2f}%")
    
    # Compare to chart drop
    print("\n8. Chart vs EMA Comparison:")
    print(f"  Chart shows: -4.82% from previous close")
    print(f"  EMA shows: {fall_percentage:.2f}% below 20 EMA")
    print(f"\n  NOTE: These are DIFFERENT metrics!")
    print(f"  - Chart drop = % change from yesterday's close")
    print(f"  - EMA drop = % below the 20-period moving average")
    
    # Run full scan
    print("\n9. Running full scan to see all eligible stocks...")
    eligible_stocks = stock_analyzer.analyze_all_stocks()
    
    print(f"\n✓ Found {len(eligible_stocks)} eligible stocks:")
    for i, stock in enumerate(eligible_stocks, 1):
        print(f"  {i}. {stock['symbol']}: {stock['fall_percentage']:.2f}% below EMA")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_reliance()
