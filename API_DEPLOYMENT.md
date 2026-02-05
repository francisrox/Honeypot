# Honeypot API Deployment Guide

This guide explains how to deploy your honeypot API endpoint for submission to the validation service.

## Quick Start (Local Testing)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` and set a secure API key:

```env
API_KEY=your-secret-api-key-here
```

**Generate a secure key:**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 3. Start the API Server

```bash
python api.py
```

The server will start on `http://localhost:8000`

### 4. Test Locally

```bash
# Health check
curl http://localhost:8000/health

# Test with scam message
curl -X POST http://localhost:8000/api/message ^
  -H "Content-Type: application/json" ^
  -H "x-api-key: your-secret-api-key-here" ^
  -d "{\"message\": \"Congratulations! You won 1 crore rupees!\"}"
```

---

## Public Deployment Options

For submission to the validation service, your API must be publicly accessible. Choose one:

### Option 1: ngrok (Fastest - For Testing)

**Best for:** Quick testing and hackathon submissions

```bash
# Install ngrok from https://ngrok.com/download

# Start your API
python api.py

# In another terminal, expose it
ngrok http 8000
```

You'll get a public URL like: `https://abc123.ngrok-free.app`

**Submit to validator:**
- **Honeypot API Endpoint URL**: `https://abc123.ngrok-free.app/api/message`
- **x-api-key**: Your API key from `.env`

> [!WARNING]
> ngrok free URLs expire when you close the tunnel. Keep it running during validation.

---

### Option 2: Railway (Free Tier)

**Best for:** Persistent deployment with zero config

1. **Create account** at [railway.app](https://railway.app)

2. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

4. **Add environment variables** in Railway dashboard:
   - `API_KEY`: Your secure API key
   - All other variables from `.env`

5. **Get public URL** from Railway dashboard

**Submit to validator:**
- **Honeypot API Endpoint URL**: `https://your-app.railway.app/api/message`
- **x-api-key**: Your API key

---

### Option 3: Render (Free Tier)

**Best for:** Simple deployment with web UI

1. **Create account** at [render.com](https://render.com)

2. **Create new Web Service:**
   - Connect your GitHub repo (or upload code)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api.py`

3. **Add environment variables** in Render dashboard (copy from `.env`)

4. **Deploy** and get public URL

**Submit to validator:**
- **Honeypot API Endpoint URL**: `https://your-app.onrender.com/api/message`
- **x-api-key**: Your API key

---

### Option 4: Heroku

**Best for:** Production-grade deployment

1. **Install Heroku CLI** from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Procfile:**
   ```
   web: python api.py
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-honeypot-api
   git push heroku main
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set API_KEY=your-secret-key
   heroku config:set LLM_PROVIDER=ollama
   # ... other variables
   ```

**Submit to validator:**
- **Honeypot API Endpoint URL**: `https://your-honeypot-api.herokuapp.com/api/message`
- **x-api-key**: Your API key

---

## API Endpoints

### `GET /health`
Health check endpoint (no authentication required)

**Response:**
```json
{
  "status": "healthy",
  "honeypot_initialized": true,
  "timestamp": "2026-02-05T07:57:48+05:30"
}
```

### `POST /api/message`
Process scam message through honeypot (requires authentication)

**Headers:**
- `Content-Type: application/json`
- `x-api-key: your-api-key-here`

**Request Body:**
```json
{
  "message": "Congratulations! You won 1 crore rupees!",
  "sender": "+919876543210"  // optional
}
```

**Response (Scam Detected):**
```json
{
  "success": true,
  "honeypot_activated": true,
  "detection_result": {
    "is_scam": true,
    "confidence": 0.92,
    "scam_type": "prize_scam"
  },
  "victim_response": "Wow! Really? How do I claim it?",
  "conversation_summary": {
    "messages_exchanged": 1,
    "stop_reason": "demo_mode",
    "scam_type": "prize_scam",
    "confidence": 0.92
  },
  "message": "Message processed successfully"
}
```

**Response (Legitimate Message):**
```json
{
  "success": true,
  "honeypot_activated": false,
  "detection_result": {
    "is_scam": false,
    "confidence": 0.15,
    "scam_type": "unknown"
  },
  "message": "Message appears legitimate - honeypot not activated"
}
```

---

## Submission Checklist

Before submitting to the validation service:

- [ ] API is publicly accessible
- [ ] `/health` endpoint returns 200 OK
- [ ] `/api/message` requires `x-api-key` header
- [ ] `/api/message` returns proper JSON responses
- [ ] Tested with sample scam message
- [ ] API key is secure and not shared publicly
- [ ] Environment variables are properly configured

---

## Troubleshooting

### "API key not configured on server"
- Ensure `API_KEY` is set in `.env` or deployment environment variables

### "Honeypot system not initialized"
- Check `LLM_PROVIDER` and `LLM_API_KEY` are configured correctly
- For Ollama, ensure Ollama is running locally or use a cloud LLM provider

### "Invalid API key"
- Verify the `x-api-key` header matches your configured `API_KEY`
- Check for extra spaces or quotes in the key

### Deployment fails
- Ensure all dependencies in `requirements.txt` are compatible
- Check deployment logs for specific errors
- Verify Python version is 3.8+

---

## Security Notes

> [!CAUTION]
> - **Never commit** your `.env` file with real API keys to Git
> - Use strong, random API keys (32+ characters)
> - For production, implement rate limiting and IP whitelisting
> - Monitor API usage and set up alerts for suspicious activity

---

## Support

For issues or questions:
1. Check the logs: `honeypot.log`
2. Test locally first with `python api.py`
3. Verify environment variables are loaded correctly
4. Review the main README.md for honeypot configuration
