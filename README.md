# Nifty 50 EMA-Based Algorithmic Trading Bot

An algorithmic trading system that monitors Nifty 50 companies, identifies those trading 3% below their 20 EMA at market close, and automatically allocates ₹15,000 to the top 5 most fallen companies daily.

## Features

- **Automated Analysis**: Monitors all Nifty 50 companies daily
- **EMA Calculation**: Uses 20-period EMA based on daily candles
- **Smart Filtering**: Identifies companies trading 5% or more below their 20 EMA
- **Automatic Allocation**: Allocates ₹15,000 per company to top 5 eligible stocks
- **Duplicate Prevention**: Prevents allocating to the same company multiple times in a day
- **REST API**: Flask API for frontend integration
- **Scheduled Execution**: Runs automatically at 3:30 PM IST (market close)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory (already created with your credentials):

```env
# AngelOne Trading API Credentials
TRADING_API_KEY=9DYha4fz
TRADING_SECRET_KEY=07f4e644-bfba-4245-920b-fc287bfb7dd2

# AngelOne Historical API Credentials
HISTORICAL_API_KEY=GEa34V7A
HISTORICAL_SECRET_KEY=bd409a72-8ea4-44e3-b656-be829af41674

# AngelOne Market API Credentials
MARKET_API_KEY=7TmcRllV
MARKET_SECRET_KEY=1a02e75d-1a1f-4f9a-96fb-e8a9e4107393

# AngelOne Account Credentials
ANGELONE_USERNAME=anubhavrajput572@gmail.com
ANGELONE_PASSWORD=Anubhav@123
ANGELONE_TOTP_TOKEN=  # See TOTP_SETUP_GUIDE.md for setup instructions
```

**Important**: You need to enable TOTP for SmartAPI authentication. See `TOTP_SETUP_GUIDE.md` for detailed instructions.

**Important**: 
- Replace `your_client_code` with your AngelOne client code
- Replace `your_pin` with your AngelOne PIN
- Replace `your_qr_code_token` with the TOTP token from your QR code (for 2FA)

### 3. Update Nifty 50 Symbols

The `data/nifty50_symbols.json` file contains Nifty 50 companies with their symbol tokens. You may need to verify and update the token IDs to match your AngelOne account.

## Usage

### Start the Trading Bot

```bash
python main.py
```

The bot will:
1. Authenticate with AngelOne
2. Start the scheduler (runs daily at 3:30 PM IST)
3. Start the Flask API server (available at `http://localhost:5000`)

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/eligible-companies` - Get all companies currently eligible (3% below EMA)
- `GET /api/allocated-today` - Get companies allocated today
- `GET /api/orders` - Get order history
- `GET /api/status` - Get system status and last execution time
- `GET /api/top-stocks?limit=5` - Get top N eligible stocks
- `POST /api/run-now` - Manually trigger the algorithm (for testing)

## Configuration

Edit `config/config.py` to customize:

- **Capital Settings**: `TOTAL_CAPITAL` (default: ₹3,00,000), `ALLOCATION_PER_COMPANY` (default: ₹15,000)
- **Market Timing**: `MARKET_CLOSE_HOUR` (default: 15), `MARKET_CLOSE_MINUTE` (default: 30)
- **EMA Parameters**: `EMA_PERIOD` (default: 20), `EMA_TIMEFRAME` (default: "ONE_DAY")
- **Trading Threshold**: `FALL_THRESHOLD` (default: 5.0%)
- **Order Settings**: Product type, duration, etc.

## How It Works

1. **Daily at 3:30 PM IST**: The scheduler triggers the algorithm
2. **Stock Analysis**: 
   - Fetches hourly candle data for all Nifty 50 companies
   - Calculates 20-period EMA for each stock
   - Identifies stocks trading 5% or more below their EMA
3. **Selection**: Sorts eligible stocks by fall percentage and selects top 5
4. **Order Placement**: 
   - Checks if company was already allocated today (prevents duplicates)
   - Calculates quantity: ₹15,000 / current_price
   - Places LIMIT buy orders
5. **Tracking**: Records all allocations in `data/daily_allocations.json`

## File Structure

```
tradingBOT/
├── config/
│   └── config.py              # Configuration settings
├── src/
│   ├── angelone_client.py     # AngelOne API wrapper
│   ├── nifty50_fetcher.py    # Nifty 50 company list
│   ├── ema_calculator.py     # EMA calculation
│   ├── stock_analyzer.py     # Stock analysis logic
│   ├── order_manager.py      # Order placement
│   ├── allocation_tracker.py # Daily allocation tracking
│   └── scheduler.py          # Daily scheduler
├── api/
│   └── flask_api.py          # Flask REST API
├── data/
│   ├── nifty50_symbols.json # Nifty 50 company data
│   └── daily_allocations.json # Allocation history
├── requirements.txt          # Python dependencies
├── main.py                   # Main entry point
└── README.md                # This file
```

## Important Notes

- **Testing**: Test with small amounts first before deploying with full capital
- **Token IDs**: Verify symbol token IDs in `nifty50_symbols.json` match your AngelOne account
- **Market Hours**: Algorithm runs at market close (3:30 PM IST). Ensure market is open for order placement
- **Error Handling**: Check logs for any API errors or authentication issues
- **Rate Limits**: Be aware of AngelOne API rate limits

## Troubleshooting

1. **Authentication Failed**: 
   - Verify credentials in `.env` file
   - Ensure TOTP token is correct
   - Check if 2FA is enabled on your account

2. **No Eligible Stocks**: 
   - This is normal if no stocks meet the 5% threshold
   - Check market conditions

3. **Order Placement Failed**:
   - Verify sufficient funds
   - Check if market is open
   - Verify symbol tokens are correct

## Deployment

This project can be deployed to:
- **Frontend**: Vercel (React app in `automatic_trading/`)
- **Backend**: Render (Flask API)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## License

This project is for educational purposes. Use at your own risk.

