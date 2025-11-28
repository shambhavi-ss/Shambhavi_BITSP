#!/usr/bin/env python3
"""
Test script for the Bill Extraction API using local files.
This script serves local files via a simple HTTP server for testing.
"""

import asyncio
import json
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

import httpx


class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS enabled."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def start_file_server(directory: Path, port: int = 8888):
    """Start a simple HTTP server in a background thread."""
    import os
    os.chdir(directory)
    
    server = HTTPServer(('', port), CORSHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    return server


async def test_local_file(file_path: Path, api_base: str = "http://localhost:8080"):
    """Test the API with a local file."""
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Start a simple file server
    print(f"🚀 Starting local file server on port 8888...")
    file_server = start_file_server(file_path.parent, 8888)
    time.sleep(1)  # Give server time to start
    
    # Construct local URL
    file_url = f"http://localhost:8888/{file_path.name}"
    
    print(f"📄 Testing file: {file_path.name}")
    print(f"🔗 URL: {file_url}")
    print("-" * 80)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{api_base}/extract-bill-data",
                json={"document": file_url},
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
                    
                    # Show first few items
                    for i, item in enumerate(page.get("bill_items", [])[:3]):
                        name = item.get("item_name", "")[:40]
                        amount = item.get("item_amount", 0)
                        print(f"      {i+1}. {name}: ₹{amount}")
                    
                    if len(page.get("bill_items", [])) > 3:
                        print(f"      ... and {len(page.get('bill_items', [])) - 3} more items")
            
            else:
                print("❌ Extraction Failed!")
                print(f"Message: {result.get('message', 'Unknown error')}")
        
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            # Stop the file server
            file_server.shutdown()


async def main():
    """Main entry point."""
    
    # Find local sample documents
    current_dir = Path.cwd()
    sample_files = list(current_dir.glob("Sample Document *.pdf")) + \
                   list(current_dir.glob("SAmple Document *.pdf"))
    
    if len(sys.argv) > 1:
        # Use file from command line
        test_file = Path(sys.argv[1])
    elif sample_files:
        # Use first sample file found
        test_file = sample_files[0]
        print(f"📁 Found sample files: {[f.name for f in sample_files]}")
        print(f"📄 Using: {test_file.name}\n")
    else:
        print("❌ No sample files found!")
        print("Usage: python test_local.py [path/to/document.pdf]")
        print("\nOr place 'Sample Document *.pdf' files in the current directory.")
        return
    
    api_base = "http://localhost:8080"
    if len(sys.argv) > 2:
        api_base = sys.argv[2]
    
    await test_local_file(test_file, api_base)


if __name__ == "__main__":
    print("🧪 Bill Extraction API - Local File Test")
    print("=" * 80)
    print("Note: Make sure the API server is running on http://localhost:8080")
    print("      Start it with: uvicorn app.main:app --reload --port 8080")
    print("=" * 80 + "\n")
    
    asyncio.run(main())
