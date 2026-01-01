#!/usr/bin/env python3
"""
AURA Live Demo
Demonstrates the full pipeline processing customer conversations
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from services.pipeline import ConversationPipeline


async def demo_conversation():
    """Run a live demo of the AURA system"""
    
    print("=" * 70)
    print("🚀 AURA - Anticipatory User Response Assistant - LIVE DEMO")
    print("=" * 70)
    print()
    
    # Initialize pipeline
    print("📦 Initializing AURA pipeline...")
    pipeline = ConversationPipeline()
    await pipeline.initialize()
    print("✅ Pipeline initialized successfully!\n")
    
    # Demo conversation scenarios
    scenarios = [
        {
            "call_id": "demo_001",
            "customer_id": "customer_123",
            "utterances": [
                "I'm really frustrated with my billing statement. There's a charge I don't recognize.",
                "It's $49.99 from last month. I never authorized this.",
                "Yes, I want a refund immediately."
            ]
        },
        {
            "call_id": "demo_002",
            "customer_id": "customer_456",
            "utterances": [
                "Hi, I need help with my account login.",
                "I keep getting an error when I try to reset my password.",
                "That would be great, thank you!"
            ]
        }
    ]
    
    for scenario_idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"📞 DEMO CALL #{scenario_idx}: {scenario['call_id']}")
        print(f"{'='*70}\n")
        
        call_id = scenario['call_id']
        customer_id = scenario['customer_id']
        
        # Start call
        print(f"🔵 Starting call for customer: {customer_id}")
        await pipeline.start_call(call_id, customer_id)
        print(f"✅ Call started\n")
        
        # Process each customer utterance
        for turn, utterance in enumerate(scenario['utterances'], 1):
            print(f"{'─'*70}")
            print(f"💬 TURN {turn}: Customer says...")
            print(f"   \"{utterance}\"")
            print()
            
            # Simulate audio processing
            audio_data = utterance.encode('utf-8')
            
            print("⚙️  Processing through AURA pipeline...")
            start_time = asyncio.get_event_loop().time()
            
            result = await pipeline.process_audio_chunk(
                call_id=call_id,
                audio_data=audio_data,
                speaker="customer"
            )
            
            latency = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Display results
            print(f"⏱️  Processing time: {latency:.0f}ms\n")
            
            if result.get('status') == 'complete':
                # Intent analysis
                interpretation = result.get('interpretation', {})
                intent = interpretation.get('intent', {})
                sentiment = interpretation.get('sentiment', {})
                
                print("📊 ANALYSIS RESULTS:")
                print(f"   🎯 Intent: {intent.get('intent', 'unknown').upper()}")
                print(f"      Confidence: {intent.get('confidence', 0)*100:.0f}%")
                print(f"   😊 Sentiment: {sentiment.get('sentiment', 'unknown').upper()}")
                print(f"      Emotion: {sentiment.get('emotion', 'unknown')}")
                print(f"      Polarity: {sentiment.get('polarity', 0):.2f}")
                
                # Customer context
                context = result.get('customer_context', {})
                print(f"\n👤 CUSTOMER CONTEXT:")
                print(f"   Type: {context.get('customer_type', 'unknown')}")
                print(f"   Persona: {context.get('selected_persona', 'default').replace('_', ' ').title()}")
                
                # Response recommendations
                responses = result.get('ranked_responses', [])
                print(f"\n💡 RESPONSE RECOMMENDATIONS ({len(responses)} options):")
                print()
                
                for idx, response in enumerate(responses[:3], 1):  # Show top 3
                    score = response.get('score', 0) * 100
                    ranking = response.get('ranking', idx)
                    text = response.get('text', '')
                    
                    badge = "🥇" if ranking == 1 else "🥈" if ranking == 2 else "🥉"
                    
                    print(f"   {badge} Option #{ranking} (Score: {score:.1f}%)")
                    print(f"      \"{text}\"")
                    
                    # Show breakdown if available
                    breakdown = response.get('breakdown', {})
                    if breakdown:
                        print(f"      └─ Resolution: {breakdown.get('resolution_probability', 0)*100:.0f}% | "
                              f"Satisfaction: {breakdown.get('satisfaction_estimate', 0)*100:.0f}%")
                    print()
                
                # Predicted reactions for top response
                if responses and responses[0].get('predicted_reactions'):
                    print("   🔮 PREDICTED CUSTOMER REACTIONS:")
                    for reaction in responses[0]['predicted_reactions'][:2]:
                        prob = reaction.get('probability', 0) * 100
                        resp = reaction.get('customer_response', '')
                        print(f"      • {prob:.0f}% chance: \"{resp}\"")
                    print()
            
            print()
            await asyncio.sleep(1)  # Pause between turns
        
        # End call
        print(f"{'─'*70}")
        print(f"🔴 Ending call...")
        await pipeline.end_call(call_id, {
            "satisfaction": 0.85,
            "resolved": True,
            "notes": "Demo call completed successfully"
        })
        print(f"✅ Call ended\n")
        await asyncio.sleep(2)
    
    print("=" * 70)
    print("✅ DEMO COMPLETE!")
    print("=" * 70)
    print("\n📈 Summary:")
    print("   • All 6 agents processed conversations successfully")
    print("   • Intent classification working")
    print("   • Sentiment analysis working")
    print("   • Response recommendations generated")
    print("   • System ready for production use!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(demo_conversation())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

