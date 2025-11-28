# Testing Guide

## Important Note About Sample URLs

⚠️ **The Azure Blob Storage URLs in the problem statement have time-limited SAS tokens that expire.**

The sample URL provided in the problem statement:
```
https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&...
```

Will return a 403 error after the token expiration date. This is expected behavior for Azure Blob Storage.

## Testing Options

### Option 1: Test with Local Files (Recommended)

Use the local test script with the sample PDF files:

```bash
python test_local.py
```

This will:
1. Find sample PDF files in your directory
2. Start a local HTTP server on port 8888
3. Send the file URL to your API for processing
4. Display detailed extraction results

You can also specify a file:
```bash
python test_local.py "Sample Document 1.pdf"
```

### Option 2: Test with Valid Public URLs

If you have your own publicly accessible documents, use:

```bash
python test_api.py "https://your-public-url.com/document.pdf"
```

### Option 3: Upload to Your Own Storage

Upload test documents to:
- Google Cloud Storage (with public access)
- AWS S3 (with public access)
- Any other public file hosting service

Then test with those URLs.

### Option 4: Get Fresh Training Samples

Download the official training samples:

```bash
python download_samples.py
```

**Note:** The download URL in the script may also expire. If it does, contact the competition organizers for a fresh link.

## Running the API Server

Before testing, make sure the API server is running:

```bash
# Terminal 1: Start the API server
uvicorn app.main:app --reload --port 8080
```

```bash
# Terminal 2: Run tests
python test_local.py
```

## Testing Checklist

- [ ] API server is running on http://localhost:8080
- [ ] You have sample documents (PDF or images)
- [ ] Your `.env` file has `GEMINI_API_KEY` set
- [ ] Tesseract OCR is installed
- [ ] Poppler utilities are installed (for PDFs)

## Expected Output

A successful test should show:
```
✅ Extraction Successful!
📄 Total Items Extracted: 15
📄 Total Pages: 2
🪙 Total Tokens Used: 2500 (Input: 2000, Output: 500)
💰 Total Amount: 15234.50

📋 Page-wise Summary:
  - Page 1 (Bill Detail): 12 items
      1. Consultation Fee: ₹500
      2. Lab Test - CBC: ₹300
      3. X-Ray Chest: ₹800
      ... and 9 more items
  - Page 2 (Final Bill): 3 items
```

## Troubleshooting

### "Connection refused" error
- Make sure the API server is running
- Check the port (default: 8080)

### "403 Forbidden" error
- The Azure SAS token has expired
- Use local files instead with `test_local.py`

### "File not found" error
- Check the file path
- Ensure the file exists in the current directory

### "GEMINI_API_KEY not set" error
- Create a `.env` file from `.env.example`
- Add your Gemini API key
- Restart the API server

### OCR or PDF errors
- Install Tesseract: `brew install tesseract` (macOS)
- Install Poppler: `brew install poppler` (macOS)

## Alternative: Use Postman

1. Import the [official Postman collection](https://hackrx.blob.core.windows.net/assets/datathon-IIT/HackRx%20Bill%20Extraction%20API.postman_collection.json)
2. Update the request body with a valid document URL
3. Send the request to your deployed API endpoint

## Need Help?

Check the main [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md) for more detailed setup instructions.
