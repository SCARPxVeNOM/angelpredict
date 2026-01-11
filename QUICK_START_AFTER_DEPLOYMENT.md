# Quick Start After Deployment

## 🎯 You're Here Because...

Your backend is deployed on Render, frontend is deployed on Vercel, but the "Run Backtest" button isn't working.

---

## ✅ What's Already Done

- ✅ Backend deployed on Render: `https://angelpredict.onrender.com`
- ✅ Frontend deployed on Vercel
- ✅ Rate limiting implemented (3 req/sec)
- ✅ API caching with 60s TTL
- ✅ Exponential backoff retry logic
- ✅ All automatic API calls disabled
- ✅ Backtest endpoint working perfectly
- ✅ Lazy authentication (no API calls on startup)

---

## ❌ What's NOT Working

Frontend can't reach backend because environment variable isn't set in Vercel.

---

## 🔧 Fix in 3 Steps (5 minutes)

### Step 1: Set Environment Variable

1. Go to https://vercel.com/dashboard
2. Click your project → **Settings** → **Environment Variables**
3. Add new variable:
   - Name: `VITE_API_BASE_URL`
   - Value: `https://angelpredict.onrender.com`
   - Environments: ✅ All three
4. Save

### Step 2: Redeploy

**Deployments** tab → Latest deployment → ••• → **Redeploy**

### Step 3: Test

1. Open your Vercel site
2. Press F12 (console)
3. Click "Run Backtest"
4. Check Render logs - you should see activity!

---

## 📚 Detailed Guides

Choose based on what you need:

### 🔴 **BACKTEST_NOT_WORKING_FIX.md** ← START HERE
Complete guide to fix the backtest button issue.

### 🔵 **FRONTEND_BACKEND_CONNECTION_FIX.md**
Detailed troubleshooting for frontend-backend connection.

### 🟢 **BACKTEST_WORKING.md**
How the backtest system works internally.

### 🟡 **VERCEL_SETUP.md**
Original Vercel deployment instructions.

### 🟣 **NO_AUTO_API_CALLS.md**
Documentation of the no-auto-call policy.

---

## 🧪 Test Your Backend

### Option 1: Use Test HTML Page

Open `test_backend.html` in your browser. It will test all endpoints visually.

### Option 2: Use Test Script

**Windows:**
```cmd
test_backend_connection.bat
```

**Linux/Mac:**
```bash
chmod +x test_backend_connection.sh
./test_backend_connection.sh
```

### Option 3: Manual cURL Test

```bash
curl https://angelpredict.onrender.com/api/health
```

Expected: `{"status":"healthy","service":"Trading Bot API"}`

---

## 🎬 What Happens After Fix

### Scan Now Button:
- Fetches current market data
- Shows eligible stocks in table
- Takes 5-10 seconds

### Run Backtest Button:
- Fetches 7 days of historical data
- Simulates trading algorithm
- Shows results in Orders panel
- Takes 2-3 minutes
- You'll see progress in Render logs:
  ```
  Starting backtest for 7 days...
  Simulating date: 2025-01-04
  Date 2025-01-04: 15 eligible, 5 selected, ₹60000 allocated
  Simulating date: 2025-01-05
  ...
  Backtest completed: 35 orders
  ```

---

## 🐛 Common Issues

### "Still seeing localhost in Network tab"
→ Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### "Backend takes 30-60 seconds to respond"
→ Normal for Render free tier. Backend was sleeping and is waking up.

### "CORS error"
→ Backend already allows all origins. Check if backend is running.

### "404 Not Found"
→ Check backend URL is correct and service is running on Render.

---

## 📊 System Architecture

```
Frontend (Vercel)
    ↓ HTTPS
Backend (Render) → AngelOne API
    ↓
Rate Limiter (3 req/sec)
    ↓
API Cache (60s TTL)
    ↓
Retry Logic (exponential backoff)
```

---

## 🔐 Security Features

- ✅ No API keys in frontend
- ✅ All API calls from backend only
- ✅ Rate limiting prevents API abuse
- ✅ Caching reduces API calls
- ✅ Retry logic handles failures
- ✅ CORS configured for security

---

## 📝 Key Files

| File | Purpose |
|------|---------|
| `BACKTEST_NOT_WORKING_FIX.md` | Fix backtest button |
| `FRONTEND_BACKEND_CONNECTION_FIX.md` | Connection troubleshooting |
| `test_backend.html` | Visual backend tester |
| `test_backend_connection.bat` | Windows test script |
| `test_backend_connection.sh` | Linux/Mac test script |
| `BACKTEST_WORKING.md` | How backtest works |
| `NO_AUTO_API_CALLS.md` | No-auto-call policy |

---

## 🚀 Next Steps

1. **Fix the connection** (5 min)
   - Set env var in Vercel
   - Redeploy
   - Test

2. **Verify it works** (2 min)
   - Open test_backend.html
   - Run all tests
   - Check Render logs

3. **Use the system** (ongoing)
   - Click "Scan Now" to see eligible stocks
   - Click "Run Backtest" to simulate past 7 days
   - View results in Orders panel

---

## 💡 Pro Tips

1. **First request after inactivity**: Render free tier spins down. First request takes 30-60s to wake up. Be patient!

2. **Check Render logs**: Always check Render logs when testing. They show exactly what's happening.

3. **Browser console**: Keep F12 console open when testing. It shows all API calls and errors.

4. **Hard refresh**: After any deployment, do a hard refresh (Ctrl+Shift+R) to clear cache.

---

## 📞 Need Help?

1. Check `BACKTEST_NOT_WORKING_FIX.md` for detailed troubleshooting
2. Run `test_backend.html` to verify backend is working
3. Check Render logs for backend errors
4. Check browser console for frontend errors

---

## ✨ Summary

**Problem**: Frontend can't reach backend  
**Cause**: Environment variable not set in Vercel  
**Fix**: Set `VITE_API_BASE_URL` in Vercel dashboard  
**Time**: 5 minutes  
**Result**: Everything works! 🎉

**Start with**: `BACKTEST_NOT_WORKING_FIX.md`
