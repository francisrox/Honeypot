# Render Deployment - Step by Step Guide

## Step 1: Create a Render Account (2 minutes)

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with:
   - GitHub (recommended - easiest)
   - OR Google
   - OR Email

**No credit card required!** ✅

---

## Step 2: Prepare Your Code (Already Done!)

Your code is ready with:
- ✅ `requirements.txt` - Dependencies
- ✅ `api.py` - Your API server
- ✅ `.env` - Configuration (we'll add this manually)

---

## Step 3: Deploy to Render

### Option A: Deploy from GitHub (Recommended)

**3A.1: Push to GitHub**

```bash
cd d:\honeypot

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Honeypot API for deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/honeypot-api.git
git push -u origin main
```

**3A.2: Deploy on Render**

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** and authorize Render
3. Select your `honeypot-api` repository
4. Click **"Connect"**

### Option B: Deploy without GitHub (Manual Upload)

**3B.1: Create a ZIP file**

1. Go to `d:\honeypot`
2. Select all files EXCEPT:
   - `__pycache__` folder
   - `*.pyc` files
   - `honeypot.log`
   - `report_*.json` and `report_*.md` files
3. Right-click → **Send to** → **Compressed (zipped) folder**
4. Name it `honeypot-api.zip`

**3B.2: Deploy on Render**

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Scroll down and click **"Public Git repository"**
3. For now, use a placeholder repo, we'll upload manually later

---

## Step 4: Configure Your Service

Fill in these settings:

**Name:**
```
honeypot-api
```

**Region:**
```
Singapore (closest to India)
```

**Branch:**
```
main
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python api.py
```

**Instance Type:**
```
Free
```

---

## Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add each of these (copy from your `.env` file):

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

**Important:** Make sure `API_PORT=8000` is set!

---

## Step 6: Deploy!

1. Click **"Create Web Service"**
2. Wait 2-5 minutes for deployment
3. Watch the build logs - you'll see:
   ```
   Installing dependencies...
   Starting server...
   ✓ Deployed successfully
   ```

---

## Step 7: Get Your Permanent URL

Once deployed, you'll see:

**Your Service URL:**
```
https://honeypot-api.onrender.com
```

**Your API Endpoint:**
```
https://honeypot-api.onrender.com/api/message
```

---

## Step 8: Test Your Deployment

```powershell
# Test health endpoint
Invoke-WebRequest -Uri https://honeypot-api.onrender.com/health -UseBasicParsing

# Test API endpoint
$headers = @{'x-api-key'='cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU'}
Invoke-WebRequest -Uri https://honeypot-api.onrender.com/api/message -Method POST -Headers $headers -UseBasicParsing
```

---

## Step 9: Submit for Evaluation

**Deployed URL:**
```
https://honeypot-api.onrender.com/api/message
```

**API KEY:**
```
cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU
```

---

## Troubleshooting

### Build fails?
- Check that `requirements.txt` is in the root directory
- Make sure Python version is compatible (3.11)

### App crashes on start?
- Check environment variables are set correctly
- Look at the logs in Render dashboard

### Can't connect to API?
- Make sure `API_HOST=0.0.0.0` (not localhost)
- Check that `API_PORT=8000` is set

---

## Important Notes

⚠️ **Free tier limitations:**
- App sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- 750 hours/month free (more than enough)

✅ **For evaluation:**
- The evaluators will wake up your app automatically
- No action needed from you!

---

## Next Steps

1. Follow this guide to deploy
2. Get your permanent URL
3. Submit to evaluation form
4. You're done! 🎉

Your app will run 24/7 without needing your computer on!
