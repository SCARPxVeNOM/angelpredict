# Backtest Logic Update

## Overview
Updated the backtester to use the same logic as the "Scan Now" feature for consistency.

## Changes Made

### 1. Historical Data Fetching (`src/backtester.py`)

**Before:**
```python
# Fetched only 25 hours of data
from_date = to_date - timedelta(hours=25)
```

**After:**
```python
# Fetch 50 calendar days to ensure enough trading days for daily EMA
from_date = to_date - timedelta(days=50)  # ~35 trading days
```

### 2. Timeframe Configuration

The backtester now automatically uses:
- **EMA Timeframe**: `config.EMA_TIMEFRAME` (ONE_DAY - daily candles)
- **Fall Threshold**: `config.FALL_THRESHOLD` (3.0%)
- **EMA Period**: `config.EMA_PERIOD` (20)
- **Days Back**: 50 calendar days (~35 trading days)

### 3. Enhanced Logging

Added detailed logging to show eligible stocks during backtest:
```
✓ ITC: Price=337.15, EMA=348.50, Fall=3.26% (ELIGIBLE)
✓ RELIANCE: Price=1475.58, EMA=1523.40, Fall=3.14% (ELIGIBLE)
```

## Consistency with Scan Now

Both "Scan Now" and "Run Backtest" now use identical logic:

| Feature | Scan Now | Run Backtest |
|---------|----------|--------------|
| **Timeframe** | ONE_DAY (daily) | ONE_DAY (daily) |
| **Threshold** | 3% below EMA | 3% below EMA |
| **EMA Period** | 20 days | 20 days |
| **Days Fetched** | 50 calendar days | 50 calendar days |
| **Data Points** | ~35 trading days | ~35 trading days |

## How It Works

### Scan Now (Real-Time)
1. Fetches last 50 calendar days of daily candles
2. Calculates 20-day EMA
3. Finds stocks ≥3% below EMA
4. Returns top 5 stocks

### Run Backtest (Historical)
1. For each past trading day:
   - Fetches 50 days of historical data up to that date
   - Calculates 20-day EMA as of that date
   - Finds stocks ≥3% below EMA on that date
   - Simulates allocation of top 5 stocks
2. Aggregates results across all days
3. Shows total orders, allocation, and performance

## Example Backtest Output

```json
{
  "period": "2026-01-04 to 2026-01-10",
  "total_days": 5,
  "simulated_days": 5,
  "total_orders": 23,
  "total_allocated": 69000.00,
  "average_daily_allocation": 13800.00,
  "unique_stocks": 12,
  "average_orders_per_day": 4.6,
  "results": [
    {
      "date": "2026-01-04",
      "eligible_stocks": 8,
      "selected_stocks": 5,
      "orders": [
        {
          "symbol": "ITC",
          "price": 337.15,
          "quantity": 8,
          "amount": 2697.20,
          "fall_percentage": 3.26
        }
      ],
      "total_allocated": 13485.60
    }
  ]
}
```

## Benefits

1. **Consistency**: Same logic for real-time and historical analysis
2. **Accuracy**: Uses daily candles matching user's TradingView charts
3. **Reliability**: Fetches enough data (50 days) to ensure 20-day EMA calculation
4. **Transparency**: Detailed logging shows which stocks qualify

## Testing

To test the updated backtest:

1. **Backend**: Already deployed with the fix
2. **Frontend**: Click "Run Backtest" button
3. **Verify**: Check logs show daily candles and 3% threshold
4. **Compare**: Results should match what "Scan Now" would find for those dates

## Files Modified

- `src/backtester.py` - Updated date range and logging

## Configuration

All settings are centralized in `config/config.py`:
```python
EMA_PERIOD = 20
EMA_TIMEFRAME = "ONE_DAY"  # Daily candles
FALL_THRESHOLD = 3.0  # 3% below EMA
TOTAL_ALLOCATION = 15000  # ₹15,000 total
ALLOCATION_PER_COMPANY = 3000  # ₹3,000 per company
MAX_COMPANIES = 5  # Top 5 companies
```
