#!/bin/bash

echo "🍎 WanderSure Setup for macOS"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found!"
    echo "Please install Python 3:"
    echo "  brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ Found: $PYTHON_VERSION"

# Check pip3
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found!"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip3 is available"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your GROQ_API_KEY"
        echo "   Run: nano .env"
        echo ""
        read -p "Press Enter after you've added your GROQ_API_KEY..."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if GROQ_API_KEY is set
if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=your_groq" .env; then
    echo "⚠️  GROQ_API_KEY not set in .env"
    echo "Please edit .env and add your Groq API key:"
    echo "   GROQ_API_KEY=your_key_here"
    exit 1
fi

echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt --user || {
    echo "❌ Failed to install dependencies"
    echo "Trying with sudo..."
    pip3 install -r requirements.txt
}

echo "✅ Dependencies installed"
echo ""
echo "🌐 Starting server on http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 run_server.py

