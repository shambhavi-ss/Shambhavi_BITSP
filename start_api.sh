#!/bin/bash

# Quick Start Script for Bill Extraction API
# This script helps you get the API running quickly

set -e  # Exit on error

echo "🚀 Bill Extraction API - Quick Start"
echo "===================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo ""
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check environment variables
echo ""
echo "🔍 Checking configuration..."

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY is not set"
    echo "   Please set it: export GEMINI_API_KEY='your-key-here'"
    echo "   Or add it to a .env file"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ GEMINI_API_KEY is set"
fi

# Start the API
echo ""
echo "🎯 Starting API server on http://localhost:8080"
echo "==========================================="
echo ""
echo "📝 Available endpoints:"
echo "   - GET  /           - API info"
echo "   - GET  /health     - Health check"
echo "   - POST /extract-bill-data - Extract bill items"
echo "   - GET  /docs       - Interactive API docs"
echo ""
echo "🌐 For public access, run ngrok in another terminal:"
echo "   ./start_ngrok.sh"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "==========================================="
echo ""

# Start uvicorn
uvicorn app.main:app --reload --port 8080
