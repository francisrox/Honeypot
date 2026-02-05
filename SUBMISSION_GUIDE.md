# Honeypot Submission Guide

## Your API Endpoint Details

Your honeypot API is now ready for submission! Here are the details you need:

### Submission Information

**Honeypot API Endpoint URL:**
```
http://localhost:8000/api/message
```

**x-api-key Header:**
```
cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU
```

> [!IMPORTANT]
> **The URL above is for LOCAL testing only.** For actual submission to the validation service, you need a **publicly accessible URL**.

---

## Quick Deployment Options

### Option 1: ngrok (Recommended for Quick Testing)

**Fastest way to get a public URL:**

1. **Download ngrok** from https://ngrok.com/download

2. **Start your API** (if not already running):
   ```bash
   python api.py
   ```

3. **In a new terminal, expose it publicly:**
   ```bash
   ngrok http 8000
   ```

4. **Copy the public URL** from ngrok output (looks like `https://abc123.ngrok-free.app`)

5. **Submit to validator:**
   - **Honeypot API Endpoint URL**: `https://YOUR-NGROK-URL.ngrok-free.app/api/message`
   - **x-api-key**: `cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU`

> [!WARNING]
> Keep ngrok running during validation! The URL expires when you close ngrok.

---

### Option 2: Railway (Free Cloud Deployment)

**For persistent deployment:**

1. Create account at https://railway.app
2. Install Railway CLI: `npm install -g @railway/cli`
3. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Add environment variables in Railway dashboard (copy from `.env`)
5. Get your public URL from Railway dashboard

**Submit to validator:**
- **Honeypot API Endpoint URL**: `https://your-app.railway.app/api/message`
- **x-api-key**: `cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU`

---

## Testing Before Submission

### Test Health Endpoint

```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing
```

**Expected Response:**
```json
{
  "status": "healthy",
  "honeypot_initialized": true,
  "timestamp": "2026-02-05T07:57:48+05:30"
}
```

### Test Message Endpoint

```bash
# PowerShell
$headers = @{
    'Content-Type'='application/json'
    'x-api-key'='cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU'
}
$body = '{"message":"Congratulations! You won 1 crore rupees!"}'
Invoke-WebRequest -Uri http://localhost:8000/api/message -Method POST -Headers $headers -Body $body -UseBasicParsing
```

**Expected Response (Scam Detected):**
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
  }
}
```

---

## Submission Checklist

Before submitting to the Agentic Honey-Pot API Endpoint Tester:

- [ ] API server is running (`python api.py`)
- [ ] Health endpoint returns 200 OK
- [ ] Message endpoint works with authentication
- [ ] API is publicly accessible (via ngrok or cloud deployment)
- [ ] You have the public URL ready
- [ ] You have the API key ready: `cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU`

---

## Troubleshooting

### "Invalid API key"
- Make sure you're using: `cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU`
- Check the header name is exactly: `x-api-key` (lowercase)

### "Honeypot system not initialized"
- Verify Ollama is running: `ollama serve`
- Check `.env` has correct LLM configuration

### API not responding
- Check if `python api.py` is still running
- Look at `honeypot.log` for errors
- Verify port 8000 is not blocked by firewall

---

## Next Steps

1. **Choose deployment method** (ngrok for quick testing, Railway for persistent)
2. **Deploy and get public URL**
3. **Test the public URL** with the commands above (replace localhost with your public URL)
4. **Submit to validation service** with:
   - URL: `https://YOUR-PUBLIC-URL/api/message`
   - API Key: `cncHbfm6SXT8EJ3zF6irhqi-snv8R4WBsL1BA0KcaJU`

Good luck with your submission! 🍯🚀
