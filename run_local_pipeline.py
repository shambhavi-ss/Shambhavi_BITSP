#!/usr/bin/env python3
"""
Run the extraction pipeline locally against a file in the workspace.

Usage:
    python run_local_pipeline.py [path/to/document]

If no path is provided, it will try "Sample Document 1.pdf" in the repo root.
"""
import sys
import json
import asyncio
from pathlib import Path
from decimal import Decimal

from app.config import get_settings
from app.services.document_processor import DocumentProcessor
from app.services.ocr import OCRService
from app.services.llm import LLMExtractionService
from app.models.schemas import BillItem, PageLineItems, ExtractionData


def build_extraction_data(llm_pages):
    pagewise = []
    total = 0
    for page in llm_pages:
        bill_items = []
        for item in page.items:
            # Coerce amounts to numbers/strings for JSON
            amt = item.item_amount if item.item_amount is not None else None
            rate = item.item_rate if item.item_rate is not None else None
            qty = item.item_quantity if item.item_quantity is not None else None
            bill_items.append(
                {
                    "item_name": item.item_name,
                    "item_amount": str(amt) if amt is not None else None,
                    "item_rate": str(rate) if rate is not None else None,
                    "item_quantity": str(qty) if qty is not None else None,
                }
            )
        total += len(bill_items)
        pagewise.append({"page_no": str(page.page_no), "page_type": page.page_type, "bill_items": bill_items})
    return {"pagewise_line_items": pagewise, "total_item_count": total}


async def main():
    settings = get_settings()

    # Determine input file
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path("Sample Document 1.pdf")

    if not path.exists():
        print(f"File not found: {path}")
        return

    print(f"Processing local file: {path}")

    processor = DocumentProcessor(poppler_path=settings.poppler_path)
    ocr = OCRService(tesseract_cmd=settings.tesseract_cmd)

    # Convert to images
    images = processor.to_images(path)
    print(f"Converted to {len(images)} images/pages")

    # OCR
    ocr_pages = ocr.run(images)
    print(f"OCR extracted text from {len(ocr_pages)} pages")

    # LLM extraction
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY not set in .env. LLM extraction skipped.")
        return

    llm = LLMExtractionService(api_key=settings.gemini_api_key, model=settings.gemini_model)
    llm_pages, usage = await llm.extract_pages(ocr_pages)

    print(f"LLM returned {len(llm_pages)} structured pages")

    extraction = build_extraction_data(llm_pages)
    output = {"is_success": True, "token_usage": usage, "data": extraction}

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
