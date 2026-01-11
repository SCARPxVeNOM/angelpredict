# Quick Change Summary: 5% → 3% Threshold

## What Changed? 🎯

Changed the trading algorithm from selecting stocks **5% below EMA** to **3% below EMA**.

## Why This Matters 📊

- **More Opportunities**: More stocks will qualify (3% drop vs 5% drop)
- **Earlier Entries**: Catch potential rebounds sooner
- **More Signals**: Expect to see more eligible stocks in backtests and scans

## Files Changed ✅

### Backend (1 file)
- `config/config.py` - Changed `FALL_THRESHOLD = 5.0` to `3.0`

### Frontend (2 files)
- `automatic_trading/src/components/StrategyPanel.tsx` - Display shows "≤ −3%"
- `automatic_trading/src/components/StockTable.tsx` - Header shows "≤ −3% drop"

### Documentation (2 files)
- `README.md` - Updated descriptions
- `automatic_trading/README.md` - Updated features

## Test After Deployment 🧪

1. **Run Backtest**
   - Should see MORE eligible stocks per day
   - Example: 15 eligible instead of 8

2. **Check Frontend**
   - Strategy Panel: "Drop Filter: ≤ −3%"
   - Stock Table: "Top 5 stocks with ≤ −3% drop"

3. **Verify Logs**
   - Should mention "3%" threshold
   - More stocks meeting criteria

## Deploy Now 🚀

```bash
git add .
git commit -m "Change threshold from 5% to 3% below EMA"
git push origin main
```

Wait 2-3 minutes for Render deployment, then test!

---

**Status**: ✅ READY
**Impact**: More trading opportunities
**Risk**: Low (simple config change)
