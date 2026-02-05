# Railway Deployment Guide

## Quick Deploy to Railway (Free & Permanent)

Railway provides free hosting that keeps your API running 24/7 without needing your computer on.

### Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended) or email

### Step 2: Deploy Your Honeypot

#### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd d:\honeypot
   git init
   git add .
   git commit -m "Initial honeypot API"
   git branch -M main
   # Create a new repo on GitHub, then:
   git remote add origin https://github.com/YOUR_USERNAME/honeypot-api.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - In Railway dashboard, click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your `honeypot-api` repository
   - Railway will auto-detect and deploy

#### Option B: Deploy with Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and deploy:**
   ```bash
   cd d:\honeypot
   railway login
   railway init
   railway up
   ```

### Step 3: Configure Environment Variables

In Railway dashboard:

1. Go to your project → **Variables** tab
2. Add these environment variables (copy from your `.env` file):

```
API_KEY=cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU
API_HOST=0.0.0.0
API_PORT=8000
LLM_PROVIDER=ollama
LLM_MODEL=llama2
CONFIDENCE_THRESHOLD=0.3
MAX_MESSAGES=15
MAX_DURATION_MINUTES=30
MIN_ENTITIES_FOR_STOP=3
ENABLE_CONSISTENCY_CHECK=true
TYPING_DELAY_SECONDS=2.0
ENABLE_NORMALIZATION=true
ENABLE_URL_EXPANSION=true
ENABLE_LEGAL_DISCLAIMERS=true
ENABLE_PII_MASKING=true
DATA_RETENTION_DAYS=90
JURISDICTION=IN
LOG_LEVEL=INFO
LOG_FILE_PATH=honeypot.log
```

### Step 4: Get Your Permanent URL

1. In Railway dashboard, go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. You'll get a URL like: `https://honeypot-api-production.up.railway.app`

### Step 5: Submit to Evaluation

**Deployed URL:**
```
https://your-app-name.up.railway.app/api/message
```

**API KEY:**
```
cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU
```

---

## Alternative: Render (Also Free)

If Railway doesn't work, try Render:

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `python api.py`
6. Add environment variables from `.env`
7. Deploy and get your permanent URL

---

## Benefits of Cloud Deployment

✅ **24/7 Uptime** - Runs even when your computer is off
✅ **Permanent URL** - Doesn't change like ngrok
✅ **Free Tier** - Railway/Render offer free hosting
✅ **Auto-restart** - Automatically restarts if it crashes
✅ **HTTPS** - Secure connection by default

---

## Files Created for Deployment

- `Procfile` - Tells Railway how to start your app
- `runtime.txt` - Specifies Python version
- `requirements.txt` - Already exists with dependencies

Your app is ready to deploy! 🚀
