# Timeframe Changed: Hourly → Daily Candles ✅

## Change Applied

Changed the EMA calculation from **hourly candles** to **daily candles**.

### Before
```python
EMA_TIMEFRAME = "ONE_HOUR"  # Hourly candles
```

### After
```python
EMA_TIMEFRAME = "ONE_DAY"  # Daily candles
```

## Why This is Better

### 1. Matches Your Chart
Your TradingView chart shows **daily candles** with a **20-day EMA** (the blue line). Now the algorithm will calculate the same 20-day EMA that you see on the chart!

### 2. More Accurate
- **Before**: 20-period EMA of hourly candles (last 20 hours)
- **After**: 20-period EMA of daily candles (last 20 days)

The daily EMA is what traders typically use and what you see on daily charts.

### 3. Better Data Availability
- Daily candles are more reliable from the API
- Less likely to have missing data
- Matches standard technical analysis

## How It Works Now

### Step 1: Fetch Daily Candles
- Gets last 30 days of **daily candles** for each stock
- This gives 30 data points (more than enough for 20-day EMA)

### Step 2: Calculate 20-Day EMA
- Calculates the 20-period EMA from daily closing prices
- This is the **blue line** on your daily chart

### Step 3: Compare to Current Price
- Gets today's closing price
- Calculates: `((20-Day EMA - Current Price) / 20-Day EMA) × 100`

### Step 4: Filter by 3%
- If price is ≥3% below the 20-day EMA → ELIGIBLE
- If price is <3% below the 20-day EMA → NOT eligible

## Example with Reliance

Looking at your chart:
- Current Price: ₹1,462.35
- 20-Day EMA (blue line): ~₹1,510 (estimated from chart)
- Drop: ((1510 - 1462.35) / 1510) × 100 = **3.15%** ✅

**Result**: Reliance SHOULD appear in the scan (if the actual 20-day EMA is around ₹1,510)

## Configuration

```python
# config/config.py
FALL_THRESHOLD = 3.0        # 3% below EMA
EMA_PERIOD = 20             # 20-period EMA
EMA_TIMEFRAME = "ONE_DAY"   # Daily candles ✅
```

## Expected Results

After deployment, the scan will now:
1. ✅ Calculate 20-day EMA (matches your chart)
2. ✅ Find stocks 3%+ below that EMA
3. ✅ Show results that match what you see on daily charts

## Why This Fixes the Issue

**Before (Hourly)**:
- 20-hour EMA ≠ 20-day EMA
- Hourly EMA changes throughout the day
- Doesn't match daily charts

**After (Daily)**:
- 20-day EMA = what you see on charts
- Stable calculation (only changes once per day)
- Matches standard technical analysis

## Deploy & Test

```bash
git add .
git commit -m "Change EMA timeframe from hourly to daily candles"
git push origin main
```

After deployment:
1. Click "Scan Now"
2. Check Render logs
3. Should see stocks that match your daily chart analysis
4. Reliance should appear if it's 3%+ below the 20-day EMA

## Summary

✅ **Timeframe**: Daily candles (was hourly)  
✅ **EMA Period**: 20 days  
✅ **Threshold**: 3% below EMA  
✅ **Matches**: Your TradingView daily chart  

This is the correct configuration for daily trading based on 20-day EMA!
