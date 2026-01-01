# 🚀 AURA Quick Start - Services Running!

## ✅ Status: LIVE

Your AURA system is now running locally!

### 🌐 Access Points

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 📊 Running Services

✅ **Backend Server** (uvicorn) - Running on port 8000
✅ **Frontend Dashboard** (React) - Running on port 3000

## Quick Commands

### Check Status
```bash
# Health check
curl http://localhost:8000/health

# Check running processes
ps aux | grep -E "uvicorn|react-scripts"
```

### Stop Services
```bash
# Find and kill processes
pkill -f "uvicorn main:app"
pkill -f "react-scripts start"
```

### Restart Services

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm start
```

## Next Steps

1. **Open the Dashboard**: Navigate to http://localhost:3000 in your browser

2. **Test the API**: Visit http://localhost:8000/docs for interactive API documentation

3. **Optional - Start Database Services** (for full functionality):
   ```bash
   # Start Docker Desktop first, then:
   docker-compose up -d postgres redis
   
   # Run migrations
   cd backend
   source venv/bin/activate
   alembic upgrade head
   ```

4. **Add API Keys** (for full AI functionality):
   - Edit `.env` file
   - Add `OPENAI_API_KEY=your-key`
   - Add `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`
   - Restart backend

## Testing the System

### Test WebSocket Connection
Open browser console (F12) and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('✅ Connected');
ws.onmessage = (e) => console.log('📨', JSON.parse(e.data));
```

### Test REST API
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

## Troubleshooting

**Port already in use?**
```bash
# Find what's using the port
lsof -i :8000
lsof -i :3000

# Kill the process or change ports
```

**Services not responding?**
- Check logs in terminal where services were started
- Verify ports are accessible
- Check firewall settings

**Need to restart?**
- Stop current processes (pkill commands above)
- Restart using the commands in "Restart Services" section

---

🎉 **Your AURA system is ready to use!**

