# Medical Bill Extraction API# Bill Extraction API



A FastAPI service that extracts line items from medical bills and invoices using OCR and LLM-based structured extraction.This repository contains a FastAPI-based service that downloads multi-page bills, runs OCR over every page, and uses Google Gemini to convert the noisy text into structured line items along with their quantities, rates, and per-page page types. The API returns a page-wise snapshot of every detected item plus aggregated token-usage metrics to evaluate cost and compliance with the HackRx submission contract.



## Overview**📚 Documentation**:

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes

This API processes multi-page medical bills (PDFs and images) and extracts detailed line items including item names, quantities, rates, and amounts. It uses Tesseract OCR for text extraction and Google Gemini for intelligent structured data extraction.- **[SOLUTION.md](SOLUTION.md)** - Comprehensive solution architecture and design decisions



**Quick Links**:## High-level Workflow

- **[QUICKSTART.md](QUICKSTART.md)** - Setup and run in 5 minutes

- **[SOLUTION.md](SOLUTION.md)** - Technical architecture and design decisions1. **Download the document** referenced in the request payload and persist it to a temp folder.

2. **Convert** PDFs into individual page images (single-page images are used as-is).

## How It Works3. **Run OCR** with Tesseract to obtain raw text for each page.

4. **LLM extraction:** send the OCR text to Google Gemini (`gemini-1.5-pro` by default) with a strict JSON output contract to capture structured line items.

1. **Download**: Fetches the document from a provided URL5. **Aggregation:** compute per-page results, total item count, and the overall token usage across all LLM calls.

2. **Convert**: Converts PDFs to images (one per page)

3. **OCR**: Extracts text from each page using Tesseract## Getting Started

4. **Extract**: Uses Google Gemini to structure the OCR text into line items

5. **Aggregate**: Combines results across all pages with token usage metrics### Prerequisites



## Setup- Python 3.11+

- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) installed locally

### Prerequisites- Poppler (`brew install poppler` on macOS) for PDF rasterization

- A Google Gemini API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

- Python 3.11+- (Optional) Download the [training sample pack](https://hackrx.blob.core.windows.net/files/TRAINING_SAMPLES.zip?sv=2025-07-05&spr=https&st=2025-11-28T06%3A47%3A35Z&se=2025-11-29T06%3A47%3A35Z&sr=b&sp=r&sig=yB8R2zjoRL2%2FWRuv7E1lvmWSHAkm%2FoIGsepj2Io9pak%3D) locally for experimentation.

- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html)

- Poppler (for PDF processing): `brew install poppler` on macOS### Installation

- Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

```bash

### Installationpython -m venv .venv

source .venv/bin/activate

```bashpip install -r requirements.txt

# Create virtual environment```

python -m venv .venv

source .venv/bin/activateCreate a `.env` file (or export env vars) with:



# Install dependencies```

pip install -r requirements.txtGEMINI_API_KEY=your-gemini-api-key-here

GEMINI_MODEL=gemini-1.5-pro

# Configure environmentTESSERACT_CMD=/opt/homebrew/bin/tesseract  # optional if tesseract is already on PATH

cp .env.example .env```

# Edit .env and add your GEMINI_API_KEY

```### Running the API



### Running```bash

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

```bash```

# Start the API server

uvicorn app.main:app --reload --port 8080Or use the Makefile for convenience:

```bash

# Or use the convenience scriptmake run

./start_api.sh```

```

Visit http://localhost:8080 to see the API information.

Visit http://localhost:8080 for API info or http://localhost:8080/docs for interactive documentation.

### Example Request

## Usage

```bash

### API Requestcurl -X POST http://localhost:8080/extract-bill-data \

  -H "Content-Type: application/json" \

```bash  -d '{"document":"https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?..."}'

curl -X POST http://localhost:8080/extract-bill-data \```

  -H "Content-Type: application/json" \

  -d '{"document": "https://example.com/medical-bill.pdf"}'### Response Shape

```

