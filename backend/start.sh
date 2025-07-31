#!/bin/bash

echo "🔄 Resetting Backend Environment..."

# 1. Kill anything using port 8000
echo "🛑 Stopping any running backend processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Also kill any uvicorn processes that might be stuck
pkill -f uvicorn 2>/dev/null || true

# 2. (Optional) Create venv if missing
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate venv
echo "🔑 Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Start backend
echo "🚀 Starting backend on port 8000..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"
echo ""
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
