from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings
from app.models.schemas import BillItem, ExtractionData, LLMPageExtraction, PageLineItems, TokenUsage
from app.services.document_processor import DocumentProcessor
from app.services.fetcher import DocumentFetcher
from app.services.llm import LLMExtractionService
from app.services.ocr import OCRService


@dataclass
class PipelineResult:
    data: ExtractionData
    token_usage: TokenUsage


class BillExtractionPipeline:
    """End-to-end orchestrator for bill line-item extraction."""

    def __init__(self) -> None:
        settings = get_settings()
        self._fetcher = DocumentFetcher(
            temp_dir=settings.temp_dir, timeout_seconds=settings.request_timeout_seconds
        )
        self._processor = DocumentProcessor(poppler_path=settings.poppler_path)
        self._ocr = OCRService(tesseract_cmd=settings.tesseract_cmd)
        self._llm = (
            LLMExtractionService(api_key=settings.gemini_api_key, model=settings.gemini_model)
            if settings.gemini_api_key
            else None
        )

    async def run(self, document_url: str) -> PipelineResult:
        local_path = await self._fetcher.fetch(str(document_url))
        images = self._processor.to_images(local_path)
        ocr_pages = self._ocr.run(images)

        if not ocr_pages:
            raise ValueError("OCR returned no text for the provided document.")

        if not self._llm:
            raise ValueError("LLM extractor is not configured. Set GEMINI_API_KEY.")

        llm_pages, usage = await self._llm.extract_pages(ocr_pages)
        extraction = self._build_response(llm_pages)
        return PipelineResult(data=extraction, token_usage=TokenUsage(**usage))

    def _build_response(self, pages: list[LLMPageExtraction]) -> ExtractionData:
        if not pages:
            raise ValueError("No structured line items were returned by the LLM.")
        pagewise_data: list[PageLineItems] = []
        total_items = 0

        for page in pages:
            # Filter out items without an amount (likely headers, subtotals, etc.)
            bill_items = [
                BillItem(
                    item_name=item.item_name,
                    item_amount=item.item_amount or 0,  # Default to 0 if None
                    item_rate=item.item_rate,
                    item_quantity=item.item_quantity,
                )
                for item in page.items
                if item.item_amount is not None and item.item_amount > 0  # Only include items with positive amounts
            ]
            total_items += len(bill_items)
            pagewise_data.append(
                PageLineItems(page_no=str(page.page_no), page_type=page.page_type, bill_items=bill_items)
            )

        return ExtractionData(pagewise_line_items=pagewise_data, total_item_count=total_items)

