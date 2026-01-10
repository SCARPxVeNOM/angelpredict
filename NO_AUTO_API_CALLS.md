# No Automatic API Calls Configuration

## Summary
This document confirms that the entire system (both frontend and backend) is configured to make **ZERO automatic API calls**. All API calls are manual-only, triggered by user actions.

---

## Backend (Python/Flask) - Deployed on Render

### ✅ Main Entry Point (`main.py`)
- **Scheduler**: Initialized but **NOT started** (line 66 commented out)
- **Flask API**: Only serves API endpoints, makes no automatic calls
- **No background tasks**: No automatic execution on startup

```python
# Line 66 in main.py - DISABLED
# self.scheduler.start()  # DISABLED - no automatic execution
```

### ✅ Scheduler (`src/scheduler.py`)
- **Status**: Initialized but never started
- **Execution**: Only via manual trigger through `/api/run-now` endpoint
- **No cron jobs**: Daily schedule exists but is never activated

### ✅ All Other Python Modules
- **AngelOneClient**: Only makes API calls when explicitly requested
- **StockAnalyzer**: Only analyzes when called by API endpoint
- **OrderManager**: Only places orders when triggered manually
- **Backtester**: Only runs when `/api/backtest` endpoint is called
- **EMACalculator**: Only calculates when requested
- **AllocationTracker**: Only tracks, no API calls
- **Nifty50Fetcher**: Only reads local JSON file, no API calls

### ✅ API Endpoints (Manual Triggers Only)
1. **POST /api/backtest** - Run backtest simulation (fetches past 7 days data)
2. **POST /api/run-now** - Manually trigger trading algorithm
3. **GET /api/stocks** - Fetch current eligible stocks (manual "Scan Now" button)
4. All other GET endpoints return cached/stored data only

---

## Frontend (React/TypeScript) - Deployed on Vercel

### ✅ All Components - No Auto-Fetch
- **StockTable.tsx**: No auto-fetch, only manual "Scan Now" button
- **OrdersPanel.tsx**: No auto-fetch, displays static data
- **LogsPanel.tsx**: No auto-fetch, displays static data
- **CapitalOverview.tsx**: No auto-fetch, displays static data
- **TopNavBar.tsx**: No auto-fetch, displays static data
- **BacktestPanel.tsx**: Only fetches when "Run Backtest" button clicked

### ✅ No Polling or Intervals
- **No useEffect with intervals**: All removed
- **No auto-refresh**: All removed
- **No background fetching**: All removed

### ✅ Manual Triggers Only
1. **"Run Backtest" button** → Calls `/api/backtest` → Fetches past 7 days data
2. **"Scan Now" button** → Calls `/api/stocks` → Fetches current market data
3. **"Load Latest Results" button** → Calls `/api/backtest/results` → Loads cached results

---

## Rate Limiting & Caching (Active)

Even though automatic calls are disabled, the system has robust protection:

### ✅ Rate Limiting
- **Token Bucket Algorithm**: 3 requests/second
- **Capacity**: 10 tokens
- **Timeout**: 10 seconds max wait

### ✅ API Caching
- **TTL**: 60 seconds
- **Max Size**: 1000 entries
- **LRU Eviction**: Automatic cleanup

### ✅ Retry Logic
- **Max Retries**: 3 attempts
- **Exponential Backoff**: 1s → 2s → 4s → 8s
- **Max Delay**: 10 seconds

---

## Verification Checklist

### Backend (Render)
- [x] Scheduler NOT started in main.py
- [x] No automatic cron jobs running
- [x] No background threads making API calls
- [x] All API calls require explicit endpoint calls
- [x] Backtest only runs when POST /api/backtest is called

### Frontend (Vercel)
- [x] No useEffect with auto-fetch on mount
- [x] No setInterval or setTimeout for polling
- [x] No automatic API calls in any component
- [x] All data fetching requires button clicks
- [x] TypeScript build passes without errors

---

## How to Trigger API Calls (Manual Only)

### 1. Run Backtest (Fetches Past 7 Days)
```bash
# Frontend: Click "Run Backtest" button
# Backend: POST /api/backtest
curl -X POST https://your-backend.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

### 2. Scan Current Market
```bash
# Frontend: Click "Scan Now" button
# Backend: GET /api/stocks
curl https://your-backend.onrender.com/api/stocks
```

### 3. Manual Algorithm Execution
```bash
# Backend only: POST /api/run-now
curl -X POST https://your-backend.onrender.com/api/run-now
```

---

## Deployment Status

### ✅ Backend (Render)
- **URL**: https://your-backend.onrender.com
- **Status**: Running in API-only mode
- **Automatic Calls**: ZERO
- **Manual Endpoints**: Active

### ✅ Frontend (Vercel)
- **URL**: https://your-frontend.vercel.app
- **Status**: Deployed successfully
- **Automatic Calls**: ZERO
- **Manual Triggers**: Active

---

## Monitoring

To verify no automatic API calls are being made:

### Backend Logs (Render)
```bash
# Check logs for any unexpected API calls
# Should only see:
# - "Scheduler initialized but NOT started"
# - "Flask API server started"
# - No "Executing trading algorithm" unless manually triggered
```

### Frontend Console (Browser)
```javascript
// Open browser console
// Should see NO automatic fetch calls
// Only manual calls when buttons are clicked
```

---

## Last Updated
**Date**: January 18, 2026  
**Status**: ✅ All automatic API calls disabled  
**Verification**: Complete

---

## Contact
If you see any automatic API calls, check:
1. Backend logs on Render
2. Frontend console in browser
3. This configuration document

All systems are configured for **manual-only execution**.
