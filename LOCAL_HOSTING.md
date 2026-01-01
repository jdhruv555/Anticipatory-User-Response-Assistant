# Local Hosting Guide for AURA

This guide will help you run AURA on your local machine.

## Prerequisites Check

Before starting, ensure you have:

- ✅ **Python 3.10+** - Check with: `python3 --version`
- ✅ **Node.js 18+** - Check with: `node --version`
- ✅ **Docker & Docker Compose** - Check with: `docker --version` and `docker-compose --version`
- ✅ **API Keys** (optional for basic testing):
  - OpenAI API key (for NLU)
  - Google Cloud credentials (for Speech-to-Text)
  - Anthropic API key (optional, for alternative NLU)

## Quick Start (Automated)

The easiest way to get started:

```bash
# Make scripts executable (first time only)
chmod +x start_local.sh start_backend.sh start_frontend.sh

# Run automated setup
./start_local.sh
```

Then in **two separate terminals**:

**Terminal 1:**
```bash
./start_backend.sh
```

**Terminal 2:**
```bash
./start_frontend.sh
```

## Step-by-Step Manual Setup

### Step 1: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
# At minimum, you'll need:
# - OPENAI_API_KEY (for intent/sentiment analysis)
# - GOOGLE_APPLICATION_CREDENTIALS (for speech-to-text)
```

**Note:** For basic testing without API keys, the system will use fallback rule-based methods, but functionality will be limited.

### Step 2: Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and Kafka using Docker
docker-compose up -d postgres redis kafka zookeeper

# Verify services are running
docker-compose ps

# You should see all services as "Up"
```

**Troubleshooting:**
- If services fail to start, check Docker is running: `docker ps`
- Check ports 5432, 6379, 9092, 2181 are not in use
- View logs: `docker-compose logs postgres`

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy language model (for NLP)
python -m spacy download en_core_web_sm

# Run database migrations
alembic upgrade head
```

**Verify backend setup:**
```bash
# Test database connection
python -c "from models.database import engine; print('Database OK')"

# Test imports
python -c "from agents import ListenerAgent; print('Imports OK')"
```

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### Step 5: Start Services

You need **two terminal windows**:

#### Terminal 1: Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test backend:**
- Open http://localhost:8000/health in browser
- Should return: `{"status": "healthy", ...}`

#### Terminal 2: Frontend Dashboard

```bash
cd frontend
npm start
```

You should see:
```
Compiled successfully!
You can now view aura-dashboard in the browser.
  Local:            http://localhost:3000
```

**Test frontend:**
- Open http://localhost:3000 in browser
- Dashboard should load

## Verifying Everything Works

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "pipeline_initialized": true,
  "active_connections": 0
}
```

### 2. Check Database Connection

```bash
# Using psql (if installed)
psql -h localhost -U aura_user -d aura_db -c "SELECT 1;"

# Or using Python
cd backend
python -c "from models.database import engine; import asyncio; asyncio.run(engine.connect())"
```

### 3. Test WebSocket Connection

Open browser console (F12) and run:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('✅ WebSocket connected');
ws.onerror = (e) => console.error('❌ WebSocket error:', e);
ws.onmessage = (e) => console.log('📨 Message:', JSON.parse(e.data));
```

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/

# API documentation
open http://localhost:8000/docs
```

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database connection refused

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart if needed
docker-compose restart postgres

# Check .env has correct credentials
cat .env | grep POSTGRES
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in uvicorn command
uvicorn main:app --reload --port 8001
```

### Issue: Frontend can't connect to backend

**Solution:**
- Check `REACT_APP_API_URL` in `.env` or `frontend/.env`
- Should be: `http://localhost:8000`
- Restart frontend after changing env vars

### Issue: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
# Or if using virtual environment:
source venv/bin/activate
python -m spacy download en_core_web_sm
```

### Issue: API key errors

**Solution:**
- System will use fallback methods without API keys
- For full functionality, add keys to `.env`:
  - `OPENAI_API_KEY=sk-...`
  - `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`

## Development Workflow

### Making Changes

1. **Backend changes**: Auto-reloads with `--reload` flag
2. **Frontend changes**: Hot-reloads automatically
3. **Database changes**: Create migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description"
   alembic upgrade head
   ```

### Viewing Logs

**Backend logs:** Terminal 1 (where uvicorn is running)

**Frontend logs:** Terminal 2 (where npm start is running)

**Infrastructure logs:**
```bash
docker-compose logs postgres
docker-compose logs redis
docker-compose logs kafka
```

### Stopping Services

**Stop backend/frontend:** `Ctrl+C` in respective terminals

**Stop infrastructure:**
```bash
docker-compose down
# Or stop specific service:
docker-compose stop postgres
```

## Next Steps

Once everything is running:

1. ✅ Test the WebSocket connection
2. ✅ Send test audio data through the pipeline
3. ✅ View response recommendations in dashboard
4. ✅ Check database for stored data
5. ✅ Review API documentation at http://localhost:8000/docs

## Getting Help

- Check logs in terminal windows
- Review `docs/ARCHITECTURE.md for system design
- Review `docs/API.md` for API documentation
- Check `SETUP.md` for additional setup details

## Performance Tips

- **Faster startup**: Pre-install dependencies
- **Better performance**: Use production build for frontend:
  ```bash
  cd frontend
  npm run build
  npm install -g serve
  serve -s build
  ```
- **Database optimization**: Add indexes for frequently queried fields
- **Caching**: Redis is already configured for caching

---

**Happy coding! 🚀**

