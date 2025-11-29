from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.models.schemas import DocumentRequest, ExtractionResponse
from app.services.pipeline import BillExtractionPipeline

app = FastAPI(
    title="Bill Extraction API",
    version="0.2.0",
    description="Extract line items, quantities, rates, and totals from invoice/bill documents.",
)

pipeline = BillExtractionPipeline()


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "Bill Extraction API",
        "version": "0.2.0",
        "status": "operational",
        "endpoints": {
            "extract": "/extract-bill-data",
            "docs": "/docs",
            "health": "/health",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "bill-extraction-api"}


@app.post("/extract-bill-data", response_model=ExtractionResponse)
async def extract_bill_data(payload: DocumentRequest) -> ExtractionResponse:
    """
    Extract line items from a medical bill or invoice.
    
    This endpoint processes the document through our pipeline:
    1. Download the document from the provided URL
    2. Convert to images (if PDF)
    3. Extract text using OCR
    4. Structure the data using LLM
    5. Return organized line items with token usage metrics
    """
    try:
        result = await pipeline.run(payload.document)
        return ExtractionResponse(
            is_success=True,
            data=result.data,
            token_usage=result.token_usage,
        )
    except Exception as exc:
        # Return a helpful error message to help debug issues
        raise HTTPException(status_code=400, detail=str(exc)) from exc

