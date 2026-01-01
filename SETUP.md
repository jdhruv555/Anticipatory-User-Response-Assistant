# AURA Setup Guide

## Quick Start

### 1. Prerequisites Installation

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ../frontend
npm install
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - Google Cloud credentials for Speech-to-Text
# - OpenAI API key
# - Anthropic API key (optional)
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL, Redis, and Kafka
docker-compose up -d postgres redis kafka

# Wait for services to be ready (check with docker-compose ps)
```

### 4. Database Initialization

```bash
cd backend

# Run migrations
alembic upgrade head

# Or create initial migration if needed
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Install spaCy Model (for NLP)

```bash
python -m spacy download en_core_web_sm
```

### 6. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 7. Access Dashboard

Open browser to: `http://localhost:3000`

## Testing the System

### 1. Test WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Start a call
  ws.send(JSON.stringify({
    type: 'call_start',
    call_id: 'test_call_001',
    customer_id: 'customer_001'
  }));
  
  // Send test audio (base64 encoded)
  ws.send(JSON.stringify({
    type: 'audio_chunk',
    call_id: 'test_call_001',
    audio_data: '<base64_audio_data>',
    speaker: 'customer'
  }));
};
```

### 2. Test REST API

```bash
# Health check
curl http://localhost:8000/health

# Get customer (after creating one)
curl http://localhost:8000/api/v1/customers/customer_001
```

## Common Issues

### Issue: Database Connection Error
**Solution**: 
- Verify PostgreSQL is running: `docker-compose ps postgres`
- Check `.env` has correct database credentials
- Ensure database exists: `createdb aura_db` (if not using Docker)

### Issue: Redis Connection Error
**Solution**:
- Verify Redis is running: `docker-compose ps redis`
- Check Redis connection in `.env`

### Issue: spaCy Model Not Found
**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: Google Speech-to-Text Error
**Solution**:
- Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to path of service account JSON
- Verify the service account has Speech-to-Text API enabled

### Issue: OpenAI API Error
**Solution**:
- Verify `OPENAI_API_KEY` is set in `.env`
- Check API key is valid and has credits

## Development Tips

1. **Hot Reload**: Backend uses `--reload` flag for auto-restart on code changes
2. **Database Migrations**: Always create migrations for schema changes:
   ```bash
   alembic revision --autogenerate -m "Description"
   alembic upgrade head
   ```
3. **Logging**: Check logs in terminal for debugging
4. **WebSocket Testing**: Use browser console or tools like `wscat`

## Next Steps

1. Configure production environment variables
2. Set up monitoring (Grafana/Prometheus)
3. Configure CI/CD pipeline
4. Set up model training pipeline
5. Implement authentication/authorization
6. Add rate limiting
7. Set up backup strategies

## Support

For issues or questions, refer to:
- Architecture documentation: `docs/ARCHITECTURE.md`
- API documentation: `docs/API.md`
- Deployment guide: `docs/DEPLOYMENT.md`

