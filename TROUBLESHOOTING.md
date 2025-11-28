# Quick Fix Guide

## Issue: Azure Blob Storage URL Expired (403 Error)

The sample URLs from the problem statement have time-limited SAS tokens that expire. This is normal behavior.

### ✅ Solution: Test with Local Files

```bash
# Make sure API server is running in another terminal
uvicorn app.main:app --reload --port 8080

# Test with local sample files
python test_local.py "Sample Document 1.pdf"
```

## Issue: Model Name Error (gemini-1.5-pro-latest not found)

### ✅ Solution: Updated to Use Correct Model Name

The model name has been corrected to `gemini-1.5-pro`.

**If you see this error**, make sure your `.env` file has:
```
GEMINI_MODEL=gemini-1.5-pro
```

Then restart the API server.

## Quick Testing Steps

### 1. Start the API Server

```bash
# Terminal 1
uvicorn app.main:app --reload --port 8080
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 2. Test with Local File

```bash
# Terminal 2
python test_local.py
```

This will automatically find and test with your local sample documents.

## What Files to Test With

You currently have these sample files:
- `Sample Document 1.pdf`
- `Sample Document 2.pdf` (SAmple)
- `Sample Document 3.pdf`

The `test_local.py` script will automatically use the first one it finds.

## Expected Workflow

1. ✅ API server starts successfully
2. ✅ Local HTTP server starts on port 8888
3. ✅ Document is fetched from local server
4. ✅ PDF is converted to images
5. ✅ OCR extracts text from each page
6. ✅ Gemini processes the text
7. ✅ Structured JSON response returned

## Common Issues & Fixes

### "Connection refused"
- **Cause**: API server not running
- **Fix**: Start it with `uvicorn app.main:app --reload --port 8080`

### "GEMINI_API_KEY not set"
- **Cause**: Missing or incorrect .env file
- **Fix**: 
  ```bash
  cp .env.example .env
  # Edit .env and add your actual Gemini API key
  ```

### "Tesseract not found"
- **Cause**: Tesseract OCR not installed
- **Fix**: `brew install tesseract` (macOS)

### "PDF conversion failed"
- **Cause**: Poppler not installed
- **Fix**: `brew install poppler` (macOS)

## Full Setup Commands (Fresh Start)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install system dependencies
brew install tesseract poppler  # macOS
# OR
sudo apt-get install tesseract-ocr poppler-utils  # Linux

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Start API server
uvicorn app.main:app --reload --port 8080

# 5. In another terminal, test
python test_local.py
```

## Success Indicators

You'll know it's working when you see:

```
✅ Extraction Successful!
📄 Total Items Extracted: 15
📄 Total Pages: 2
💰 Total Amount: 12345.67
```

## Need More Help?

- Check [TESTING.md](TESTING.md) for detailed testing guide
- Check [QUICKSTART.md](QUICKSTART.md) for setup guide
- Check [README.md](README.md) for full documentation
