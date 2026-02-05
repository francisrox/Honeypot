# Setup Guide: Using Ollama (No API Key Required)

## What is Ollama?

Ollama lets you run LLMs locally on your computer - **completely free, no API keys needed!**

## Installation Steps

### 1. Install Ollama

**Windows:**
1. Download from: https://ollama.com/download
2. Run the installer
3. Ollama will start automatically

**Verify installation:**
```bash
ollama --version
```

### 2. Download a Model

Choose one of these models (smaller = faster, larger = better quality):

**Recommended for this project:**
```bash
# Llama 2 (7B) - Good balance of speed and quality
ollama pull llama2

# OR Mistral (7B) - Faster, good for scam detection
ollama pull mistral

# OR Phi-2 (2.7B) - Very fast, smaller model
ollama pull phi
```

**Verify model downloaded:**
```bash
ollama list
```

### 3. Test Ollama

```bash
ollama run llama2
```

You should see a prompt. Type something and press Enter. If you get a response, it's working!

Type `/bye` to exit.

### 4. Configure the Honeypot

The `.env` file is already configured for Ollama:

```env
LLM_PROVIDER=ollama
LLM_MODEL=llama2  # Change to mistral or phi if you downloaded those
```

**If you want to use a different model**, edit `.env`:
```env
LLM_MODEL=mistral  # or phi
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Honeypot!

```bash
python main.py --demo
```

## Troubleshooting

### "Connection refused" error

**Problem:** Ollama service not running.

**Solution:**
- Windows: Ollama should auto-start. Check system tray for Ollama icon.
- If not running, restart Ollama from Start menu.

### "Model not found" error

**Problem:** Model not downloaded.

**Solution:**
```bash
ollama pull llama2
```

### Slow responses

**Problem:** Model is large for your hardware.

**Solution:** Use a smaller model:
```bash
ollama pull phi
```

Then update `.env`:
```env
LLM_MODEL=phi
```

## Model Comparison

| Model | Size | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| phi | 2.7B | ⚡⚡⚡ Fast | ⭐⭐ Good | Testing, low-end PCs |
| llama2 | 7B | ⚡⚡ Medium | ⭐⭐⭐ Great | **Best balance** |
| mistral | 7B | ⚡⚡ Medium | ⭐⭐⭐ Great | Alternative to llama2 |
| llama2:13b | 13B | ⚡ Slow | ⭐⭐⭐⭐ Excellent | High-end PCs only |

## System Requirements

**Minimum:**
- 8GB RAM
- 4GB free disk space
- CPU: Any modern processor

**Recommended:**
- 16GB RAM
- 8GB free disk space
- GPU (optional, speeds up responses)

## Advantages of Ollama

✅ **Free** - No API costs  
✅ **Private** - Data never leaves your computer  
✅ **Offline** - Works without internet  
✅ **No rate limits** - Use as much as you want  

## Quick Start Commands

```bash
# 1. Install Ollama (download from ollama.com)

# 2. Download model
ollama pull llama2

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run honeypot
python main.py --demo

# 5. Test with mock scammer
python mock_scammer.py
```

## Need Help?

- Ollama docs: https://ollama.com/docs
- Ollama models: https://ollama.com/library
- Check if Ollama is running: `ollama list`

---

**You're all set! No API keys needed. Everything runs locally on your machine.** 🎉
