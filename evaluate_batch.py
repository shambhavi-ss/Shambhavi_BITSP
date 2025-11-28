#!/usr/bin/env python3
"""
Batch evaluation script for testing multiple documents.
This helps assess the accuracy and performance of the extraction API.
"""

import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Any

import httpx


class BillEvaluator:
    """Evaluate bill extraction accuracy and performance."""

    def __init__(self, api_base: str = "http://localhost:8080"):
        self.api_base = api_base
        self.results: List[Dict[str, Any]] = []

    async def evaluate_document(self, document_url: str, expected_total: float = None) -> Dict[str, Any]:
        """Evaluate a single document extraction."""
        print(f"\n{'='*80}")
        print(f"Testing: {document_url[:80]}...")
        print(f"{'='*80}")

        result = {
            "document_url": document_url,
            "success": False,
            "error": None,
            "extraction_data": None,
            "metrics": {},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.api_base}/extract-bill-data",
                    json={"document": document_url},
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()

                result["success"] = data.get("is_success", False)
                result["extraction_data"] = data

                if result["success"]:
                    metrics = self._calculate_metrics(data, expected_total)
                    result["metrics"] = metrics
                    self._print_metrics(metrics)
                else:
                    result["error"] = data.get("message", "Unknown error")
                    print(f"❌ Extraction failed: {result['error']}")

            except httpx.HTTPStatusError as e:
                result["error"] = f"HTTP {e.response.status_code}: {e.response.text}"
                print(f"❌ HTTP Error: {result['error']}")
            except Exception as e:
                result["error"] = str(e)
                print(f"❌ Error: {result['error']}")

        self.results.append(result)
        return result

    def _calculate_metrics(self, data: Dict[str, Any], expected_total: float = None) -> Dict[str, Any]:
        """Calculate extraction metrics."""
        extraction_data = data.get("data", {})
        token_usage = data.get("token_usage", {})

        total_items = extraction_data.get("total_item_count", 0)
        pages = extraction_data.get("pagewise_line_items", [])
        num_pages = len(pages)

        # Calculate extracted total
        extracted_total = Decimal("0")
        items_with_rate_qty = 0
        items_with_consistency = 0

        for page in pages:
            for item in page.get("bill_items", []):
                item_amount = Decimal(str(item.get("item_amount", 0)))
                extracted_total += item_amount

                # Check if rate and quantity are provided
                if item.get("item_rate") is not None and item.get("item_quantity") is not None:
                    items_with_rate_qty += 1

                    # Check consistency: amount ≈ rate × quantity
                    rate = Decimal(str(item["item_rate"]))
                    qty = Decimal(str(item["item_quantity"]))
                    expected_amount = rate * qty

                    # Allow 1% tolerance for rounding
                    if abs(item_amount - expected_amount) / max(item_amount, Decimal("0.01")) < Decimal("0.01"):
                        items_with_consistency += 1

        metrics = {
            "total_items": total_items,
            "total_pages": num_pages,
            "extracted_total": float(extracted_total),
            "items_with_rate_qty": items_with_rate_qty,
            "items_with_consistency": items_with_consistency,
            "consistency_rate": (
                items_with_consistency / items_with_rate_qty if items_with_rate_qty > 0 else 1.0
            ),
            "tokens": {
                "total": token_usage.get("total_tokens", 0),
                "input": token_usage.get("input_tokens", 0),
                "output": token_usage.get("output_tokens", 0),
            },
        }

        if expected_total is not None:
            difference = abs(float(extracted_total) - expected_total)
            accuracy = 1 - (difference / expected_total) if expected_total > 0 else 0
            metrics["expected_total"] = expected_total
            metrics["difference"] = difference
            metrics["accuracy_percent"] = accuracy * 100

        return metrics

    def _print_metrics(self, metrics: Dict[str, Any]):
        """Pretty print metrics."""
        print("\n📊 Extraction Metrics:")
        print(f"  ✅ Success!")
        print(f"  📄 Total Items: {metrics['total_items']}")
        print(f"  📄 Total Pages: {metrics['total_pages']}")
        print(f"  💰 Extracted Total: ₹{metrics['extracted_total']:.2f}")

        if "expected_total" in metrics:
            print(f"  💵 Expected Total: ₹{metrics['expected_total']:.2f}")
            print(f"  📊 Difference: ₹{metrics['difference']:.2f}")
            print(f"  🎯 Accuracy: {metrics['accuracy_percent']:.2f}%")

        print(f"  🔢 Items with Rate & Qty: {metrics['items_with_rate_qty']} / {metrics['total_items']}")
        print(f"  ✓ Consistency Rate: {metrics['consistency_rate']*100:.1f}%")
        print(f"  🪙 Tokens Used: {metrics['tokens']['total']} "
              f"(In: {metrics['tokens']['input']}, Out: {metrics['tokens']['output']})")

    async def evaluate_batch(self, documents: List[Dict[str, Any]]):
        """Evaluate multiple documents."""
        print(f"\n🚀 Starting batch evaluation of {len(documents)} documents...")

        for i, doc in enumerate(documents, 1):
            print(f"\n[{i}/{len(documents)}]")
            url = doc.get("url")
            expected_total = doc.get("expected_total")
            await self.evaluate_document(url, expected_total)

        self._print_summary()

    def _print_summary(self):
        """Print summary statistics."""
        if not self.results:
            return

        print(f"\n{'='*80}")
        print("📈 BATCH EVALUATION SUMMARY")
        print(f"{'='*80}")

        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]

        print(f"\n✅ Successful: {len(successful)} / {len(self.results)}")
        print(f"❌ Failed: {len(failed)} / {len(self.results)}")

        if successful:
            avg_items = sum(r["metrics"]["total_items"] for r in successful) / len(successful)
            avg_tokens = sum(r["metrics"]["tokens"]["total"] for r in successful) / len(successful)
            total_tokens = sum(r["metrics"]["tokens"]["total"] for r in successful)

            print(f"\n📊 Average Items per Document: {avg_items:.1f}")
            print(f"🪙 Average Tokens per Document: {avg_tokens:.0f}")
            print(f"🪙 Total Tokens Used: {total_tokens}")

            with_expected = [r for r in successful if "expected_total" in r["metrics"]]
            if with_expected:
                avg_accuracy = sum(r["metrics"]["accuracy_percent"] for r in with_expected) / len(with_expected)
                print(f"🎯 Average Accuracy: {avg_accuracy:.2f}%")

        if failed:
            print(f"\n❌ Failed Documents:")
            for r in failed:
                print(f"  - {r['document_url'][:60]}...")
                print(f"    Error: {r['error']}")

    def save_results(self, output_path: str = "evaluation_results.json"):
        """Save results to JSON file."""
        output_file = Path(output_path)
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file.absolute()}")


async def main():
    """Main entry point."""
    # Example documents for testing
    # Add your own document URLs and expected totals here
    test_documents = [
        {
            "url": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-28T07%3A21%3A28Z&se=2026-11-29T07%3A21%3A00Z&sr=b&sp=r&sig=GTu74m7MsMT1fXcSZ8v92ijcymmu55sRklMfkTPuobc%3D",
            "expected_total": None,  # Set if you know the expected total
        },
        # Add more documents here:
        # {
        #     "url": "https://example.com/bill2.pdf",
        #     "expected_total": 1500.00,
        # },
    ]

    api_base = "http://localhost:8080"
    if len(sys.argv) > 1:
        api_base = sys.argv[1]

    evaluator = BillEvaluator(api_base=api_base)
    await evaluator.evaluate_batch(test_documents)
    evaluator.save_results()


if __name__ == "__main__":
    asyncio.run(main())
