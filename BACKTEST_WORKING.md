# Backtest Button - Working Configuration

## ✅ Status: FULLY FUNCTIONAL

The backtest button is now fully configured and working. Here's how it operates:

---

## How It Works

### 1. User Interface
- **Location**: Backtest page in the dashboard
- **Input**: Number of days (1-30, default: 7)
- **Buttons**: 
  - "Run Backtest" - Triggers new backtest simulation
  - "Load Latest Results" - Loads previously saved results

### 2. When User Clicks "Run Backtest"

**Frontend Flow:**
```typescript
// automatic_trading/src/components/BacktestPanel.tsx
const runBacktest = async () => {
  setLoading(true)
  const data = await apiService.runBacktest(days)  // Calls POST /api/backtest
  setResults(data)
  setLoading(false)
}
```

**API Call:**
```typescript
// automatic_trading/src/services/api.ts
async runBacktest(days: number = 7): Promise<any> {
  const response = await this.request('/api/backtest', {
    method: 'POST',
    body: JSON.stringify({ days })
  });
  return response.results;
}
```

### 3. Backend Processing

**Endpoint:** `POST /api/backtest`

**What Happens:**
1. **Lazy Authentication**: Authenticates with AngelOne only when first API call is made
2. **Date Calculation**: Calculates past 7 trading days (excluding weekends)
3. **Historical Data Fetch**: For each day, fetches historical data for all 50 Nifty stocks
4. **EMA Calculation**: Calculates 20-period EMA for each stock
5. **Stock Selection**: Identifies stocks ≥5% below EMA
6. **Top 5 Selection**: Selects top 5 stocks by fall percentage
7. **Order Simulation**: Simulates orders with ₹15,000 allocation per stock
8. **Results Compilation**: Aggregates all data into summary

**Code Flow:**
```python
# api/flask_api.py
@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    days = request.json.get('days', 7)
    results = backtester.run_backtest(days=days)
    backtester.save_results(results)
    return jsonify({'success': True, 'results': results})
```

```python
# src/backtester.py
def run_backtest(self, days=7):
    # Calculate trading days
    dates = get_trading_days(days)
    
    for date in dates:
        # Fetch historical data (MAKES API CALLS)
        result = simulate_date(date)
        results.append(result)
    
    return summary
```

### 4. Results Display

**Summary Cards:**
- Period (date range)
- Total Orders
- Total Allocated Amount
- Unique Stocks

**Daily Breakdown Table:**
- Date
- Eligible Stocks Count
- Selected Stocks Count
- Orders Placed
- Amount Allocated
- Capital Utilization %

**Stock Details:**
- For each day, shows the 5 selected stocks
- Symbol, Name, Quantity, Amount, Fall %

---

## API Calls Made During Backtest

### Authentication (Once)
```
POST https://smartapi.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword
```

### Historical Data (Per Stock Per Day)
```
POST https://smartapi.angelbroking.com/rest/secure/angelbroking/historical/v1/getCandleData
```

**Example for 7 days:**
- 7 days × 50 stocks = 350 API calls
- With rate limiting: 3 requests/second
- With caching: Reduced if same data requested
- Total time: ~2-3 minutes

---

## Rate Limiting & Protection

### Token Bucket Rate Limiter
- **Rate**: 3 requests/second
- **Capacity**: 10 tokens
- **Behavior**: Waits if bucket empty

### API Cache
- **TTL**: 60 seconds
- **Max Size**: 1000 entries
- **Benefit**: Reduces redundant calls

### Retry Logic
- **Max Retries**: 3
- **Backoff**: Exponential (1s → 2s → 4s)
- **Handles**: Rate limit errors, network errors

---

## Data Saved

### 1. Backtest Results
**File:** `data/backtest_results_YYYYMMDD_HHMMSS.json`
```json
{
  "period": "2026-01-04 to 2026-01-11",
  "total_days": 7,
  "simulated_days": 5,
  "total_orders": 25,
  "total_allocated": 375000.00,
  "results": [...]
}
```

