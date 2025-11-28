from __future__ import annotations

import mimetypes
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
            target_path = self._temp_dir / self._build_filename(
                url, response.headers.get("content-type")
            )
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

