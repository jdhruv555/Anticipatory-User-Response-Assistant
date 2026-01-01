"""
Conversation Pipeline
Orchestrates all agents to process conversations in real-time
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from agents.listener_agent import ListenerAgent
from agents.interpreter_agent import InterpreterAgent
from agents.history_rl_agent import HistoryRLAgent
from agents.planner_agent import PlannerAgent
from agents.critic_ranker_agent import CriticRankerAgent
from sqlalchemy import select
from models.database import get_db_session
from models.schemas import CallHistory, Customer
from utils.config import settings

logger = logging.getLogger(__name__)


class ConversationPipeline:
    """Main pipeline orchestrating all agents"""
    
    def __init__(self):
        self.listener = ListenerAgent()
        self.interpreter = InterpreterAgent()
        self.history_rl = HistoryRLAgent()
        self.planner = PlannerAgent()
        self.critic_ranker = CriticRankerAgent()
        
        self.active_calls = {}  # call_id -> call_state
        
    async def initialize(self):
        """Initialize all agents"""
        logger.info("Initializing conversation pipeline...")
        
        await asyncio.gather(
            self.listener.initialize(),
            self.interpreter.initialize(),
            self.history_rl.initialize(),
            self.planner.initialize(),
            self.critic_ranker.initialize()
        )
        
        logger.info("Conversation pipeline initialized")
    
    async def start_call(self, call_id: str, customer_id: str):
        """Initialize a new call"""
        call_state = {
            "call_id": call_id,
            "customer_id": customer_id,
            "start_time": datetime.utcnow(),
            "transcripts": [],
            "interpretations": [],
            "responses": [],
            "current_intent": None,
            "current_sentiment": None,
            "selected_persona": None,
            "customer_context": None
        }
        
        self.active_calls[call_id] = call_state
        logger.info(f"Started call {call_id} for customer {customer_id}")
    
    async def process_audio_chunk(
        self,
        call_id: str,
        audio_data: bytes,
        speaker: str = "customer"
    ) -> Dict[str, Any]:
        """
        Process audio chunk through the full pipeline
        
        Args:
            call_id: Call identifier
            audio_data: Raw audio bytes
            speaker: "customer" or "agent"
            
        Returns:
            Complete analysis with response recommendations
        """
        if call_id not in self.active_calls:
            logger.warning(f"Call {call_id} not found, creating new call")
            await self.start_call(call_id, f"customer_{uuid.uuid4().hex[:8]}")
        
        call_state = self.active_calls[call_id]
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Listener Agent - Transcribe audio
            # If audio_data is text (from base64 decoded message), use it directly
            if isinstance(audio_data, bytes):
                try:
                    # Try to decode as text first
                    text_check = audio_data.decode('utf-8')
                    if text_check and not text_check.startswith('[Mock:'):
                        transcript = text_check
                    else:
                        transcription = await self.listener.transcribe_audio_chunk(audio_data)
                        transcript = transcription.get("transcript", "")
                except:
                    transcription = await self.listener.transcribe_audio_chunk(audio_data)
                    transcript = transcription.get("transcript", "")
            else:
                transcript = str(audio_data)
            
            if not transcript or speaker != "customer":
                return {
                    "call_id": call_id,
                    "status": "processing",
                    "transcript": transcript
                }
            
            call_state["transcripts"].append({
                "text": transcript,
                "timestamp": datetime.utcnow().isoformat(),
                "speaker": speaker
            })
            
            # Step 2: Interpreter Agent - Extract intent, sentiment, entities
            interpretation = await self.interpreter.interpret(
                transcript,
                context=call_state.get("customer_context")
            )
            
            call_state["interpretations"].append(interpretation)
            call_state["current_intent"] = interpretation.get("intent", {}).get("intent")
            call_state["current_sentiment"] = interpretation.get("sentiment")
            
            # Step 3: History & RL Agent - Get customer context and select persona
            customer_context = await self.history_rl.get_customer_context(
                call_state["customer_id"],
                call_state["current_intent"],
                call_state["current_sentiment"]
            )
            
            call_state["customer_context"] = customer_context
            call_state["selected_persona"] = customer_context.get("selected_persona")
            
            # Step 4: Planner Agent - Generate response options and predict reactions
            dialogue_plan = await self.planner.plan_dialogue(
                customer_utterance=transcript,
                intent=call_state["current_intent"],
                sentiment=call_state["current_sentiment"],
                persona=call_state["selected_persona"],
                context=customer_context
            )
            
            # Step 5: Critic/Ranker Agent - Score and rank responses
            ranked_responses = await self.critic_ranker.rank_responses(
                dialogue_plans=dialogue_plan.get("options", []),
                customer_context=customer_context.get("customer_profile", {}),
                current_sentiment=call_state["current_sentiment"]
            )
            
            call_state["responses"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "ranked_responses": ranked_responses
            })
            
            # Calculate latency
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # Prepare response for dashboard
            result = {
                "call_id": call_id,
                "status": "complete",
                "latency_ms": latency_ms,
                "transcript": transcript,
                "interpretation": {
                    "intent": interpretation.get("intent"),
                    "sentiment": interpretation.get("sentiment"),
                    "entities": interpretation.get("entities", [])
                },
                "customer_context": {
                    "customer_type": customer_context.get("customer_type"),
                    "selected_persona": customer_context.get("selected_persona")
                },
                "ranked_responses": ranked_responses[:5],  # Top 5 responses
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if latency_ms > settings.MAX_LATENCY_MS:
                logger.warning(f"Latency {latency_ms}ms exceeds target {settings.MAX_LATENCY_MS}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing audio chunk for call {call_id}: {e}")
            return {
                "call_id": call_id,
                "status": "error",
                "error": str(e)
            }
    
    async def record_response_selection(self, call_id: str, response_id: str):
        """Record which response the agent selected"""
        if call_id in self.active_calls:
            call_state = self.active_calls[call_id]
            call_state["selected_response_id"] = response_id
            logger.info(f"Recorded response selection: {response_id} for call {call_id}")
    
    async def end_call(self, call_id: str, outcome: Dict[str, Any]):
        """End call and trigger RL feedback loop"""
        if call_id not in self.active_calls:
            logger.warning(f"Call {call_id} not found")
            return
        
        call_state = self.active_calls[call_id]
        customer_id = call_state["customer_id"]
        persona = call_state.get("selected_persona")
        customer_type = call_state.get("customer_context", {}).get("customer_type")
        
        try:
            # Save call history
            async with get_db_session() as session:
                duration = (datetime.utcnow() - call_state["start_time"]).total_seconds()
                
                call_history = CallHistory(
                    id=call_id,
                    customer_id=customer_id,
                    persona_used=persona,
                    intent=call_state.get("current_intent"),
                    satisfaction_score=outcome.get("satisfaction"),
                    resolved=outcome.get("resolved", False),
                    outcome=outcome,
                    duration_seconds=int(duration)
                )
                session.add(call_history)
                
                # Update customer metrics
                result = await session.execute(
                    select(Customer).where(Customer.id == customer_id)
                )
                customer = result.scalar_one_or_none()
                
                if customer:
                    customer.total_calls += 1
                    if outcome.get("satisfaction") is not None:
                        # Update satisfaction average
                        current_avg = customer.satisfaction_avg
                        total_calls = customer.total_calls
                        new_satisfaction = outcome.get("satisfaction")
                        customer.satisfaction_avg = (
                            (current_avg * (total_calls - 1) + new_satisfaction) / total_calls
                        )
                    
                    if outcome.get("resolved"):
                        # Update resolution rate
                        current_rate = customer.resolution_rate
                        total_calls = customer.total_calls
                        customer.resolution_rate = (
                            (current_rate * (total_calls - 1) + 1.0) / total_calls
                        )
                
                await session.commit()
            
            # Update persona performance
            if customer_type and persona:
                await self.history_rl.update_persona_performance(
                    customer_type,
                    persona,
                    outcome
                )
            
            # Remove from active calls
            del self.active_calls[call_id]
            
            logger.info(f"Ended call {call_id} with outcome: {outcome}")
            
        except Exception as e:
            logger.error(f"Error ending call {call_id}: {e}")
    
    async def cleanup(self):
        """Cleanup all agents"""
        await asyncio.gather(
            self.listener.cleanup(),
            self.interpreter.cleanup(),
            self.history_rl.cleanup(),
            self.planner.cleanup(),
            self.critic_ranker.cleanup(),
            return_exceptions=True
        )

