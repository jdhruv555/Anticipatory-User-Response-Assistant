#!/bin/bash

# Start AURA Services
# This script starts both backend and frontend

echo "🚀 Starting AURA Services..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating default..."
    cat > .env << 'EOF'
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aura_db
POSTGRES_USER=aura_user
POSTGRES_PASSWORD=aura_password
REDIS_HOST=localhost
REDIS_PORT=6379
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
EOF
fi

# Start backend in background
echo "📦 Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: tail -f backend.log"
echo ""

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "📦 Starting frontend dashboard..."
cd ../frontend
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: tail -f frontend.log"
echo ""

cd ..

echo "🎉 AURA is starting!"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Dashboard: http://localhost:3000"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "To view logs:"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"

