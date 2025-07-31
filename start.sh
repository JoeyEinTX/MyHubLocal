#!/bin/bash

echo "🔄 Starting MyHubLocal (Backend + Frontend)..."

# 1. Kill any processes using our ports
echo "🛑 Stopping any running processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Kill any lingering processes
pkill -f uvicorn 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

echo "✅ Cleared all existing processes"

# 2. Start Backend
echo "🚀 Starting FastAPI backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 3. Start Frontend
echo "🎨 Starting React frontend..."
cd frontend
npm install -q
npm run dev &
FRONTEND_PID=$!
cd ..

# 4. Wait a moment for servers to start
sleep 3

echo ""
echo "🎉 MyHubLocal is running!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ""; echo "🛑 Stopped MyHubLocal"; exit' INT
wait
