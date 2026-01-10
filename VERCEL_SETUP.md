# Vercel Frontend Setup - CRITICAL

## 🔴 IMPORTANT: Set Environment Variable

Your frontend is currently pointing to `localhost:5000` which won't work in production!

### Steps to Fix:

1. **Go to Vercel Dashboard**
   - Navigate to your project
   - Go to Settings → Environment Variables

2. **Add Environment Variable**
   ```
   Name: VITE_API_BASE_URL
   Value: https://your-backend-name.onrender.com
   ```
   
   Replace `your-backend-name` with your actual Render service name.

3. **Redeploy**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment
   - OR push a new commit to trigger deployment

### How to Find Your Render Backend URL:

1. Go to Render Dashboard
2. Click on your backend service
3. Copy the URL at the top (e.g., `https://angelpredict-backend.onrender.com`)
4. Use that URL in Vercel environment variable

### Verify It's Working:

After redeployment, open browser console (F12) and check:
- Network tab should show requests going to your Render URL
- No CORS errors
- API calls should return data

### Current Configuration:

**Local Development (.env):**
```
VITE_API_BASE_URL=http://localhost:5000
```

**Production (.env.production or Vercel):**
```
VITE_API_BASE_URL=https://your-backend-name.onrender.com
```

---

## Alternative: Update .env.production

If you prefer, you can update `automatic_trading/.env.production` with your Render URL and push to GitHub:

```bash
# Edit automatic_trading/.env.production
VITE_API_BASE_URL=https://your-actual-render-url.onrender.com

# Commit and push
git add automatic_trading/.env.production
git commit -m "Update production API URL"
git push origin main
```

Vercel will automatically use `.env.production` for production builds.

---

## Testing After Setup:

1. **Open your Vercel frontend**
2. **Open browser console (F12)**
3. **Click "Scan Now" or "Run Backtest"**
4. **Check Network tab:**
   - Should see POST request to `https://your-backend.onrender.com/api/stocks/scan`
   - Should see response with data
   - No CORS errors

---

## Common Issues:

### Issue: "Failed to fetch" or "Network Error"
**Cause**: API URL not set or incorrect
**Fix**: Set `VITE_API_BASE_URL` in Vercel environment variables

### Issue: CORS Error
**Cause**: Backend CORS not configured for your frontend URL
**Fix**: Backend already configured to allow all origins (`*`), should work

### Issue: 404 Not Found
**Cause**: Wrong API URL or endpoint
**Fix**: Verify Render URL is correct and backend is running

---

## Quick Fix Command:

```bash
# Update production env file
echo "VITE_API_BASE_URL=https://YOUR-RENDER-URL.onrender.com" > automatic_trading/.env.production

# Commit and push
git add automatic_trading/.env.production
git commit -m "Fix: Update production API URL to Render backend"
git push origin main
```

Replace `YOUR-RENDER-URL` with your actual Render service URL!
