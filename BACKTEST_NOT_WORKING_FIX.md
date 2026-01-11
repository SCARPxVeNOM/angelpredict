# Backtest Button Not Working - Complete Fix Guide

## Problem Summary

You're clicking "Run Backtest" button but seeing no Render logs and no response.

**Root Cause**: Frontend is calling `localhost:5000` instead of your Render backend URL.

---

## Quick Fix (5 minutes)

### Step 1: Set Environment Variable in Vercel

1. Go to https://vercel.com/dashboard
2. Click your project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: `https://angelpredict.onrender.com`
   - **Environments**: Check all three (Production, Preview, Development)
6. Click **Save**

### Step 2: Redeploy

Go to **Deployments** tab → Click latest deployment → Click ••• → **Redeploy**

### Step 3: Verify

1. Open your Vercel frontend
2. Press F12 (open browser console)
3. Type: `console.log(import.meta.env.VITE_API_BASE_URL)`
4. Should show: `https://angelpredict.onrender.com` (NOT localhost)

### Step 4: Test

1. Click "Run Backtest" button
2. Open Render dashboard → Your service → Logs tab
3. You should see:
   ```
   API /api/backtest: Request received
   Starting backtest for 7 days...
   Simulating date: 2025-01-XX
   ...
   Backtest completed successfully
   ```

---

## Why This Happens

Vercel **does NOT automatically use** `.env.production` file. You must set environment variables in the Vercel dashboard.

Your `.env.production` file has the correct URL, but Vercel ignores it unless you explicitly set it in the dashboard.

---

## Test Backend Directly (Optional)

To verify your backend is working, run this command:

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://angelpredict.onrender.com/api/health" | Select-Object -Expand Content
```

**Windows (CMD):**
```cmd
curl https://angelpredict.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "Trading Bot API"
}
```

If you get this response, your backend is working fine!

---

## Test Scripts Included

I've created test scripts for you:

### Windows:
```cmd
test_backend_connection.bat
```

### Linux/Mac:
```bash
chmod +x test_backend_connection.sh
./test_backend_connection.sh
```

These scripts will test all endpoints and confirm your backend is accessible.

---

## What Happens After Fix

### Scan Now Button:
1. Frontend → `POST https://angelpredict.onrender.com/api/stocks/scan`
2. Backend fetches data from AngelOne API
3. Render logs show: "API /api/stocks/scan: Manual scan triggered"
4. Frontend displays stocks

### Run Backtest Button:
1. Frontend → `POST https://angelpredict.onrender.com/api/backtest`
2. Backend fetches historical data (2-3 minutes)
3. Render logs show progress:
   ```
   Starting backtest for 7 days...
   Simulating date: 2025-01-04
   Simulating date: 2025-01-05
   ...
   Backtest completed: 35 orders, ₹300000.00 allocated
   ```
4. Frontend displays results in Orders panel

---

## Troubleshooting

### Issue: Still no Render logs

**Check 1**: Is env var set in Vercel?
- Go to Vercel → Settings → Environment Variables
- Verify `VITE_API_BASE_URL` exists

**Check 2**: Did you redeploy?
- After setting env var, you MUST redeploy
- Go to Deployments → Redeploy

**Check 3**: Hard refresh browser
- Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- This clears cached JavaScript

**Check 4**: Check Network tab
- Open browser console (F12)
- Go to Network tab
- Click "Run Backtest"
- Look for request - should go to `angelpredict.onrender.com`, NOT `localhost`

### Issue: Backend sleeping (Render free tier)

**Symptom**: First request takes 30-60 seconds

**Fix**: This is normal for Render free tier. Backend spins down after inactivity and takes time to wake up.

**Solution**: Wait for first request to complete, then subsequent requests will be fast.

### Issue: CORS error

**Symptom**: Browser console shows CORS error

**Fix**: Backend is already configured to allow all origins. If you still see this:
1. Check Render logs for errors
2. Verify backend is running: `curl https://angelpredict.onrender.com/api/health`

---

## Expected Timeline

After setting env var and redeploying:

- **Scan Now**: 5-10 seconds (fetches current market data)
- **Run Backtest**: 2-3 minutes (fetches 7 days of historical data for 50 stocks)

During backtest, you'll see progress in Render logs:
```
Simulating date: 2025-01-04
Date 2025-01-04: 15 eligible, 5 selected, ₹60000.00 allocated
Simulating date: 2025-01-05
Date 2025-01-05: 18 eligible, 5 selected, ₹60000.00 allocated
...
```

---

## Files Reference

- `FRONTEND_BACKEND_CONNECTION_FIX.md` - Detailed connection fix guide
- `BACKTEST_WORKING.md` - How backtest works internally
- `VERCEL_SETUP.md` - Original Vercel setup instructions
- `NO_AUTO_API_CALLS.md` - Documentation of no-auto-call policy
- `test_backend_connection.bat` - Windows test script
- `test_backend_connection.sh` - Linux/Mac test script

---

## Summary

1. ✅ Set `VITE_API_BASE_URL` in Vercel dashboard
2. ✅ Redeploy on Vercel
3. ✅ Hard refresh browser
4. ✅ Click "Run Backtest"
5. ✅ Check Render logs - you should see activity!

**The backtest endpoint is working perfectly. The only issue is the frontend isn't reaching it because of the environment variable.**

Once you set the env var in Vercel, everything will work!
