# Deployment Guide

This guide covers deploying the Trading Bot frontend to Vercel and backend to Render.

## Repository Structure

- **Frontend**: `automatic_trading/` - React + TypeScript + Vite
- **Backend**: Python Flask API (`main.py`, `api/flask_api.py`)

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- GitHub repository connected to Vercel

### Steps

1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import `SCARPxVeNOM/angelpredict` repository
   - Select the `automatic_trading` folder as the root directory

2. **Configure Build Settings**
   - **Framework Preset**: Vite
   - **Root Directory**: `automatic_trading`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Environment Variables**
   Add these in Vercel project settings:
   ```
   VITE_API_BASE_URL=https://angelpredict.onrender.com
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy your frontend

### Custom Domain (Optional)
- Add your custom domain in Vercel project settings
- Update DNS records as instructed

## Backend Deployment (Render)

### Prerequisites
- Render account
- GitHub repository connected to Render

### Steps

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `SCARPxVeNOM/angelpredict`

2. **Configure Service**
   - **Name**: `angelpredict-backend` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty (root of repo)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     python main.py
     ```

3. **Environment Variables**
   Add all variables from your `.env` file:
   ```
   TRADING_API_KEY=your_trading_api_key
   TRADING_SECRET_KEY=your_trading_secret_key
   HISTORICAL_API_KEY=your_historical_api_key
   HISTORICAL_SECRET_KEY=your_historical_secret_key
   MARKET_API_KEY=your_market_api_key
   MARKET_SECRET_KEY=your_market_secret_key
   ANGELONE_USERNAME=your_username
   ANGELONE_PASSWORD=your_password
   ANGELONE_MPIN=your_mpin
   USE_MPIN=true
   ANGELONE_TOTP_TOKEN=your_totp_token
   GEMINI_API_KEY=your_gemini_api_key
   ANGELONE_CLIENT_ID=your_client_id
   FLASK_HOST=0.0.0.0
   FLASK_PORT=10000
   FLASK_DEBUG=false
   FRONTEND_URL=https://angelpredict.vercel.app
   ```

   **Important**: 
   - Render uses port `10000` by default, but check your service settings
   - Set `FLASK_DEBUG=false` for production
   - Set `FRONTEND_URL` to your Vercel frontend URL for CORS configuration
   - Never commit `.env` file to Git

4. **Advanced Settings**
   - **Auto-Deploy**: Enable to auto-deploy on push to `main`
   - **Health Check Path**: `/api/health`

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your backend
   - Note the service URL (e.g., `https://angelpredict-backend.onrender.com`)

### Update Frontend API URL

After backend is deployed:

1. Go to Vercel project settings
2. Update environment variable:
   ```
   VITE_API_BASE_URL=https://angelpredict.onrender.com
   ```
3. Redeploy frontend (or wait for auto-deploy)

## Post-Deployment Checklist

- [ ] Backend health check: `https://your-backend.onrender.com/api/health`
- [ ] Frontend loads correctly
- [ ] API calls from frontend work (check browser console)
- [ ] Environment variables are set correctly
- [ ] CORS is enabled (already configured in `flask_api.py`)
- [ ] Backend logs show successful authentication

## Troubleshooting

### Backend Issues

**Port Issues**
- Render uses port `10000` by default
- Update `FLASK_PORT` in environment variables if needed
- Check Render service logs for port conflicts

**Authentication Failures**
- Verify all API keys are correct
- Check MPIN and TOTP token are valid
- Review backend logs in Render dashboard

**CORS Errors**
- Ensure `CORS(self.app)` is enabled in `flask_api.py` (already done)
- Check frontend API URL matches backend URL

### Frontend Issues

**API Connection Errors**
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend is running and accessible
- Review browser console for errors

**Build Failures**
- Check Node.js version compatibility
- Ensure all dependencies are in `package.json`
- Review Vercel build logs

## Environment Variables Reference

### Backend (Render)
```
TRADING_API_KEY
TRADING_SECRET_KEY
HISTORICAL_API_KEY
HISTORICAL_SECRET_KEY
MARKET_API_KEY
MARKET_SECRET_KEY
ANGELONE_USERNAME
ANGELONE_PASSWORD
ANGELONE_MPIN
USE_MPIN
ANGELONE_TOTP_TOKEN
GEMINI_API_KEY
ANGELONE_CLIENT_ID
FLASK_HOST
FLASK_PORT
FLASK_DEBUG
FRONTEND_URL
```

### Frontend (Vercel)
```
VITE_API_BASE_URL
```

## Monitoring

### Backend Logs
- View logs in Render dashboard
- Check for authentication errors
- Monitor API response times

### Frontend Logs
- View build logs in Vercel dashboard
- Check browser console for runtime errors
- Monitor deployment status

## Updates

Both platforms support auto-deployment:
- **Render**: Auto-deploys on push to `main` branch
- **Vercel**: Auto-deploys on push to `main` branch

To manually trigger deployment:
- **Render**: Click "Manual Deploy" → "Deploy latest commit"
- **Vercel**: Click "Redeploy" in deployment history

## Security Notes

- Never commit `.env` files
- Use environment variables for all secrets
- Enable HTTPS (automatic on both platforms)
- Regularly rotate API keys
- Monitor for unauthorized access

## Support

For issues:
1. Check logs in respective dashboards
2. Review error messages
3. Verify environment variables
4. Check GitHub issues