```json

### Response Format{

  "is_success": true,

```json  "token_usage": {

{    "total_tokens": 1234,

  "is_success": true,    "input_tokens": 789,

  "token_usage": {    "output_tokens": 445

    "total_tokens": 1234,  },

    "input_tokens": 789,  "data": {

    "output_tokens": 445    "pagewise_line_items": [

  },      {

  "data": {        "page_no": "1",

    "pagewise_line_items": [        "page_type": "Bill Detail",

      {        "bill_items": [

        "page_no": "1",          {

        "page_type": "Bill Detail",            "item_name": "Item 1",

        "bill_items": [            "item_amount": 448,

          {            "item_rate": 32,

            "item_name": "Consultation",            "item_quantity": 14

            "item_amount": 500.0,          }

            "item_rate": 500.0,        ]

            "item_quantity": 1.0      }

          }    ],

        ]    "total_item_count": 1

      }  }

    ],}

    "total_item_count": 1```

  }

}## Accuracy Tips & References

```

- Provide higher-resolution scans or exports to improve OCR fidelity.

## Testing- When bills contain tables, keeping the grid lines improves Tesseract accuracy.

- Use the official [Postman collection](https://hackrx.blob.core.windows.net/assets/datathon-IIT/HackRx%20Bill%20Extraction%20API.postman_collection.json?sv=2025-07-05&spr=https&st=2025-11-28T07%3A21%3A28Z&se=2026-11-29T07%3A21%3A00Z&sr=b&sp=r&sig=GTu74m7MsMT1fXcSZ8v92ijcymmu55sRklMfkTPuobc%3D) to verify parity with the judging harness.

### Test with a sample document

## Solution Architecture

```bash

python test_api.py <document_url>### Core Components



# Example with local file1. **Document Fetcher (`app/services/fetcher.py`)**

python test_local.py "Sample Document 1.pdf"   - Downloads documents from public URLs

```   - Handles multiple content types (images, PDFs)

   - Stores files temporarily with unique identifiers

### Batch testing

2. **Document Processor (`app/services/document_processor.py`)**

```bash   - Converts PDFs to individual page images using pdf2image

python run_local_pipeline.py   - Handles various image formats (PNG, JPG, TIFF, etc.)

```   - Prepares images for OCR processing



## Key Features3. **OCR Service (`app/services/ocr.py`)**

   - Uses Tesseract OCR to extract text from each page

- **Multi-page support** - Handles complex bills across multiple pages   - Returns page-wise text with page numbers

- **Smart extraction** - Distinguishes line items from totals and headers   - Configurable language support

- **Page classification** - Identifies page types (Bill Detail, Pharmacy, etc.)

- **Complete data** - Extracts names, amounts, rates, and quantities4. **LLM Extraction Service (`app/services/llm.py`)**

- **Token tracking** - Reports LLM API usage for cost monitoring   - Leverages Google Gemini 1.5 Pro for structured extraction

- **Flexible input** - Supports PDFs and various image formats   - Converts raw OCR text into structured JSON

   - Handles concurrent processing for multiple pages

## Architecture   - Tracks and aggregates token usage across all API calls



### Two-Step Processing5. **Pipeline Orchestrator (`app/services/pipeline.py`)**

   - Coordinates all services in the correct sequence

Following best practices for document extraction:   - Aggregates results across all pages

   - Ensures no line items are missed or double-counted

**Step 1: OCR Processing**

- Image preprocessing (contrast enhancement, sharpening, upscaling)### Design Decisions

- Optimized Tesseract configuration for structured documents

- Clean, reliable text extraction**Why Tesseract + Gemini?**

- Tesseract provides accurate, cost-free OCR for text extraction

**Step 2: Structured Extraction**- Gemini 1.5 Pro excels at understanding noisy OCR output and extracting structured data

- LLM processes OCR text with explicit instructions- This hybrid approach balances accuracy and cost-effectiveness

- Structured JSON output with validation

- Guards against common interpretation errors**Multi-page Handling**

- Each page is processed independently to avoid context overflow

### Services- LLM extraction runs concurrently for faster processing

- Results are aggregated while maintaining page-level granularity

- **DocumentFetcher** - Downloads and caches documents

- **DocumentProcessor** - Converts PDFs to images**Error Prevention**

- **OCRService** - Extracts text with Tesseract- Strict JSON schema enforcement prevents malformed outputs

- **LLMExtractionService** - Structures data with Gemini- Validation at multiple levels (Pydantic models)

- **BillExtractionPipeline** - Orchestrates the entire flow- Clear prompts to avoid double-counting and ensure completeness



## Deployment**Token Usage Tracking**

- Essential for competition evaluation criteria

### Using Docker- Tracks input, output, and total tokens per page

- Aggregates across all LLM calls for final reporting

```bash

# Build## Key Features

docker build -t bill-extraction-api .

✅ **Accurate Line Item Extraction**: Captures all line items without missing or double-counting  

# Run✅ **Multi-page Support**: Handles complex bills spanning multiple pages  

docker run -p 8080:8080 \✅ **Page Type Classification**: Identifies "Bill Detail", "Final Bill", "Pharmacy", etc.  

  -e GEMINI_API_KEY=your-key \✅ **Quantity & Rate Extraction**: Extracts item quantities and unit rates when available  

  bill-extraction-api✅ **Token Usage Reporting**: Tracks all LLM API usage for cost transparency  

```✅ **Flexible Document Support**: Works with PDFs and various image formats  

✅ **Async Processing**: Fast parallel processing of multi-page documents

### Using Docker Compose

## Problem-Specific Approach

```bash

# Start### Avoiding Double-Counting

docker-compose up -d- Each page is processed independently

- The LLM is explicitly instructed to extract only purchasable line items

# Check logs- Subtotal and total rows are filtered out during extraction

docker-compose logs -f- Page types help identify summary pages vs. detail pages



# Stop### Ensuring Completeness

docker-compose down- High-quality OCR with Tesseract ensures minimal text loss

```- Gemini 1.5 Pro's large context window handles complex layouts

- Explicit prompt instructions emphasize not omitting items

### Cloud Deployment- Validation ensures all extracted items have required fields



The API can be deployed to any platform that supports Docker:### Accuracy Maximization

- **Render** - Connect GitHub repo, add env vars, deploy- The prompt enforces `item_amount = item_rate × item_quantity` consistency

- **Google Cloud Run** - `gcloud run deploy`- Decimal precision for monetary values (no floating-point errors)

- **AWS App Runner** - Deploy from ECR- Page-wise extraction maintains document structure

- **Azure App Service** - Container deployment- Final total is computed by summing all individual line items



Or use ngrok for quick public access:## Deployment

```bash

# Terminal 1: Start API### Docker Deployment

uvicorn app.main:app --port 8080

Build the Docker image:

# Terminal 2: Expose via ngrok

ngrok http 8080```bash

```docker build -t bill-extraction-api .

```

## Project Structure

Run the container:

```

app/```bash

├── main.py                    # FastAPI applicationdocker run -d -p 8080:8080 \

├── config.py                  # Configuration management  -e GEMINI_API_KEY=your-api-key-here \

├── models/  --name bill-extractor \

│   └── schemas.py            # Request/response models  bill-extraction-api

└── services/```

    ├── fetcher.py            # Document download

    ├── document_processor.py # PDF to image conversion### Docker Compose Deployment (Recommended)

    ├── ocr.py                # Text extraction

    ├── llm.py                # Gemini integrationThe easiest way to run the API with Docker:

    └── pipeline.py           # Main orchestration

```bash

test_api.py                    # API testing script# Make sure your .env file has GEMINI_API_KEY set

test_local.py                  # Local file testingdocker-compose up -d

run_local_pipeline.py          # Batch processing```

start_api.sh                   # Quick start script

start_ngrok.sh                 # Ngrok helperCheck status:

``````bash

docker-compose ps

## Design Decisionsdocker-compose logs -f

```

**Why Tesseract + Gemini?**

- Tesseract provides accurate, cost-free OCRStop the service:

- Gemini excels at understanding noisy OCR output```bash

- Hybrid approach balances accuracy and costdocker-compose down

```

**Error Prevention**

- Explicit prompt instructions to avoid interpretation errors### Cloud Deployment Options

- Field validation to ensure monetary values only

- Filtering to prevent double-counting**Render**

- Rate × quantity verification for consistency1. Create a new Web Service

2. Connect your GitHub repository

**Performance**3. Set environment variables in Render dashboard

- Async processing for multiple pages4. Deploy with Docker runtime

- Parallel LLM calls for speed

- Image preprocessing for better OCR quality**Azure App Service**

1. Create a new App Service (Container)

## Troubleshooting2. Configure container registry or GitHub Actions

3. Set application settings (environment variables)

**Tesseract not found**4. Deploy the container

```bash

# macOS**Google Cloud Run**

brew install tesseract```bash

gcloud run deploy bill-extraction-api \

# Ubuntu/Debian  --source . \

apt-get install tesseract-ocr  --platform managed \

```  --region us-central1 \

  --allow-unauthenticated \

**PDF conversion fails**  --set-env-vars GEMINI_API_KEY=your-key

```bash```

# macOS

brew install poppler**AWS App Runner / ECS**

1. Push Docker image to ECR

# Ubuntu/Debian2. Create App Runner service or ECS task definition

apt-get install poppler-utils3. Configure environment variables

```4. Deploy and expose on port 8080



**LLM errors**Any platform that can run a FastAPI + Uvicorn stack works. Package the project, forward port `8080`, and configure the required environment variables in your hosting dashboard or secret manager.

- Verify `GEMINI_API_KEY` is set correctly

- Check API quota limits### Testing the Deployed API

- Ensure stable internet connection

Use the provided `test_api.py` script:

## Contributing

```bash

Built for the HackRx Datathon. Contributions and improvements welcome!python test_api.py <document_url> <your-api-base-url>



## License# Or with Make

make test

MIT License```


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

