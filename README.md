# Bill Extraction API

This repository contains a FastAPI-based service that downloads multi-page bills, runs OCR over every page, and uses Google Gemini to convert the noisy text into structured line items along with their quantities, rates, and per-page page types. The API returns a page-wise snapshot of every detected item plus aggregated token-usage metrics to evaluate cost and compliance with the HackRx submission contract.

**📚 Documentation**:
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[SOLUTION.md](SOLUTION.md)** - Comprehensive solution architecture and design decisions

## High-level Workflow

1. **Download the document** referenced in the request payload and persist it to a temp folder.
2. **Convert** PDFs into individual page images (single-page images are used as-is).
3. **Run OCR** with Tesseract to obtain raw text for each page.
4. **LLM extraction:** send the OCR text to Google Gemini (`gemini-1.5-pro` by default) with a strict JSON output contract to capture structured line items.
5. **Aggregation:** compute per-page results, total item count, and the overall token usage across all LLM calls.

## Getting Started

### Prerequisites

- Python 3.11+
- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) installed locally
- Poppler (`brew install poppler` on macOS) for PDF rasterization
- A Google Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))
- (Optional) Download the [training sample pack](https://hackrx.blob.core.windows.net/files/TRAINING_SAMPLES.zip?sv=2025-07-05&spr=https&st=2025-11-28T06%3A47%3A35Z&se=2025-11-29T06%3A47%3A35Z&sr=b&sp=r&sig=yB8R2zjoRL2%2FWRuv7E1lvmWSHAkm%2FoIGsepj2Io9pak%3D) locally for experimentation.

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (or export env vars) with:

```
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro
TESSERACT_CMD=/opt/homebrew/bin/tesseract  # optional if tesseract is already on PATH
```

### Running the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Or use the Makefile for convenience:
```bash
make run
```

Visit http://localhost:8080 to see the API information.

### Example Request

```bash
curl -X POST http://localhost:8080/extract-bill-data \
  -H "Content-Type: application/json" \
  -d '{"document":"https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?..."}'
```

### Response Shape

```json
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 1234,
    "input_tokens": 789,
    "output_tokens": 445
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Item 1",
            "item_amount": 448,
            "item_rate": 32,
            "item_quantity": 14
          }
        ]
      }
    ],
    "total_item_count": 1
  }
}
```

## Accuracy Tips & References

- Provide higher-resolution scans or exports to improve OCR fidelity.
- When bills contain tables, keeping the grid lines improves Tesseract accuracy.
- Use the official [Postman collection](https://hackrx.blob.core.windows.net/assets/datathon-IIT/HackRx%20Bill%20Extraction%20API.postman_collection.json?sv=2025-07-05&spr=https&st=2025-11-28T07%3A21%3A28Z&se=2026-11-29T07%3A21%3A00Z&sr=b&sp=r&sig=GTu74m7MsMT1fXcSZ8v92ijcymmu55sRklMfkTPuobc%3D) to verify parity with the judging harness.

## Solution Architecture

### Core Components

1. **Document Fetcher (`app/services/fetcher.py`)**
   - Downloads documents from public URLs
   - Handles multiple content types (images, PDFs)
   - Stores files temporarily with unique identifiers

2. **Document Processor (`app/services/document_processor.py`)**
   - Converts PDFs to individual page images using pdf2image
   - Handles various image formats (PNG, JPG, TIFF, etc.)
   - Prepares images for OCR processing

3. **OCR Service (`app/services/ocr.py`)**
   - Uses Tesseract OCR to extract text from each page
   - Returns page-wise text with page numbers
   - Configurable language support

4. **LLM Extraction Service (`app/services/llm.py`)**
   - Leverages Google Gemini 1.5 Pro for structured extraction
   - Converts raw OCR text into structured JSON
   - Handles concurrent processing for multiple pages
   - Tracks and aggregates token usage across all API calls

5. **Pipeline Orchestrator (`app/services/pipeline.py`)**
   - Coordinates all services in the correct sequence
   - Aggregates results across all pages
   - Ensures no line items are missed or double-counted

### Design Decisions

**Why Tesseract + Gemini?**
- Tesseract provides accurate, cost-free OCR for text extraction
- Gemini 1.5 Pro excels at understanding noisy OCR output and extracting structured data
- This hybrid approach balances accuracy and cost-effectiveness

**Multi-page Handling**
- Each page is processed independently to avoid context overflow
- LLM extraction runs concurrently for faster processing
- Results are aggregated while maintaining page-level granularity

**Error Prevention**
- Strict JSON schema enforcement prevents malformed outputs
- Validation at multiple levels (Pydantic models)
- Clear prompts to avoid double-counting and ensure completeness

**Token Usage Tracking**
- Essential for competition evaluation criteria
- Tracks input, output, and total tokens per page
- Aggregates across all LLM calls for final reporting

## Key Features

✅ **Accurate Line Item Extraction**: Captures all line items without missing or double-counting  
✅ **Multi-page Support**: Handles complex bills spanning multiple pages  
✅ **Page Type Classification**: Identifies "Bill Detail", "Final Bill", "Pharmacy", etc.  
✅ **Quantity & Rate Extraction**: Extracts item quantities and unit rates when available  
✅ **Token Usage Reporting**: Tracks all LLM API usage for cost transparency  
✅ **Flexible Document Support**: Works with PDFs and various image formats  
✅ **Async Processing**: Fast parallel processing of multi-page documents

## Problem-Specific Approach

### Avoiding Double-Counting
- Each page is processed independently
- The LLM is explicitly instructed to extract only purchasable line items
- Subtotal and total rows are filtered out during extraction
- Page types help identify summary pages vs. detail pages

### Ensuring Completeness
- High-quality OCR with Tesseract ensures minimal text loss
- Gemini 1.5 Pro's large context window handles complex layouts
- Explicit prompt instructions emphasize not omitting items
- Validation ensures all extracted items have required fields

### Accuracy Maximization
- The prompt enforces `item_amount = item_rate × item_quantity` consistency
- Decimal precision for monetary values (no floating-point errors)
- Page-wise extraction maintains document structure
- Final total is computed by summing all individual line items

## Deployment

### Docker Deployment

Build the Docker image:

```bash
docker build -t bill-extraction-api .
```

Run the container:

```bash
docker run -d -p 8080:8080 \
  -e GEMINI_API_KEY=your-api-key-here \
  --name bill-extractor \
  bill-extraction-api
```

### Docker Compose Deployment (Recommended)

The easiest way to run the API with Docker:

```bash
# Make sure your .env file has GEMINI_API_KEY set
docker-compose up -d
```

Check status:
```bash
docker-compose ps
docker-compose logs -f
```

Stop the service:
```bash
docker-compose down
```

### Cloud Deployment Options

**Render**
1. Create a new Web Service
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy with Docker runtime

**Azure App Service**
1. Create a new App Service (Container)
2. Configure container registry or GitHub Actions
3. Set application settings (environment variables)
4. Deploy the container

**Google Cloud Run**
```bash
gcloud run deploy bill-extraction-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key
```

**AWS App Runner / ECS**
1. Push Docker image to ECR
2. Create App Runner service or ECS task definition
3. Configure environment variables
4. Deploy and expose on port 8080

Any platform that can run a FastAPI + Uvicorn stack works. Package the project, forward port `8080`, and configure the required environment variables in your hosting dashboard or secret manager.

### Testing the Deployed API

Use the provided `test_api.py` script:

```bash
python test_api.py <document_url> <your-api-base-url>

# Or with Make
make test
```

Example:
```bash
python test_api.py "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?..." "https://your-app.render.com"
```

For batch evaluation:
```bash
python evaluate_batch.py
# Or
make evaluate
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8080/docs
- **Alternative docs**: http://localhost:8080/redoc

## Troubleshooting

**OCR Issues**
- Ensure Tesseract is installed: `tesseract --version`
- For macOS: `brew install tesseract`
- For Ubuntu/Debian: `apt-get install tesseract-ocr`

**PDF Processing Issues**
- Ensure Poppler is installed: `pdftoppm -v`
- For macOS: `brew install poppler`
- For Ubuntu/Debian: `apt-get install poppler-utils`

**LLM Errors**
- Verify your Gemini API key is valid
- Check API quota and rate limits
- Ensure `GEMINI_API_KEY` environment variable is set

**Token Usage Concerns**
- Gemini 1.5 Pro offers generous free tier limits
- Monitor usage in the response `token_usage` field
- Consider using `gemini-1.5-flash` for lower cost (update `GEMINI_MODEL`)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── main.py                # FastAPI application entry point
│   ├── models/
│   │   └── schemas.py         # Pydantic models for request/response
│   ├── services/
│   │   ├── document_processor.py  # PDF to image conversion
│   │   ├── fetcher.py            # Document download service
│   │   ├── llm.py                # Gemini LLM integration
│   │   ├── ocr.py                # Tesseract OCR service
│   │   └── pipeline.py           # Main orchestration pipeline
│   └── utils/
├── tmp/                       # Temporary file storage
├── .env.example              # Environment variable template
├── .gitignore               # Git ignore patterns
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Container definition
├── download_samples.py      # Script to download training samples
├── evaluate_batch.py        # Batch evaluation and accuracy testing
├── Makefile                 # Convenient command shortcuts
├── QUICKSTART.md           # Quick start guide
├── README.md                # This file
├── requirements.txt         # Python dependencies
└── test_api.py             # API testing script
```

## Helper Scripts

### `test_api.py`
Test the API with a single document:
```bash
python test_api.py [document_url] [api_base_url]
```

### `evaluate_batch.py`
Evaluate multiple documents and calculate accuracy metrics:
```bash
python evaluate_batch.py [api_base_url]
```
Outputs detailed metrics including:
- Item counts and totals
- Token usage statistics
- Accuracy percentage (if expected totals provided)
- Consistency validation (rate × quantity = amount)

### `download_samples.py`
Download the official training samples:
```bash
python download_samples.py
# Or
make samples
```

## Contributing

This project was developed for the HackRx Datathon competition. Feel free to fork and improve!

## License

MIT License - feel free to use this code for your own projects.

