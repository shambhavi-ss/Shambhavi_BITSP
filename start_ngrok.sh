#!/bin/bash

# Start Ngrok Helper Script
# This script helps you start the API server and ngrok tunnel

echo "🚀 Bill Extraction API - Ngrok Setup"
echo "====================================="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok is not installed. Install it with:"
    echo "   brew install ngrok/ngrok/ngrok"
    exit 1
fi

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    echo "⚠️  Ngrok is not authenticated yet."
    echo ""
    echo "To authenticate:"
    echo "1. Go to https://dashboard.ngrok.com/signup"
    echo "2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE"
    echo ""
    read -p "Have you already authenticated? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please authenticate ngrok first, then run this script again."
        exit 1
    fi
fi

echo "✅ Ngrok is installed and ready"
echo ""
echo "📋 Instructions:"
echo "1. First, start your API server in another terminal:"
echo "   uvicorn app.main:app --reload --port 8080"
echo ""
echo "2. Then, this script will start ngrok to expose it publicly"
echo ""
read -p "Is your API server running on port 8080? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Please start the API server first:"
    echo "   uvicorn app.main:app --reload --port 8080"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "🌐 Starting ngrok tunnel on port 8080..."
echo "==========================================="
echo ""
echo "Your API will be accessible at the ngrok URL shown below."
echo "Press Ctrl+C to stop ngrok when done."
echo ""
echo "📊 View ngrok dashboard at: http://localhost:4040"
echo ""

# Start ngrok
ngrok http 8080
