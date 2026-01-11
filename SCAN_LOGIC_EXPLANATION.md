# Scan Logic Explanation: Why Reliance Might Not Appear

## Understanding the Difference

### What the Chart Shows
The chart shows **-4.82% drop from previous close**:
- Previous Close: ₹1,533.20
- Current Price: ₹1,462.35
- Drop: -70.85 points (-4.82%)

This is the **daily price change**.

### What the Algorithm Checks
The algorithm checks if the price is **3% below the 20 EMA** (the blue line on the chart):
- Current Price: ₹1,462.35
- 20 EMA: ₹? (need to calculate from hourly candles)
- Drop from EMA: ? %

This is the **distance from the moving average**.

## Key Difference

**These are TWO DIFFERENT metrics:**

1. **Daily Drop** = (Previous Close - Current Price) / Previous Close × 100
   - Compares today's price to yesterday's close
   - What you see on the chart: -4.82%

2. **EMA Drop** = (20 EMA - Current Price) / 20 EMA × 100
   - Compares current price to the 20-period moving average
   - What the algorithm checks: ? %

## Why Reliance Might Not Appear

Looking at the chart, the **blue EMA line** appears to be around ₹1,480-1,500.

If EMA = ₹1,490, then:
- EMA Drop = (1490 - 1462.35) / 1490 × 100 = **1.86%**
- This is **LESS than 3%**, so it won't appear!

If EMA = ₹1,510, then:
- EMA Drop = (1510 - 1462.35) / 1510 × 100 = **3.15%**
- This is **MORE than 3%**, so it WILL appear!

## The Algorithm is Correct

The algorithm is working as designed:
- ✅ It calculates the 20-period EMA from hourly candles
- ✅ It compares current price to that EMA
- ✅ It selects stocks that are ≥3% below the EMA

## Why This Makes Sense

The algorithm uses EMA (not daily drop) because:

1. **EMA is a trend indicator** - Shows the average price over 20 periods
2. **Daily drop can be misleading** - A stock can drop 5% but still be above its EMA (uptrend)
3. **EMA drop indicates oversold** - When price is significantly below EMA, it might bounce back

## Example Scenarios

### Scenario 1: Stock in Uptrend
- Previous Close: ₹100
- Current Price: ₹95 (5% daily drop)
- 20 EMA: ₹90 (stock has been rising)
- EMA Drop: (90 - 95) / 90 = **-5.5%** (price is ABOVE EMA)
- **Result**: NOT eligible (price above EMA despite daily drop)

### Scenario 2: Stock in Downtrend
- Previous Close: ₹100
- Current Price: ₹98 (2% daily drop)
- 20 EMA: ₹105 (stock has been falling)
- EMA Drop: (105 - 98) / 105 = **6.7%** (price is BELOW EMA)
- **Result**: ELIGIBLE (price significantly below EMA)

## How to Check Reliance

Run the test script to see the actual EMA value:

```bash
python test_reliance_scan.py
```

This will show:
- Current Price
- 20 EMA value
- Actual percentage below EMA
- Whether it's eligible or not

## What to Look For

On the chart:
1. Find the **blue EMA line** (20-period moving average)
2. Compare current price to that line
3. If price is **3% or more below the blue line**, it will appear in scan

## Possible Reasons Reliance Doesn't Appear

1. **EMA is lower than expected** - Price might only be 1-2% below EMA
2. **Recent uptrend** - EMA hasn't caught up to recent price increases
3. **Insufficient data** - API might not have enough hourly candles
4. **API authentication issue** - Can't fetch historical data

## How to Fix

### Option 1: Check the Actual EMA Value
Run the test script to see what the algorithm is calculating.

### Option 2: Adjust the Threshold
If you want to catch stocks with smaller drops, change the threshold:
```python
# In config/config.py
FALL_THRESHOLD = 2.0  # Change from 3.0 to 2.0
```

### Option 3: Use Daily Drop Instead
If you prefer to use daily drop % instead of EMA drop %, we need to modify the algorithm logic.

## Recommendation

**First, run the test script** to see what's actually happening:

```bash
python test_reliance_scan.py
```

This will tell us:
- What the 20 EMA value is
- What the actual drop percentage is
- Why Reliance is or isn't appearing

Then we can decide if:
- The logic is correct (and Reliance just isn't 3% below EMA)
- The threshold needs adjustment
- The logic needs to be changed

---

**Next Step**: Run `python test_reliance_scan.py` and share the output!
