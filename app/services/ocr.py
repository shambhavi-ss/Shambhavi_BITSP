from __future__ import annotations

from typing import List, Sequence, Tuple

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


class OCRService:
    """
    Extracts text from images using Tesseract OCR.
    
    This is Step A of our two-step approach (per the competition hints):
    We focus on getting clean, reliable text output before sending it to the LLM.
    
    To improve OCR quality, we preprocess images by:
    - Upscaling low-resolution images
    - Enhancing contrast for better text visibility
    - Sharpening to improve edge definition
    """

    def __init__(self, tesseract_cmd: str | None = None, lang: str = "eng") -> None:
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self._lang = lang

    def run(self, images: Sequence[Image.Image]) -> List[Tuple[int, str]]:
        """
        Return list of (page_number, extracted_text).
        
        Applies preprocessing to improve OCR quality:
        - Image enhancement (contrast, sharpness)
        - Optimal configuration for Tesseract
        """
        ocr_results: List[Tuple[int, str]] = []
        for idx, image in enumerate(images, start=1):
            # Preprocess image for better OCR quality
            enhanced_image = self._preprocess_image(image)
            
            # Use optimized Tesseract config for structured documents
            custom_config = r'--oem 3 --psm 6'  # OEM 3 = Default, PSM 6 = Assume uniform block of text
            text = pytesseract.image_to_string(
                enhanced_image, 
                lang=self._lang,
                config=custom_config
            )
            cleaned = text.strip()
            ocr_results.append((idx, cleaned))
        return ocr_results
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.
        
        Techniques:
        - Convert to RGB (if needed)
        - Enhance contrast for better text visibility
        - Sharpen to improve edge definition
        - Upscale if image is too small
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Upscale if image is small (improves OCR on low-res images)
        min_dimension = 1500
        width, height = image.size
        if width < min_dimension or height < min_dimension:
            scale_factor = max(min_dimension / width, min_dimension / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Enhance contrast for better text visibility
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # Increase contrast by 50%
        
        # Sharpen for better edge definition
        image = image.filter(ImageFilter.SHARPEN)
        
        return image

