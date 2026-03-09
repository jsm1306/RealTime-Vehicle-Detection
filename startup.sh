#!/bin/bash

# Vehicle Detection App - Local Development Startup Script

echo ""
echo "===================================="
echo "Vehicle Detection Application"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3.10+ is required but not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js 18+ is required but not installed"
    exit 1
fi

echo "[✓] Python and Node.js detected"
echo ""

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo ""
echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

# Start backend in background
echo ""
echo "Starting FastAPI Backend (port 8000)..."
python backend/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Install and start frontend
echo ""
echo "Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "Starting React Frontend (port 3000)..."
echo "Opening browser..."

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

npm start

# Handle cleanup
trap "kill $BACKEND_PID" EXIT
