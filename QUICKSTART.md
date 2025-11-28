# Quick Start Guide

Get the Bill Extraction API running in under 5 minutes!

## Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher installed
- Tesseract OCR installed on your system
- Poppler utilities installed (for PDF processing)
- A Google Gemini API key

### Installing System Dependencies

**macOS (using Homebrew):**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases

## Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd /path/to/Datathon

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your API key from: https://makersuite.google.com/app/apikey
```

Your `.env` should look like:
```
GEMINI_API_KEY=your-actual-api-key-here
GEMINI_MODEL=gemini-1.5-pro
```

## Step 3: Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

## Step 4: Test the API

Open a new terminal and run:

```bash
# Using the test script
python test_api.py

# Or using curl
curl -X POST http://localhost:8080/extract-bill-data \
  -H "Content-Type: application/json" \
  -d '{"document":"https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-28T07%3A21%3A28Z&se=2026-11-29T07%3A21%3A00Z&sr=b&sp=r&sig=GTu74m7MsMT1fXcSZ8v92ijcymmu55sRklMfkTPuobc%3D"}'
```

## Step 5: View API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Optional: Download Training Samples

```bash
python download_samples.py
```

This will download and extract ~15 sample documents to the `training_samples/` directory.

## Common Issues

### "Tesseract not found"
- Verify installation: `tesseract --version`
- If installed but not found, set `TESSERACT_CMD` in `.env`:
  ```
  TESSERACT_CMD=/opt/homebrew/bin/tesseract  # macOS with Homebrew
  ```

### "GEMINI_API_KEY not set"
- Ensure `.env` file exists in the project root
- Verify the API key is correct (no quotes needed in .env)
- Restart the server after changing .env

### "Module not found" errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port 8080 already in use
- Use a different port: `uvicorn app.main:app --port 8000`
- Update test commands accordingly

## Next Steps

1. Test with your own documents
2. Review the [main README.md](README.md) for detailed architecture
3. Deploy to your preferred cloud platform
4. Submit your solution!

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review the [Postman collection](https://hackrx.blob.core.windows.net/assets/datathon-IIT/HackRx%20Bill%20Extraction%20API.postman_collection.json) for API specifications
- Examine the training samples for document format examples
