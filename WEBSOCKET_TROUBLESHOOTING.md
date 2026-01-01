# WebSocket Connection Troubleshooting

## Error: "WebSocket error: [object Event]"

This means the backend WebSocket server isn't running or isn't accessible.

## Quick Fix

### 1. Check if Backend is Running
```bash
curl http://localhost:8000/health
```

If it fails, the backend isn't running.

### 2. Start the Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verify WebSocket Endpoint
The WebSocket should be available at: `ws://localhost:8000/ws`

### 4. Test Connection
Open browser console and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('✅ Connected!');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

## Common Issues

### Issue 1: Backend Not Running
**Solution**: Start the backend server (see above)

### Issue 2: Port Already in Use
**Solution**: 
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it or use a different port
```

### Issue 3: CORS/Connection Refused
**Solution**: 
- Check backend logs for errors
- Verify `allow_origins=["*"]` in CORS middleware
- Make sure backend is listening on `0.0.0.0` not just `127.0.0.1`

### Issue 4: WebSocket URL Wrong
**Solution**: 
- Verify URL is `ws://localhost:8000/ws` (not `wss://` or different port)
- Check `REACT_APP_WS_URL` in `.env` if using React

## Quick Start Script

```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then in another terminal:
```bash
# Start frontend (if needed)
cd frontend
npm start
```

## Verification Steps

1. ✅ Backend health check works: `curl http://localhost:8000/health`
2. ✅ Port 8000 is listening: `lsof -i :8000`
3. ✅ WebSocket endpoint exists: Check backend logs for "WebSocket connected"
4. ✅ Browser can connect: Check browser console for connection status

## Fixed Issues

- ✅ Better error messages in WebSocket handlers
- ✅ CORS allows all origins for WebSocket
- ✅ Connection status properly tracked
- ✅ Detailed logging for debugging

---

**If backend is running but WebSocket still fails, check backend logs for errors.**

