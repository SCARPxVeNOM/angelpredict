@echo off
REM Test Backend Connection Script (Windows)
REM This script tests if the Render backend is accessible

set BACKEND_URL=https://angelpredict.onrender.com

echo =========================================
echo Testing Backend Connection
echo =========================================
echo.

echo Backend URL: %BACKEND_URL%
echo.

REM Test 1: Health Check
echo Test 1: Health Check Endpoint
echo GET %BACKEND_URL%/api/health
echo.
curl -s "%BACKEND_URL%/api/health"
echo.
echo Expected: {"status":"healthy","service":"Trading Bot API"}
echo.
echo =========================================
echo.

REM Test 2: Status Check
echo Test 2: Status Endpoint
echo GET %BACKEND_URL%/api/status
echo.
curl -s "%BACKEND_URL%/api/status"
echo.
echo =========================================
echo.

REM Test 3: Stocks Endpoint
echo Test 3: Stocks Endpoint (should return empty)
echo GET %BACKEND_URL%/api/stocks
echo.
curl -s "%BACKEND_URL%/api/stocks"
echo.
echo Expected: {"success":true,"stocks":[],"message":"Use POST /api/stocks/scan to fetch market data"}
echo.
echo =========================================
echo.

REM Test 4: Backtest Endpoint
echo Test 4: Backtest Endpoint (POST)
echo.
set /p CONFIRM="Do you want to trigger a backtest? This will make API calls to AngelOne. (y/N): "
if /i "%CONFIRM%"=="y" (
    echo Triggering backtest...
    curl -s -X POST "%BACKEND_URL%/api/backtest" -H "Content-Type: application/json" -d "{\"days\": 7}"
    echo.
    echo Check Render logs to see backtest progress
) else (
    echo Skipped backtest test
)

echo.
echo =========================================
echo Tests Complete
echo =========================================
echo.
echo If all tests returned JSON data, your backend is working!
echo If you see connection errors, check:
echo   1. Render service is running (not sleeping)
echo   2. URL is correct: %BACKEND_URL%
echo   3. No firewall blocking requests
echo.
pause
