# Frontend-Backend Connection Fix

## Current Status

✅ **Backend deployed on Render**: `https://angelpredict.onrender.com`  
✅ **Frontend deployed on Vercel**: (your Vercel URL)  
✅ **Backtest endpoint working**: `POST /api/backtest`  
❌ **Problem**: Frontend not connecting to backend (no Render logs)

---

## Root Cause

Your frontend is still calling `localhost:5000` instead of the Render backend URL.

**Why?** Vercel doesn't automatically use `.env.production` file - you need to set environment variables in the Vercel dashboard.

---

## SOLUTION: Set Environment Variable in Vercel

### Step 1: Go to Vercel Dashboard

1. Open https://vercel.com/dashboard
2. Click on your project (automatic_trading)
3. Go to **Settings** tab
4. Click **Environment Variables** in the left sidebar

### Step 2: Add Environment Variable

Click "Add New" and enter:

```
Name:  VITE_API_BASE_URL
Value: https://angelpredict.onrender.com
```

**Important**: 
- No trailing slash at the end
- Must start with `https://`
- Use the exact Render URL

### Step 3: Select Environments

Check all three boxes:
- ✅ Production
- ✅ Preview
- ✅ Development

Click **Save**

### Step 4: Redeploy

**Option A - Redeploy existing:**
1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the three dots (•••)
4. Click **Redeploy**
5. Confirm

**Option B - Push new commit:**
```bash
# Make a small change to trigger deployment
git commit --allow-empty -m "Trigger redeploy with env var"
git push origin main
```

---

## Verify It's Working

### Test 1: Check Environment Variable

After redeployment, open your Vercel frontend and check browser console:

```javascript
// Open browser console (F12) and type:
console.log(import.meta.env.VITE_API_BASE_URL)
// Should show: https://angelpredict.onrender.com
// NOT: http://localhost:5000
```

### Test 2: Check Network Requests

1. Open browser console (F12)
2. Go to **Network** tab
3. Click "Run Backtest" button
4. Look for request to `/api/backtest`
5. Check the URL - should be `https://angelpredict.onrender.com/api/backtest`

### Test 3: Check Render Logs

1. Open Render dashboard
2. Go to your backend service
3. Click **Logs** tab
4. Click "Run Backtest" in your frontend
5. You should see logs like:
   ```
   API /api/backtest: Request received
   Starting backtest for 7 days...
   ```

---

## Expected Behavior After Fix

### When you click "Scan Now":
1. Frontend sends: `POST https://angelpredict.onrender.com/api/stocks/scan`
2. Render logs show: `API /api/stocks/scan: Manual scan triggered`
3. Backend fetches data from AngelOne API
4. Frontend displays stocks in table

### When you click "Run Backtest":
1. Frontend sends: `POST https://angelpredict.onrender.com/api/backtest`
2. Render logs show: `Starting backtest for 7 days...`
3. Backend fetches historical data (takes 2-3 minutes)
4. Render logs show: `Backtest completed successfully: X orders`
5. Frontend displays results

---

## Troubleshooting

### Issue: Still seeing localhost in Network tab

**Cause**: Environment variable not set or deployment didn't pick it up

**Fix**:
1. Verify env var is set in Vercel dashboard
2. Redeploy again
3. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
4. Clear browser cache

### Issue: CORS Error

**Cause**: Backend CORS not allowing your frontend domain

**Fix**: Backend is already configured to allow all origins (`*`), so this shouldn't happen. If it does:
1. Check Render logs for CORS errors
2. Verify backend is running (visit `https://angelpredict.onrender.com/api/health`)

### Issue: 404 Not Found

**Cause**: Wrong API URL or backend not running

**Fix**:
1. Test backend directly: `curl https://angelpredict.onrender.com/api/health`
2. Should return: `{"status":"healthy","service":"Trading Bot API"}`
3. If not, check Render dashboard - service might be sleeping

### Issue: Request timeout

**Cause**: Render free tier spins down after inactivity

**Fix**:
1. First request after inactivity takes 30-60 seconds to wake up
2. Wait for backend to wake up
3. Subsequent requests will be fast

---

## Quick Test Commands

### Test Backend Health (from terminal):
```bash
curl https://angelpredict.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Trading Bot API"
}
```

### Test Backtest Endpoint (from terminal):
```bash
curl -X POST https://angelpredict.onrender.com/api/backtest \
  -H "Content-Type: application/json" \
  -d '{"days": 7}'
```

This will trigger a backtest and you should see logs in Render dashboard.

---

## Summary

1. ✅ Set `VITE_API_BASE_URL=https://angelpredict.onrender.com` in Vercel dashboard
2. ✅ Redeploy on Vercel
3. ✅ Test in browser console
4. ✅ Check Network tab shows Render URL
5. ✅ Verify Render logs show incoming requests

After these steps, your frontend will connect to the backend and you'll see logs in Render when clicking buttons!
