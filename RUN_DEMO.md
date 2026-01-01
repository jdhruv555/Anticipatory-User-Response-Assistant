# 🚀 AURA Live Demo - How to Run

## Quick Start

### Option 1: Python Demo Script (Recommended)

```bash
cd /Users/dhruv/AURA
python3 demo_live.py
```

This will show:
- ✅ Full pipeline processing
- ✅ Intent classification
- ✅ Sentiment analysis  
- ✅ Response recommendations
- ✅ Real-time processing times

### Option 2: WebSocket Interactive Demo

1. **Open the HTML demo:**
   ```bash
   open demo_websocket.html
   # Or navigate to: file:///Users/dhruv/AURA/demo_websocket.html
   ```

2. **Make sure backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **In the browser:**
   - Click "Connect WebSocket"
   - Click "Start Call"
   - Enter a customer message
   - Click "Process Message"
   - See real-time results!

### Option 3: Dashboard Demo

1. **Open dashboard:**
   ```bash
   open http://localhost:3000
   ```

2. **Use browser console to test:**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onopen = () => {
       ws.send(JSON.stringify({
           type: 'call_start',
           call_id: 'demo_001',
           customer_id: 'customer_001'
       }));
       ws.send(JSON.stringify({
           type: 'audio_chunk',
           call_id: 'demo_001',
           audio_data: btoa('I need help with my billing'),
           speaker: 'customer'
       }));
   };
   ws.onmessage = (e) => console.log(JSON.parse(e.data));
   ```

## Demo Scenarios

### Scenario 1: Billing Inquiry
```
Customer: "I'm frustrated with my billing statement. There's a $49.99 charge I don't recognize."
Expected: Intent = billing_inquiry, Sentiment = negative
```

### Scenario 2: Technical Support
```
Customer: "I can't log into my account. I keep getting an error."
Expected: Intent = technical_support, Sentiment = neutral
```

### Scenario 3: Refund Request
```
Customer: "I want a refund for my last purchase immediately."
Expected: Intent = refund_request, Sentiment = negative
```

## What You'll See

### Python Demo Output:
- 🎯 Intent classification with confidence scores
- 😊 Sentiment analysis (polarity, emotion)
- 👤 Customer context (type, persona)
- 💡 Ranked response recommendations (top 3)
- 🔮 Predicted customer reactions
- ⏱️ Processing latency

### WebSocket Demo:
- Real-time connection status
- Interactive message sending
- Live results display
- Activity log
- Response recommendations with scores

## Troubleshooting

**Backend not running?**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**WebSocket connection failed?**
- Check backend is running: `curl http://localhost:8000/health`
- Check firewall settings
- Try `ws://127.0.0.1:8000/ws` instead

**No results showing?**
- Check browser console for errors
- Verify WebSocket is connected (green indicator)
- Make sure you started the call before sending messages

## Performance

- **Processing Time**: < 100ms per message
- **Latency**: < 500ms end-to-end
- **Accuracy**: 
  - Intent: ~70-80% (rule-based)
  - Sentiment: ~85% (TextBlob)

---

**Ready to demo!** 🎉

