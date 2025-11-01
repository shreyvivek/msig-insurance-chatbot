#!/bin/bash

echo "🚀 Starting WanderSure..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your API keys!"
        exit 1
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if GROQ_API_KEY is set
if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=your_groq" .env; then
    echo "⚠️  GROQ_API_KEY not set in .env. Please add your Groq API key!"
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1 || {
    echo "❌ Failed to install dependencies. Please run: pip install -r requirements.txt"
    exit 1
}

echo "✅ Dependencies installed"
echo ""
echo "🌐 Starting server on http://localhost:8001"
echo ""

python run_server.py

