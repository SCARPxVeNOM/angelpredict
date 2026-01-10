# Render Backend Deployment Guide

This guide covers deploying **ONLY the backend API** to Render. The frontend is deployed separately on Vercel.

## Architecture

- **Backend (Render)**: Flask API serving `/api/*` endpoints
- **Frontend (Vercel)**: React app consuming the API

## Prerequisites

1. GitHub repository connected to Render
2. Render account
3. AngelOne API credentials
4. Gemini API key (optional, for AI features)

## Deployment Steps

### 1. Push Updated Code to GitHub

The following files have been updated for backend-only deployment:
- `render.yaml` - Render configuration
- `api/flask_api.py` - Removed frontend serving
- `.renderignore` - Excludes frontend files

```bash
git add .
git commit -m "Configure Render for backend-only deployment"
git push origin main
```

### 2. Configure Render Service

#### Option A: Using render.yaml (Recommended)

Render will automatically detect `render.yaml` and configure the service.

#### Option B: Manual Configuration

If not using `render.yaml`:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `angelpredict-backend`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### 3. Set Environment Variables

In Render Dashboard → Environment → Add Environment Variables:

#### Required Variables

```bash
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=10000
FLASK_DEBUG=false

# Trading Mode
PAPER_TRADING=true
SIMULATE_ORDERS=true
USE_MPIN=true

# AngelOne Trading API
TRADING_API_KEY=your_trading_api_key
TRADING_SECRET_KEY=your_trading_secret_key

# AngelOne Historical API
HISTORICAL_API_KEY=your_historical_api_key
HISTORICAL_SECRET_KEY=your_historical_secret_key

# AngelOne Market API
MARKET_API_KEY=your_market_api_key
MARKET_SECRET_KEY=your_market_secret_key

# AngelOne Account Credentials
ANGELONE_USERNAME=your_username
ANGELONE_PASSWORD=your_password
ANGELONE_MPIN=your_mpin
ANGELONE_TOTP_TOKEN=your_totp_token

# Gemini AI (Optional)
GEMINI_API_KEY=your_gemini_api_key

# CORS Configuration (IMPORTANT!)
FRONTEND_URL=https://your-vercel-app.vercel.app
```

**⚠️ IMPORTANT**: Replace `https://your-vercel-app.vercel.app` with your actual Vercel frontend URL.

### 4. Deploy

Click "Create Web Service" or "Manual Deploy" → "Deploy latest commit"

Render will:
1. Install Python dependencies
2. Start the Flask API server
3. Run health checks on `/api/health`

### 5. Verify Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-render-app.onrender.com/api/health

# Get stocks
curl https://your-render-app.onrender.com/api/stocks

# Get capital info
curl https://your-render-app.onrender.com/api/capital
```

You should see JSON responses.

### 6. Update Vercel Frontend

In your Vercel project settings, update the environment variable:

```
VITE_API_BASE_URL=https://your-render-app.onrender.com
```

Then redeploy your Vercel frontend.

## API Endpoints

Your Render backend serves these endpoints:

- `GET /api/health` - Health check
- `GET /api/stocks` - Get eligible stocks
- `GET /api/capital` - Get capital overview
- `GET /api/orders` - Get order history
- `GET /api/logs` - Get system logs
- `GET /api/status` - Get system status
- `POST /api/run-now` - Manually trigger algorithm
- `POST /api/backtest` - Run backtest simulation
- `POST /api/ai/chat` - AI chat endpoint

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:

1. Verify `FRONTEND_URL` environment variable in Render matches your Vercel URL exactly
2. Redeploy Render service after updating
3. Clear browser cache

### Authentication Errors

If you see authentication failures in logs:

1. Verify all AngelOne credentials are correct
2. Check TOTP token is valid
3. Ensure MPIN is correct (not password)

### No Stocks Found

If API returns empty stocks array:

1. Check Render logs for errors
2. Verify AngelOne API keys have correct permissions
3. Ensure market is open (or use backtest feature)

### Port Issues

Render uses port `10000` by default. If you see port conflicts:

1. Check `FLASK_PORT` environment variable
2. Ensure it matches Render's expected port

## Monitoring

### View Logs

Render Dashboard → Your Service → Logs

Look for:
- `[I]` Info messages (successful operations)
- `[W]` Warnings (non-critical issues)
- `[E]` Errors (critical issues)

### Health Checks

Render automatically monitors `/api/health` endpoint. If it fails, Render will restart the service.

## Scaling

### Free Tier Limitations

- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free

### Upgrade Options

For production use, consider upgrading to:
- **Starter Plan** ($7/month) - Always on, no spin-down
- **Standard Plan** ($25/month) - More resources, faster

## Security Best Practices

1. ✅ Never commit `.env` file to Git
2. ✅ Use environment variables for all secrets
3. ✅ Keep `PAPER_TRADING=true` until thoroughly tested
4. ✅ Regularly rotate API keys
5. ✅ Monitor logs for suspicious activity
6. ✅ Use HTTPS only (automatic on Render)

## Auto-Deployment

Render automatically deploys when you push to `main` branch.

To disable auto-deploy:
1. Render Dashboard → Your Service → Settings
2. Uncheck "Auto-Deploy"

## Rollback

If deployment fails:
1. Render Dashboard → Your Service → Events
2. Find previous successful deployment
3. Click "Rollback to this version"

## Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Project Issues**: Check GitHub repository issues

## Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Verify Vercel frontend connects successfully
3. ✅ Run a backtest to validate functionality
4. ✅ Monitor logs for any errors
5. ✅ Set up alerts (optional)

---

**Deployment Complete!** 🎉

Your backend is now running on Render, serving API endpoints only. The frontend on Vercel will consume these APIs.
