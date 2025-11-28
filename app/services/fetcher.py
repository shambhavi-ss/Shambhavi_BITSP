from __future__ import annotations

import mimetypes
import io
try:
    import magic
except Exception:
    magic = None
import uuid
from pathlib import Path

import httpx


class DocumentFetcher:
    """Download remote documents to a temporary directory for downstream processing."""

    def __init__(self, temp_dir: Path, timeout_seconds: int = 30) -> None:
        self._temp_dir = temp_dir
        self._timeout_seconds = timeout_seconds

    async def fetch(self, url: str) -> Path:
        """Download the document located at `url` to a temporary file."""
        async with httpx.AsyncClient(
            timeout=self._timeout_seconds, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type")

            # If content-type is generic or missing, try to detect from bytes
            if not content_type or content_type in ("application/octet-stream", "binary/octet-stream"):
                detected_type = None
                # First try python-magic if installed
                if magic:
                    try:
                        detected_type = magic.from_buffer(response.content, mime=True)
                    except Exception:
                        detected_type = None

                # Fall back to simple checks on the first bytes
                if not detected_type:
                    head = response.content[:16]
                    if head.startswith(b"%PDF"):
                        detected_type = "application/pdf"
                    elif head.startswith(b"\x89PNG"):
                        detected_type = "image/png"
                    elif head[0:2] in (b"\xff\xd8", b"\xff\xd9"):
                        detected_type = "image/jpeg"

                if detected_type:
                    content_type = detected_type

            target_path = self._temp_dir / self._build_filename(url, content_type)
            target_path.write_bytes(response.content)
        return target_path

    def _build_filename(self, url: str, content_type: str | None) -> str:
        extension = self._infer_extension(url, content_type) or ".bin"
        return f"{uuid.uuid4().hex}{extension}"

    @staticmethod
    def _infer_extension(url: str, content_type: str | None) -> str | None:
        guessed_type = content_type
        if not guessed_type:
            guessed_type, _ = mimetypes.guess_type(url)
        if guessed_type:
            extension = mimetypes.guess_extension(guessed_type, strict=False)
            if extension:
                return extension

        # Fallback to just using the suffix in the URL path if it exists.
        path_suffix = Path(url.split("?")[0]).suffix
        if path_suffix:
            return path_suffix
        return None

