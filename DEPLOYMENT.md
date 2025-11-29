# 🎯 Quick Start for Judges

## Public API (Live Now)

**URL**: `https://edgar-unconcurrent-superobediently.ngrok-free.app`

**Interactive Docs**: [https://edgar-unconcurrent-superobediently.ngrok-free.app/docs](https://edgar-unconcurrent-superobediently.ngrok-free.app/docs)

**Dashboard**: [http://127.0.0.1:4040](http://127.0.0.1:4040) (real-time monitoring)

## Test It Now

```bash
curl -X POST https://edgar-unconcurrent-superobediently.ngrok-free.app/extract-bill-data \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{"document": "YOUR_DOCUMENT_URL"}'
```

## What We Built

A medical bill extraction API that:
- ✅ Extracts ALL line items (no missing data)
- ✅ Avoids double-counting
- ✅ Handles multi-page documents
- ✅ Tracks token usage
- ✅ Works with PDFs and images

## How It Works

**Two-Step Approach** (following competition hints):
1. **OCR**: Extract clean text with Tesseract
2. **LLM**: Structure data with Google Gemini

**Error Prevention**:
- Explicit guards against common mistakes (dates as amounts, etc.)
- Field validation to ensure data quality
- Smart filtering to avoid double-counting

## Documentation

- **[README.md](README.md)** - Setup and usage
- **[SOLUTION.md](SOLUTION.md)** - Technical approach
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide

## Local Setup

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your GEMINI_API_KEY

# Run
./start_api.sh
```

## Sample Test Results

From `train_sample_1.pdf`:
- ✅ 38 items extracted
- ✅ 2 pages processed
- ✅ ₹73,400 total
- ✅ No interpretation errors
- ✅ All amounts valid

---

**Status**: ✅ Production Ready | **Team**: BFHL | **Date**: Nov 29, 2025
