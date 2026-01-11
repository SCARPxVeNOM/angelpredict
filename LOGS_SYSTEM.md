# Logs System Documentation

## Overview

The trading bot now has a comprehensive logging system that captures all backend activity and makes it available through the frontend.

## How It Works

### Backend Logging

1. **Log File**: All backend logs are written to `logs/trading_bot.log`
   - Maximum file size: 10MB
   - Backup count: 3 files
   - Automatic rotation when size limit is reached

2. **Log Format**: 
   ```
   [YYYY-MM-DD HH:MM:SS] LEVEL - message
   ```

3. **Log Levels**:
   - `INFO`: General information (system startup, API calls, etc.)
   - `WARNING`: Non-critical issues
   - `ERROR`: Critical errors
   - `SUCCESS`: Successful operations (backtest completion, orders, etc.)

### Frontend Logs Panel

The Logs Panel (`/logs` page) displays system logs with the following features:

1. **Auto-Fetch on Mount**: Logs are automatically fetched when you navigate to the Logs page
2. **Manual Refresh**: Click the "Refresh Logs" button to fetch the latest logs
3. **Real-Time Updates**: After clicking "Scan Now" or "Run Backtest", navigate to Logs and click "Refresh Logs" to see the latest activity
4. **Color-Coded Severity**:
   - 🟢 Green: Success messages
   - 🟡 Yellow: Warnings
   - 🔴 Red: Errors
   - 🔵 Blue: Info messages

### API Endpoint

**GET /api/logs**

Returns the latest system logs in JSON format:

```json
{
  "success": true,
  "logs": [
    {
      "id": "log_1",
      "timestamp": "15:30:45",
      "message": "Backtest completed: 15 orders, 7 days simulated",
      "severity": "success"
    },
    ...
  ]
}
```

## Viewing Logs

### Method 1: Frontend (Recommended)

1. Navigate to the Logs page in the frontend
2. Click "Refresh Logs" to see the latest activity
3. Logs are displayed in reverse chronological order (newest first)

### Method 2: Backend Log File

View the raw log file directly:

```bash
# View last 50 lines
tail -n 50 logs/trading_bot.log

# Follow logs in real-time
tail -f logs/trading_bot.log

# Search for specific text
grep "backtest" logs/trading_bot.log
```

### Method 3: Render Dashboard (Production)

1. Go to your Render dashboard
2. Click on your backend service
3. Click "Logs" tab
4. View real-time logs from the deployed backend

## What Gets Logged

### Backtest Execution

When you click "Run Backtest":

```
[2026-01-11 15:30:00] INFO - Starting backtest for 7 days...
[2026-01-11 15:30:01] INFO - Backtesting dates: ['2026-01-03', '2026-01-04', ...]
[2026-01-11 15:30:05] INFO - Date 2026-01-03: 12 eligible, 5 selected, ₹75000.00 allocated
[2026-01-11 15:30:10] INFO - Date 2026-01-04: 8 eligible, 5 selected, ₹75000.00 allocated
...
[2026-01-11 15:30:45] INFO - Backtest completed: 35 orders, ₹525000.00 allocated
[2026-01-11 15:30:45] INFO - Backtest results saved to data/backtest_results_20260111_153045.json
[2026-01-11 15:30:45] INFO - Saved 35 backtest orders to data/backtest_orders.json
```

### Stock Scanning

When you click "Scan Now":

```
[2026-01-11 15:35:00] INFO - API /api/stocks/scan: Manual scan triggered
[2026-01-11 15:35:05] INFO - API /api/stocks/scan: Found 12 top stocks
[2026-01-11 15:35:05] INFO - API /api/stocks/scan: Eligible stocks: ['RELIANCE', 'TCS', 'INFY', ...]
[2026-01-11 15:35:05] INFO - API /api/stocks/scan: Returning 5 stocks to frontend
```

### API Calls

All API requests are logged:

```
[2026-01-11 15:40:00] INFO - API /api/logs: Returning 50 log entries
[2026-01-11 15:40:05] INFO - API /api/orders: Returning 35 total orders (35 backtest, 0 simulated, 0 today)
[2026-01-11 15:40:10] INFO - API /api/capital: Capital overview requested
```

### Errors

Any errors are logged with full details:

```
[2026-01-11 15:45:00] ERROR - Error running backtest: Authentication required
[2026-01-11 15:45:00] ERROR - Historical API authentication required. Please check HISTORICAL_API_KEY
```

## Troubleshooting

### Logs Not Updating

**Problem**: Logs panel shows old data after running backtest

**Solution**:
1. Navigate to the Logs page
2. Click the "Refresh Logs" button
3. Logs should update with the latest activity

### No Logs Showing

**Problem**: Logs panel is empty

**Solution**:
1. Check if backend is running (visit `/api/health`)
2. Check Render logs to see if backend is logging
3. Verify `logs/trading_bot.log` file exists
4. Try running a backtest or scan to generate new logs

### Logs Not Persisting

**Problem**: Logs disappear after backend restart

**Solution**:
- Logs are stored in `logs/trading_bot.log` which persists across restarts
- On Render, logs are ephemeral (cleared on restart)
- Use the log file for persistent logs, or download logs before restart

## Best Practices

1. **Check Logs After Actions**: After running backtest or scan, refresh the logs to see what happened
2. **Monitor Errors**: Red error messages indicate issues that need attention
3. **Use Render Logs for Production**: For deployed backend, use Render's log viewer for real-time monitoring
4. **Download Logs**: Download log files before major changes for debugging

## Log Retention

- **Local Development**: Logs are kept in `logs/trading_bot.log` with 3 backup files (30MB total)
- **Production (Render)**: Logs are ephemeral and cleared on restart
- **Frontend Display**: Shows last 50 log entries

## Future Enhancements

Potential improvements:

1. **Auto-Refresh**: Add option to auto-refresh logs every N seconds
2. **Log Filtering**: Filter by severity level (errors only, warnings, etc.)
3. **Log Search**: Search logs by keyword
4. **Export Logs**: Download logs as a file from frontend
5. **Real-Time Streaming**: WebSocket-based real-time log streaming
