#!/usr/bin/env python3
"""
Download and extract training samples for local testing.
"""

import asyncio
import os
import zipfile
from pathlib import Path

import httpx


async def download_training_samples():
    """Download the training samples ZIP file."""
    url = (
        "https://hackrx.blob.core.windows.net/files/TRAINING_SAMPLES.zip"
        "?sv=2025-07-05&spr=https&st=2025-11-28T06%3A47%3A35Z"
        "&se=2025-11-29T06%3A47%3A35Z&sr=b&sp=r"
        "&sig=yB8R2zjoRL2%2FWRuv7E1lvmWSHAkm%2FoIGsepj2Io9pak%3D"
    )

    output_dir = Path("training_samples")
    output_dir.mkdir(exist_ok=True)

    zip_path = output_dir / "TRAINING_SAMPLES.zip"

    print("📥 Downloading training samples...")
    print(f"URL: {url[:80]}...")

    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            with open(zip_path, "wb") as f:
                f.write(response.content)

            print(f"✅ Downloaded: {zip_path} ({len(response.content) / 1024 / 1024:.2f} MB)")

            # Extract the ZIP file
            print("📂 Extracting files...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(output_dir)

            print(f"✅ Extracted to: {output_dir}")

            # List extracted files
            extracted_files = list(output_dir.glob("**/*"))
            document_files = [
                f for f in extracted_files if f.is_file() and f.suffix.lower() in [".pdf", ".png", ".jpg", ".jpeg"]
            ]

            print(f"\n📄 Found {len(document_files)} document files:")
            for doc in sorted(document_files):
                print(f"  - {doc.relative_to(output_dir)}")

            # Clean up ZIP file
            zip_path.unlink()
            print(f"\n🧹 Cleaned up: {zip_path}")

            print("\n✨ Training samples are ready!")
            print(f"📁 Location: {output_dir.absolute()}")

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(download_training_samples())
