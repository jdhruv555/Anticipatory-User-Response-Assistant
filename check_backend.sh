#!/bin/bash
echo "Checking AURA backend status..."
echo ""

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ Backend is NOT running"
    echo ""
    echo "Starting backend..."
    cd backend
    source venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi

