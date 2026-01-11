# 🚀 START HERE - Fix Your Backtest Button

## The Problem

You click "Run Backtest" but nothing happens. No Render logs, no response.

## The Solution (5 Minutes)

Your backend is working perfectly. The frontend just can't reach it because of a missing environment variable.

---

## Fix It Now

### 1. Open Vercel Dashboard
Go to: https://vercel.com/dashboard

### 2. Find Your Project
Click on your automatic_trading project

### 3. Add Environment Variable
- Click **Settings** (left sidebar)
- Click **Environment Variables**
- Click **Add New**
- Enter:
  ```
  Name:  VITE_API_BASE_URL
  Value: https://angelpredict.onrender.com
  ```
- Check all three boxes: Production, Preview, Development
- Click **Save**

### 4. Redeploy
- Click **Deployments** tab
- Find the latest deployment
- Click the three dots (•••)
- Click **Redeploy**
- Wait for deployment to complete (~2 minutes)

### 5. Test It
- Open your Vercel site
- Press **F12** to open browser console
- Click **"Run Backtest"** button
- Open Render dashboard in another tab
- Go to your service → **Logs** tab
- You should see:
  ```
  API /api/backtest: Request received
  Starting backtest for 7 days...
  Simulating date: 2025-01-04
  ...
  ```

---

## That's It!

If you see logs in Render, it's working! The backtest takes 2-3 minutes to complete.

---

## Still Not Working?

### Quick Test: Is Backend Running?

Open this in your browser:
```
https://angelpredict.onrender.com/api/health
```

Should show:
```json
{"status":"healthy","service":"Trading Bot API"}
```

If you see this, backend is fine. The issue is frontend connection.

### Check Environment Variable

After redeploying, open your Vercel site and press F12. In the console, type:
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```

Should show: `https://angelpredict.onrender.com`  
NOT: `http://localhost:5000`

If it still shows localhost:
1. Verify env var is saved in Vercel dashboard
2. Redeploy again
3. Hard refresh browser (Ctrl+Shift+R)

---

## Need More Help?

### Visual Testing Tool
Open `test_backend.html` in your browser. It will test all endpoints with a nice UI.

### Detailed Guides
- **BACKTEST_NOT_WORKING_FIX.md** - Complete troubleshooting guide
- **FRONTEND_BACKEND_CONNECTION_FIX.md** - Connection issues
- **QUICK_START_AFTER_DEPLOYMENT.md** - Overview of everything

### Test Scripts
**Windows:**
```cmd
test_backend_connection.bat
```

**Linux/Mac:**
```bash
./test_backend_connection.sh
```

---

## What You'll See After Fix

### Scan Now Button:
- Takes 5-10 seconds
- Shows eligible stocks in table
- Render logs show: "API /api/stocks/scan: Manual scan triggered"

### Run Backtest Button:
- Takes 2-3 minutes
- Shows progress in Render logs
- Displays results in Orders panel
- Shows execution dates for each order

---

## Why This Happened

Vercel doesn't automatically use `.env.production` file. You must set environment variables in the Vercel dashboard.

Your `.env.production` has the correct URL, but Vercel ignores it unless explicitly set in the dashboard.

---

## Summary

1. ✅ Go to Vercel dashboard
2. ✅ Add `VITE_API_BASE_URL` environment variable
3. ✅ Set value to `https://angelpredict.onrender.com`
4. ✅ Redeploy
5. ✅ Test - should see Render logs!

**That's all you need to do!** 🎉

---

## Pro Tip

Keep Render logs open in one tab and your Vercel site in another. When you click buttons, you'll see real-time logs showing what's happening.

---

**Ready? Go to Vercel dashboard and add that environment variable!**
