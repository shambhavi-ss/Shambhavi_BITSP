# Quick Deployment Fix for Render

## Issue
Render can't find the `app/` directory during Docker build because files aren't committed to git properly.

## Solution - Commit All Files

```bash
cd /Users/shambhavisushant/Documents/Datathon

# Make sure you're in the Datathon directory
pwd

# Add all files (this will include app/ directory)
git add .

# Commit everything
git commit -m "Add complete bill extraction API with all dependencies"

# Push to your repository
git push origin main
```

## If Git Repository Wasn't Initialized

If you see "not a git repository" error:

```bash
cd /Users/shambhavisushant/Documents/Datathon

# Initialize git
git init

# Add remote
git remote add origin git@github.com:shambhavi-ss/Datathon.git

# Create main branch
git branch -M main

# Add all files
git add .

# Commit
git commit -m "Initial commit: Bill extraction API for HackRx"

# Push to GitHub
git push -u origin main
```

## Verify Files Are Committed

Check that app/ directory is included:
```bash
git ls-files | grep "app/"
```

You should see:
```
app/__init__.py
app/config.py
app/main.py
app/models/schemas.py
app/services/document_processor.py
app/services/fetcher.py
app/services/llm.py
app/services/ocr.py
app/services/pipeline.py
```

## After Pushing to GitHub

1. Go to Render dashboard
2. Click "Manual Deploy" or "Clear build cache & deploy"
3. Wait for deployment to complete

## Alternative: Simplify Dockerfile

If still having issues, update Dockerfile to copy everything:

```dockerfile
# Instead of:
COPY app/ ./app/

# Use:
COPY . .
```

Then rebuild on Render.

## Environment Variables on Render

Make sure these are set in Render dashboard:
- `GEMINI_API_KEY` = your-actual-api-key
- `GEMINI_MODEL` = gemini-2.5-flash

## Test After Deployment

```bash
curl -X POST https://your-app.onrender.com/extract-bill-data \
  -H "Content-Type: application/json" \
  -d '{"document":"http://example.com/sample.pdf"}'
```

Your endpoint will be:
```
https://your-app-name.onrender.com/extract-bill-data
```
