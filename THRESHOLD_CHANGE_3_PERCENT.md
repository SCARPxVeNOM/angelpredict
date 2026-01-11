# Threshold Change: 5% → 3% Below EMA

## Change Summary

Changed the trading algorithm threshold from **5% below EMA** to **3% below EMA**.

This means the system will now select stocks that are trading **3% or more** below their 20-period EMA, instead of the previous 5% threshold.

## Impact

### More Stocks Will Qualify

- **Before**: Only stocks that dropped ≥5% below EMA were selected
- **After**: Stocks that drop ≥3% below EMA will be selected

**Result**: More stocks will meet the criteria, potentially finding more trading opportunities.

### Earlier Entry Points

- **Before**: Waited for larger drops (5%)
- **After**: Enters positions earlier (3%)

**Result**: May catch rebounds sooner, but also increases risk of catching falling knives.

## Files Changed

### Backend Configuration
1. ✅ `config/config.py` - Changed `FALL_THRESHOLD = 5.0` to `FALL_THRESHOLD = 3.0`

### Frontend Display
2. ✅ `automatic_trading/src/components/StrategyPanel.tsx` - Updated "Drop Filter" from "≤ −5%" to "≤ −3%"
3. ✅ `automatic_trading/src/components/StockTable.tsx` - Updated description from "≤ −5% drop" to "≤ −3% drop"

### Documentation
4. ✅ `README.md` - Updated description and API documentation
5. ✅ `automatic_trading/README.md` - Updated feature description

## Testing

After deployment, verify the change:

### Test 1: Check Configuration
```bash
# Check config file
cat config/config.py | grep FALL_THRESHOLD
# Expected: FALL_THRESHOLD = 3.0
```

### Test 2: Run Backtest
1. Go to Dashboard
2. Click "Run Backtest"
3. Check results - should see more eligible stocks per day
4. Verify logs show "≥3%" threshold

### Test 3: Scan Stocks
1. Click "Scan Now"
2. Should see stocks that are 3-5% below EMA (previously would have been filtered out)
3. Check Strategy Panel shows "≤ −3%"

### Test 4: Check Frontend Display
1. Verify Strategy Panel shows: "Drop Filter: ≤ −3%"
2. Verify Stock Table header shows: "Top 5 stocks with ≤ −3% drop"

## Expected Behavior Changes

### Backtest Results

**Before (5% threshold)**:
```
Date 2026-01-03: 8 eligible, 5 selected
Date 2026-01-04: 5 eligible, 5 selected
Date 2026-01-05: 3 eligible, 3 selected
```

**After (3% threshold)**:
```
Date 2026-01-03: 15 eligible, 5 selected
Date 2026-01-04: 12 eligible, 5 selected
Date 2026-01-05: 10 eligible, 5 selected
```

More stocks will be eligible, but still only top 5 are selected.

### Stock Selection

**Before**: Only stocks with large drops (5%+) were considered
**After**: Stocks with moderate drops (3%+) are now included

This means:
- More trading opportunities
- Earlier entry points
- Potentially more false signals
- May need to adjust other parameters (stop loss, take profit) accordingly

## Risk Considerations

### Increased Activity
- More stocks will meet criteria
- More frequent trading signals
- Higher transaction costs (if real trading)

### Earlier Entries
- Catching rebounds sooner (positive)
- Risk of catching falling knives (negative)
- May need tighter stop losses

### Recommendations

1. **Monitor Performance**: Track win rate and profitability with new threshold
2. **Adjust Stop Loss**: Consider tighter stop losses for 3% entries vs 5% entries
3. **Review Regularly**: Compare results to previous 5% threshold
4. **Consider Dynamic Threshold**: Could implement variable threshold based on market conditions

## Rollback

If you want to revert to 5%:

```python
# In config/config.py
FALL_THRESHOLD = 5.0  # Change back to 5.0
```

Then update frontend displays and documentation accordingly.

## Deployment

```bash
# 1. Commit changes
git add .
git commit -m "Change threshold from 5% to 3% below EMA"
git push origin main

# 2. Wait for Render deployment (2-3 min)

# 3. Test in production
# - Run backtest
# - Verify more stocks are eligible
# - Check frontend displays "3%"
```

## Monitoring

After deployment, monitor:

1. **Number of Eligible Stocks**: Should increase
2. **Backtest Results**: More stocks per day
3. **Performance Metrics**: Track if 3% threshold performs better/worse than 5%
4. **False Signals**: Watch for stocks that continue falling after 3% drop

---

**Status**: ✅ READY FOR DEPLOYMENT
**Risk Level**: Low (configuration change only)
**Expected Impact**: More trading opportunities, earlier entries
