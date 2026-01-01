#!/usr/bin/env python3
"""
Quick test script to verify WebSocket results are working
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Start a call
            await websocket.send(json.dumps({
                "type": "call_start",
                "call_id": "test_ws_001",
                "customer_id": "customer_001"
            }))
            print("📞 Sent call_start")
            
            # Wait for response
            response = await websocket.recv()
            print(f"📨 Received: {response[:100]}...")
            
            # Send a message
            message_text = "I need help with my billing statement"
            await websocket.send(json.dumps({
                "type": "audio_chunk",
                "call_id": "test_ws_001",
                "audio_data": message_text.encode('utf-8').hex(),  # Send as hex for testing
                "speaker": "customer"
            }))
            print(f"💬 Sent message: '{message_text}'")
            
            # Wait for results
            print("⏳ Waiting for results...")
            result = await websocket.recv()
            data = json.loads(result)
            
            print("\n" + "="*70)
            print("📊 RESULTS:")
            print("="*70)
            print(f"Status: {data.get('status')}")
            print(f"Call ID: {data.get('call_id')}")
            print(f"Transcript: {data.get('transcript', 'N/A')}")
            
            if data.get('interpretation'):
                intent = data['interpretation'].get('intent', {})
                sentiment = data['interpretation'].get('sentiment', {})
                print(f"\nIntent: {intent.get('intent')} ({intent.get('confidence', 0)*100:.0f}%)")
                print(f"Sentiment: {sentiment.get('sentiment')} ({sentiment.get('emotion')})")
            
            if data.get('ranked_responses'):
                print(f"\n💡 Response Recommendations: {len(data['ranked_responses'])}")
                for i, resp in enumerate(data['ranked_responses'][:3], 1):
                    print(f"\n  {i}. Score: {resp.get('score', 0)*100:.1f}%")
                    print(f"     Text: {resp.get('text', 'N/A')[:80]}...")
            else:
                print("\n❌ No ranked_responses in result!")
                print(f"Available keys: {list(data.keys())}")
            
            print("="*70)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())

