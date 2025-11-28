#!/usr/bin/env python3
"""
Test script for the Bill Extraction API
Run the API server first with: uvicorn app.main:app --reload --port 8080
"""

import asyncio
import json
import sys

import httpx


async def test_extraction(document_url: str, api_base: str = "http://localhost:8080"):
    """Test the bill extraction endpoint with a sample document."""
    print(f"Testing bill extraction for: {document_url}")
    print("-" * 80)

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{api_base}/extract-bill-data",
                json={"document": document_url},
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            result = response.json()

            # Pretty print the result
            print(json.dumps(result, indent=2, default=str))
            print("-" * 80)

            # Summary statistics
            if result.get("is_success"):
                data = result.get("data", {})
                token_usage = result.get("token_usage", {})

                print("\n✅ Extraction Successful!")
                print(f"📄 Total Items Extracted: {data.get('total_item_count', 0)}")
                print(f"📄 Total Pages: {len(data.get('pagewise_line_items', []))}")
                print(
                    f"🪙 Total Tokens Used: {token_usage.get('total_tokens', 0)} "
                    f"(Input: {token_usage.get('input_tokens', 0)}, "
                    f"Output: {token_usage.get('output_tokens', 0)})"
                )

                # Calculate total amount
                total_amount = 0
                for page in data.get("pagewise_line_items", []):
                    for item in page.get("bill_items", []):
                        total_amount += float(item.get("item_amount", 0))

                print(f"💰 Total Amount: {total_amount:.2f}")
                print("\n📋 Page-wise Summary:")
                for page in data.get("pagewise_line_items", []):
                    page_no = page.get("page_no")
                    page_type = page.get("page_type", "Unknown")
                    item_count = len(page.get("bill_items", []))
                    print(f"  - Page {page_no} ({page_type}): {item_count} items")

            else:
                print("❌ Extraction Failed!")
                print(f"Message: {result.get('message', 'Unknown error')}")

        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main entry point."""
    # Sample document URLs from the problem statement
    sample_urls = [
        "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-28T07%3A21%3A28Z&se=2026-11-29T07%3A21%3A00Z&sr=b&sp=r&sig=GTu74m7MsMT1fXcSZ8v92ijcymmu55sRklMfkTPuobc%3D",
    ]

    if len(sys.argv) > 1:
        # Use URL from command line argument
        test_url = sys.argv[1]
    else:
        # Use default sample URL
        test_url = sample_urls[0]

    api_base = "http://localhost:8080"
    if len(sys.argv) > 2:
        api_base = sys.argv[2]

    await test_extraction(test_url, api_base)


if __name__ == "__main__":
    asyncio.run(main())
