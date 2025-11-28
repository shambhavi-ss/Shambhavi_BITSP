#!/usr/bin/env python3
"""
List available Gemini models to help choose the right one.
"""

import os
import sys
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    print("❌ google-generativeai not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set in .env file")
    sys.exit(1)

print("🔍 Checking available Gemini models...")
print("=" * 80)

try:
    genai.configure(api_key=api_key)
    
    print("\n✅ API Key is valid!")
    print("\n📋 Available Models:\n")
    
    models = genai.list_models()
    
    # Filter for generative models
    generative_models = []
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            generative_models.append(model)
            print(f"  ✓ {model.name}")
            print(f"    Display Name: {model.display_name}")
            print(f"    Description: {model.description[:100]}...")
            print()
    
    print("=" * 80)
    print(f"\n📊 Found {len(generative_models)} models supporting generateContent")
    
    # Recommend a model
    print("\n💡 Recommended models for this project:")
    print("  - gemini-1.5-flash-latest (Fast, cost-effective)")
    print("  - gemini-1.5-pro-latest (Best quality)")
    print("  - gemini-pro (Stable, widely available)")
    
    print("\n📝 Update your .env file:")
    print("  GEMINI_MODEL=gemini-1.5-flash-latest")
    print("  # or")
    print("  GEMINI_MODEL=gemini-1.5-pro-latest")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your API key is correct")
    print("  2. Ensure you have internet connection")
    print("  3. Verify the API key has proper permissions")
