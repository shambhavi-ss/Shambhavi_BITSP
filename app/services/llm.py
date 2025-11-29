from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import google.generativeai as genai

from app.models.schemas import LLMPageExtraction


@dataclass
class _LLMCallResult:
    page: LLMPageExtraction
    usage: Dict[str, int]


class LLMExtractionService:
    """
    Converts OCR text into structured line-item data using Google Gemini.
    
    This service handles the "understanding" phase - taking potentially noisy
    OCR text and extracting the meaningful line items with proper structure.
    We use careful prompt engineering to avoid common pitfalls like:
    - Confusing dates/invoice numbers with amounts
    - Double-counting items
    - Missing legitimate line items
    """

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name=model)

    async def extract_pages(
        self, pages: Sequence[tuple[int, str]]
    ) -> Tuple[List[LLMPageExtraction], Dict[str, int]]:
        tasks = [self._extract_single(page_no, text) for page_no, text in pages if text]
        if not tasks:
            return [], {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}
        responses = await asyncio.gather(*tasks)
        usage_totals = self._aggregate_usage(result.usage for result in responses)
        return [result.page for result in responses], usage_totals

    async def _extract_single(self, page_no: int, text: str) -> _LLMCallResult:
        return await asyncio.to_thread(self._call_model, page_no, text)

    def _call_model(self, page_no: int, text: str) -> _LLMCallResult:
        prompt = self._build_prompt(page_no, text)
        response = self._model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        message = response.text if hasattr(response, "text") else ""
        payload = json.loads(message or "{}")
        payload.setdefault("page_no", page_no)
        usage = self._extract_usage(response)
        return _LLMCallResult(page=LLMPageExtraction.model_validate(payload), usage=usage)

    @staticmethod
    def _build_prompt(page_no: int, text: str) -> str:
        return (
            "You are an expert billing analyst extracting line items from medical/pharmacy bills.\n\n"
            "TASK: Extract EVERY individual purchasable line item (services, medications, supplies, etc.) from the OCR text below.\n\n"
            "CRITICAL RULES:\n"
            "1. Extract ONLY line items representing actual goods/services purchased WITH A VALID MONETARY AMOUNT\n"
            "2. DO NOT extract subtotals, grand totals, tax lines, summary rows, or headers\n"
            "3. DO NOT extract items without a clear monetary amount\n"
            "4. DO NOT double-count items that appear multiple times\n"
            "5. DO NOT omit any legitimate line items - completeness is critical\n"
            "6. ALWAYS provide item_amount as a number (required field, never null)\n"
            "7. When item_rate and item_quantity exist, verify item_amount = item_rate × item_quantity\n"
            "8. Use numbers only (no currency symbols like ₹, $, etc.)\n"
            "9. Use null for item_rate or item_quantity ONLY if not explicitly mentioned\n"
            "10. Classify page_type based on content:\n"
            "    - 'Bill Detail' for detailed line item pages\n"
            "    - 'Final Bill' for summary/payment pages\n"
            "    - 'Pharmacy' for medication/pharmacy bills\n"
            "    - 'Other' if unsure\n\n"
            "⚠️ CRITICAL: AVOID INTERPRETATION ERRORS ⚠️\n"
            "DO NOT confuse non-monetary fields with amounts! These are NOT amounts:\n"
            "❌ Invoice Numbers (e.g., 'INV-12345', '2024001')\n"
            "❌ Dates/Times (e.g., '01/01/2024', '14:30', '20240101')\n"
            "❌ Patient IDs, Account Numbers, Reference Numbers\n"
            "❌ Quantities without corresponding prices\n"
            "❌ Page numbers, Order numbers\n"
            "❌ Percentages (e.g., '10%' for discount or tax rates)\n"
            "❌ Codes (e.g., 'CPT-99213', 'MED-001')\n\n"
            "✅ ONLY extract values that represent CURRENCY/MONEY for goods or services:\n"
            "- Line item prices/amounts (e.g., 'Consultation: 500')\n"
            "- Service charges\n"
            "- Medication costs\n"
            "- Procedure fees\n\n"
            "If a number appears near labels like 'Date', 'Time', 'Invoice #', 'Patient ID', 'Bill #', etc., it is NOT an amount!\n\n"
            "OUTPUT FORMAT (strict JSON):\n"
            "{\n"
            '  "page_no": <int>,\n'
            '  "page_type": "Bill Detail|Final Bill|Pharmacy|Other",\n'
            '  "items": [\n'
            "    {\n"
            '      "item_name": "<exact name from bill>",\n'
            '      "item_amount": <number (REQUIRED, never null, MUST be currency)>,\n'
            '      "item_rate": <number|null>,\n'
            '      "item_quantity": <number|null>\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "IMPORTANT: Every item MUST have a valid item_amount as a number representing currency. If you cannot determine the monetary amount, do not include that item.\n\n"
            f"PAGE NUMBER: {page_no}\n\n"
            f"OCR TEXT:\n{text}\n\n"
            "Extract all line items now:"
        )

    @staticmethod
    def _extract_usage(response: object) -> Dict[str, int]:
        usage = getattr(response, "usage_metadata", None)
        if not usage:
            return {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}
        return {
            "total_tokens": getattr(usage, "total_token_count", 0) or 0,
            "input_tokens": getattr(usage, "prompt_token_count", 0) or 0,
            "output_tokens": getattr(usage, "candidates_token_count", 0) or 0,
        }

    @staticmethod
    def _aggregate_usage(usages: Sequence[Dict[str, int]]) -> Dict[str, int]:
        totals = {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0}
        for usage in usages:
            for key in totals:
                totals[key] += usage.get(key, 0)
        return totals

