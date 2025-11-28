from __future__ import annotations

from pathlib import Path
from typing import List

from pdf2image import convert_from_path
from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}


class DocumentProcessor:
    """Turn PDFs or image files into a list of Pillow Image objects."""

    def __init__(self, poppler_path: str | None = None) -> None:
        self._poppler_path = poppler_path

    def to_images(self, file_path: Path) -> List[Image.Image]:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self._pdf_to_images(file_path)
        if suffix in SUPPORTED_IMAGE_EXTENSIONS:
            return [Image.open(file_path)]
        raise ValueError(f"Unsupported document type: {suffix}")

    def _pdf_to_images(self, file_path: Path) -> List[Image.Image]:
        return convert_from_path(file_path.as_posix(), poppler_path=self._poppler_path)

