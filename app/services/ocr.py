from __future__ import annotations

from typing import List, Sequence, Tuple

from PIL import Image
import pytesseract


class OCRService:
    """Wrapper around pytesseract to extract text from images."""

    def __init__(self, tesseract_cmd: str | None = None, lang: str = "eng") -> None:
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self._lang = lang

    def run(self, images: Sequence[Image.Image]) -> List[Tuple[int, str]]:
        """Return list of (page_number, extracted_text)."""
        ocr_results: List[Tuple[int, str]] = []
        for idx, image in enumerate(images, start=1):
            text = pytesseract.image_to_string(image, lang=self._lang)
            cleaned = text.strip()
            ocr_results.append((idx, cleaned))
        return ocr_results

