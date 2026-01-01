# AURA - Anticipatory User Response Assistant

An AI co-pilot system that assists human customer care agents during live calls using real-time sentiment analysis, predictive dialogue planning, and reinforcement learning.

## System Architecture

The system consists of six specialized agents:

1. **Listener Agent**: Automatic Speech Recognition and Turn Detection
2. **Interpreter Agent**: Intent, Sentiment, and Entity Extraction
3. **History & RL Agent**: Customer Profile Retrieval and Persona Selection
4. **Planner Agent**: Dialogue Prediction with 1-2 step look-ahead
5. **Critic/Ranker Agent**: RL-Weighted Response Scoring
6. **Agent Dashboard**: Real-time Display with Context and History

## Key Features

- Real-time speech processing with <3s latency
- Multi-agent collaboration pipeline
- Reinforcement learning feedback loop (PPO)
- Dynamic persona adaptation (8 persona types)
- Predictive dialogue planning with branching predictions

## Tech Stack

- **AI/ML**: Google Speech-to-Text, Anthropic/OpenAI models, PPO, PyTorch
- **Backend**: FastAPI, Apache Kafka, PostgreSQL, Redis
- **Frontend**: React, WebSocket, Tailwind CSS
- **Infrastructure**: Docker, Kubernetes, Grafana/Prometheus

## Quick Start - Local Hosting

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker and Docker Compose

### One-Command Setup (Recommended)

```bash
# Run the automated setup script
./start_local.sh
```

This script will:
1. ✅ Check and create `.env` file from template
2. ✅ Start infrastructure services (PostgreSQL, Redis, Kafka)
3. ✅ Install backend dependencies
4. ✅ Set up database with migrations
5. ✅ Install frontend dependencies

### Manual Setup

1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (OpenAI, Google Cloud, etc.)
   ```

2. **Start infrastructure services:**
   ```bash
   docker-compose up -d postgres redis kafka
   ```

3. **Setup backend:**
   ```bash
   cd backend
   python3 -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   alembic upgrade head
   ```

4. **Setup frontend:**
   ```bash
   cd frontend
   npm install
   ```

5. **Start services (in separate terminals):**

   **Terminal 1 - Backend:**
   ```bash
   ./start_backend.sh
   # Or manually:
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   **Terminal 2 - Frontend:**
   ```bash
   ./start_frontend.sh
   # Or manually:
   cd frontend
   npm start
   ```

6. **Access the system:**
   - Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
AURA/
├── backend/              # FastAPI backend services
│   ├── agents/          # Individual agent implementations
│   ├── api/             # API routes and WebSocket handlers
│   ├── models/          # Database models
│   ├── rl/              # Reinforcement learning components
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API and WebSocket clients
│   │   └── hooks/       # Custom React hooks
├── infrastructure/      # Docker, K8s, monitoring configs
└── docs/                # Documentation

```

## License

MIT

