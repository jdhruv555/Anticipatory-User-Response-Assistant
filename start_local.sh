#!/bin/bash

# AURA Local Startup Script
# This script helps you start the AURA system locally

set -e

echo "🚀 Starting AURA System Locally..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your API keys before continuing.${NC}"
        echo -e "${YELLOW}Press Enter when ready to continue...${NC}"
        read
    else
        echo -e "${RED}❌ .env.example not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Step 1: Start Infrastructure Services
echo -e "${GREEN}📦 Step 1: Starting infrastructure services (PostgreSQL, Redis, Kafka)...${NC}"
docker-compose up -d postgres redis kafka zookeeper

echo "Waiting for services to be ready..."
sleep 5

# Check if services are running
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    exit 1
fi

if ! docker-compose ps | grep -q "redis.*Up"; then
    echo -e "${RED}❌ Redis failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Infrastructure services started${NC}"
echo ""

# Step 2: Install Backend Dependencies
echo -e "${GREEN}📦 Step 2: Installing backend dependencies...${NC}"
cd backend

if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || true

pip install -q -r requirements.txt

# Install spaCy model if not already installed
python3 -m spacy download en_core_web_sm 2>/dev/null || echo "spaCy model already installed or failed"

echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# Step 3: Database Setup
echo -e "${GREEN}📦 Step 3: Setting up database...${NC}"
alembic upgrade head
echo -e "${GREEN}✅ Database setup complete${NC}"
echo ""

cd ..

# Step 4: Install Frontend Dependencies
echo -e "${GREEN}📦 Step 4: Installing frontend dependencies...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
else
    echo "Frontend dependencies already installed"
fi

echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

cd ..

# Step 5: Start Services
echo -e "${GREEN}🎯 Step 5: Starting services...${NC}"
echo ""
echo -e "${YELLOW}⚠️  You'll need to run the backend and frontend in separate terminals.${NC}"
echo ""
echo -e "${GREEN}Terminal 1 - Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate  # or: source .venv/bin/activate"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo -e "${GREEN}Terminal 2 - Frontend:${NC}"
echo "  cd frontend"
echo "  npm start"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${GREEN}Access the dashboard at: http://localhost:3000${NC}"
echo -e "${GREEN}Backend API at: http://localhost:8000${NC}"
echo -e "${GREEN}API docs at: http://localhost:8000/docs${NC}"
echo ""

