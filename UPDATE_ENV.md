# ⚠️ IMPORTANT: Update Required

## Your .env file needs to be updated!

The Gemini model naming has changed. Please update your `.env` file:

### Current (OLD - won't work):
```
GEMINI_MODEL=gemini-1.5-pro-latest
```

### Updated (NEW - will work):
```
GEMINI_MODEL=gemini-2.5-flash
```

## Quick Fix

Run these commands:

```bash
# Option 1: Edit .env manually
nano .env
# Change GEMINI_MODEL line to: GEMINI_MODEL=gemini-2.5-flash

# Option 2: Use sed (automatic)
sed -i '' 's/GEMINI_MODEL=.*/GEMINI_MODEL=gemini-2.5-flash/' .env

# Then restart your API server
# Press Ctrl+C in the server terminal, then:
uvicorn app.main:app --reload --port 8080
```

## Why This Change?

- ✅ `gemini-2.5-flash` - Latest stable version (November 2025)
- ✅ Fast and efficient
- ✅ Cost-effective
- ✅ Fully supported

## Alternative Models

If you want the highest quality (more expensive):
```
GEMINI_MODEL=gemini-2.5-pro
```

If you want the absolute latest (always up-to-date):
```
GEMINI_MODEL=gemini-flash-latest
```

## Check Available Models

Run this to see all models available with your API key:
```bash
python check_models.py
```

## After Updating

1. Save your `.env` file
2. Restart the API server (Ctrl+C, then start again)
3. Test again: `python test_local.py`

You should see: ✅ Extraction Successful!
