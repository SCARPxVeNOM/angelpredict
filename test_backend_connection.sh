#!/bin/bash
# Test Backend Connection Script
# This script tests if the Render backend is accessible

BACKEND_URL="https://angelpredict.onrender.com"

echo "========================================="
echo "Testing Backend Connection"
echo "========================================="
echo ""

echo "Backend URL: $BACKEND_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check Endpoint"
echo "GET $BACKEND_URL/api/health"
echo ""
curl -s -w "\nHTTP Status: %{http_code}\n" "$BACKEND_URL/api/health"
echo ""
echo "Expected: {\"status\":\"healthy\",\"service\":\"Trading Bot API\"}"
echo ""
echo "========================================="
echo ""

# Test 2: Status Check
echo "Test 2: Status Endpoint"
echo "GET $BACKEND_URL/api/status"
echo ""
curl -s -w "\nHTTP Status: %{http_code}\n" "$BACKEND_URL/api/status"
echo ""
echo "========================================="
echo ""

# Test 3: Stocks Endpoint (should return empty)
echo "Test 3: Stocks Endpoint (should return empty)"
echo "GET $BACKEND_URL/api/stocks"
echo ""
curl -s -w "\nHTTP Status: %{http_code}\n" "$BACKEND_URL/api/stocks"
echo ""
echo "Expected: {\"success\":true,\"stocks\":[],\"message\":\"Use POST /api/stocks/scan to fetch market data\"}"
echo ""
echo "========================================="
echo ""

# Test 4: Backtest Endpoint (POST)
echo "Test 4: Backtest Endpoint (will trigger actual backtest)"
echo "POST $BACKEND_URL/api/backtest"
echo ""
read -p "Do you want to trigger a backtest? This will make API calls to AngelOne. (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Triggering backtest..."
    curl -s -X POST "$BACKEND_URL/api/backtest" \
      -H "Content-Type: application/json" \
      -d '{"days": 7}' \
      -w "\nHTTP Status: %{http_code}\n"
    echo ""
    echo "Check Render logs to see backtest progress"
else
    echo "Skipped backtest test"
fi

echo ""
echo "========================================="
echo "Tests Complete"
echo "========================================="
echo ""
echo "If all tests show HTTP Status 200, your backend is working!"
echo "If you see connection errors, check:"
echo "  1. Render service is running (not sleeping)"
echo "  2. URL is correct: $BACKEND_URL"
echo "  3. No firewall blocking requests"
echo ""