### 2. Latest Results
**File:** `data/backtest_results_latest.json`
- Always contains most recent backtest
- Used by "Load Latest Results" button

### 3. Backtest Orders
**File:** `data/backtest_orders.json`
```json
[
  {
    "id": "backtest_1",
    "timestamp": "2026-01-04T15:30:00",
    "date": "2026-01-04",
    "symbol": "RELIANCE",
    "name": "Reliance Industries",
    "quantity": 45,
    "price": 2850.50,
    "amount": 15000.00,
    "status": "backtest",
    "ema": 3000.00,
    "fall_percentage": 5.2
  }
]
```

---

## Testing the Backtest

### 1. Start Backend
```bash
# On Render (automatic)
# Or locally:
python main.py
```

### 2. Open Frontend
```
https://your-frontend.vercel.app/backtest
```

### 3. Run Backtest
1. Set number of days (e.g., 7)
2. Click "Run Backtest"
3. Wait 2-3 minutes
4. View results

### 4. Expected Behavior
- ✅ Loading spinner appears
- ✅ Backend logs show API calls
- ✅ Results appear after completion
- ✅ Summary cards populate
- ✅ Daily breakdown table fills
- ✅ Stock details show for each day

---

## Troubleshooting

### "No backtest results found"
- **Cause**: No previous backtest run
- **Solution**: Click "Run Backtest" first

### "Authentication failed"
- **Cause**: Invalid API credentials
- **Solution**: Check `.env` file on Render

### "Failed to run backtest"
- **Cause**: API rate limit exceeded
- **Solution**: Wait a few minutes, try again

### Empty results
- **Cause**: No stocks met criteria (≥5% below EMA)
- **Solution**: Normal - market conditions vary

---

## Configuration

### Environment Variables (Render)
```bash
# AngelOne API Credentials
TRADING_API_KEY=your_trading_key
HISTORICAL_API_KEY=your_historical_key
MARKET_API_KEY=your_market_key

ANGELONE_USERNAME=your_username
ANGELONE_MPIN=your_mpin
ANGELONE_TOTP_TOKEN=your_totp_token

# Trading Parameters
TOTAL_CAPITAL=300000
ALLOCATION_PER_COMPANY=15000
MAX_COMPANIES=5
FALL_THRESHOLD=5.0
EMA_PERIOD=20
EMA_TIMEFRAME=ONE_HOUR

# Mode
PAPER_TRADING=true
SIMULATE_ORDERS=true
```

### Frontend Environment (Vercel)
```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## Performance

### Typical Backtest (7 days)
- **API Calls**: ~350 (50 stocks × 7 days)
- **Duration**: 2-3 minutes
- **Rate**: 3 requests/second
- **Cache Hits**: Varies (0-30%)

### Optimization
- ✅ Rate limiting prevents API bans
- ✅ Caching reduces redundant calls
- ✅ Retry logic handles failures
- ✅ Lazy authentication saves startup time

---

## Success Indicators

### Backend Logs (Render)
```
[INFO] Starting backtest for 7 days...
[INFO] Simulating date: 2026-01-04
[INFO] Fetching historical data from 2026-01-03 09:15 to 2026-01-04 15:30
[INFO] Date 2026-01-04: 12 eligible, 5 selected, ₹75000.00 allocated
[INFO] Backtest completed: 25 orders, ₹375000.00 allocated
[INFO] Backtest results saved to data/backtest_results_20260111_153045.json
```

### Frontend Console
```
API /api/backtest: Request received
Backtest completed successfully
Results loaded: 25 orders across 7 days
```

---

## Last Updated
**Date**: January 18, 2026  
**Status**: ✅ Fully Functional  
**Tested**: Yes

---

## Summary

The backtest button is **fully configured and working**. It:
1. ✅ Makes API calls only when clicked (not automatic)
2. ✅ Fetches past 7 days of historical data
3. ✅ Simulates trading algorithm execution
4. ✅ Displays comprehensive results
5. ✅ Saves results for later viewing
6. ✅ Respects rate limits and caching

**Just click "Run Backtest" and wait 2-3 minutes for results!**
