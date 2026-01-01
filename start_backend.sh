#!/bin/bash

# Start AURA Backend Server

cd "$(dirname "$0")/backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "🚀 Starting AURA Backend..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

