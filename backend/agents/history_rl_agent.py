"""
History & RL Agent
Handles Customer Profile Retrieval and Persona Selection
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from models.database import get_db_session
from models.schemas import Customer, CallHistory, PersonaPerformance
from utils.config import settings

logger = logging.getLogger(__name__)


class HistoryRLAgent:
    """Agent responsible for customer history retrieval and persona selection"""
    
    # Initial persona types
    PERSONA_TYPES = [
        "empathetic_authoritative",
        "efficient_solution_focused",
        "friendly_casual",
        "professional_formal",
        "patient_educational",
        "assertive_direct",
        "supportive_encouraging",
        "analytical_detailed"
    ]
    
    def __init__(self):
        self.redis_client = None
        self.persona_performance_cache = {}
        
    async def initialize(self):
        """Initialize Redis client and load persona performance data"""
        try:
            self.redis_client = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                decode_responses=True
            )
            
            # Load persona performance data from database
            await self._load_persona_performance()
            
            logger.info("History & RL Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize History & RL Agent: {e}")
            raise
    
    async def _load_persona_performance(self):
        """Load persona performance metrics from database"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(PersonaPerformance)
                )
                performances = result.scalars().all()
                
                for perf in performances:
                    key = f"{perf.customer_type}:{perf.persona_type}"
                    self.persona_performance_cache[key] = {
                        "success_rate": perf.success_rate,
                        "satisfaction_avg": perf.satisfaction_avg,
                        "resolution_rate": perf.resolution_rate,
                        "call_count": perf.call_count
                    }
        except Exception as e:
            logger.warning(f"Could not load persona performance: {e}")
    
    async def get_customer_profile(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve customer profile and interaction history
        
        Args:
            customer_id: Unique customer identifier
            
        Returns:
            Customer profile with history and classification
        """
        try:
            # Try Redis cache first (if available)
            if self.redis_client:
                try:
                    cache_key = f"customer:{customer_id}"
                    cached = await self.redis_client.get(cache_key)
                    if cached:
                        import json
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Redis cache read failed: {e}")
            
            # Query database (with fallback if DB not available)
            try:
                async with get_db_session() as session:
                    result = await session.execute(
                        select(Customer).where(Customer.id == customer_id)
                    )
                    customer = result.scalar_one_or_none()
                    
                    if not customer:
                        # Create new customer profile
                        customer = Customer(
                            id=customer_id,
                            customer_type="new",
                            total_calls=0,
                            satisfaction_avg=0.0,
                            resolution_rate=0.0
                        )
                        session.add(customer)
                        await session.commit()
                    
                    # Get call history
                    history_result = await session.execute(
                        select(CallHistory)
                        .where(CallHistory.customer_id == customer_id)
                        .order_by(CallHistory.timestamp.desc())
                        .limit(10)
                    )
                    call_history = history_result.scalars().all()
                    
                    profile = {
                        "customer_id": customer.id,
                        "customer_type": customer.customer_type,
                        "total_calls": customer.total_calls,
                        "satisfaction_avg": customer.satisfaction_avg,
                        "resolution_rate": customer.resolution_rate,
                        "preferred_persona": customer.preferred_persona,
                        "recent_calls": [
                            {
                                "call_id": call.id,
                                "timestamp": call.timestamp.isoformat(),
                                "outcome": call.outcome,
                                "satisfaction": call.satisfaction_score
                            }
                            for call in call_history
                        ]
                    }
                    
                    # Cache for 1 hour (if Redis available)
                    if self.redis_client:
                        try:
                            await self.redis_client.setex(
                                cache_key,
                                3600,
                                json.dumps(profile)
                            )
                        except Exception as e:
                            logger.warning(f"Redis cache write failed: {e}")
                    
                    return profile
            except Exception as e:
                logger.warning(f"Database query failed, using default profile: {e}")
                # Return default profile if DB not available
                profile = {
                    "customer_id": customer_id,
                    "customer_type": "new",
                    "total_calls": 0,
                    "satisfaction_avg": 0.0,
                    "resolution_rate": 0.0,
                    "recent_calls": []
                }
                return profile
                
        except Exception as e:
            logger.error(f"Error retrieving customer profile: {e}")
            return {
                "customer_id": customer_id,
                "customer_type": "unknown",
                "total_calls": 0,
                "satisfaction_avg": 0.0,
                "resolution_rate": 0.0,
                "recent_calls": []
            }
    
    async def classify_customer_type(
        self,
        customer_profile: Dict[str, Any],
        current_intent: str,
        current_sentiment: Dict[str, Any]
    ) -> str:
        """
        Classify customer type based on profile and current interaction
        
        Args:
            customer_profile: Customer profile data
            current_intent: Current conversation intent
            current_sentiment: Current sentiment analysis
            
        Returns:
            Customer type classification
        """
        # Simple classification logic
        # In production, use ML model for classification
        
        total_calls = customer_profile.get("total_calls", 0)
        satisfaction = customer_profile.get("satisfaction_avg", 0.0)
        sentiment_polarity = current_sentiment.get("polarity", 0.0)
        
        if total_calls == 0:
            return "new"
        elif total_calls > 10 and satisfaction > 0.7:
            return "loyal_positive"
        elif sentiment_polarity < -0.3:
            return "frustrated"
        elif current_intent == "complaint":
            return "complainer"
        elif total_calls > 5:
            return "repeat"
        else:
            return "regular"
    
    async def select_optimal_persona(
        self,
        customer_type: str,
        intent: str,
        sentiment: Dict[str, Any]
    ) -> str:
        """
        Select optimal agent persona based on customer type and context
        
        Args:
            customer_type: Classified customer type
            intent: Current intent
            sentiment: Sentiment analysis
            
        Returns:
            Selected persona type
        """
        # Check persona performance cache
        best_persona = None
        best_score = 0.0
        
        for persona in self.PERSONA_TYPES:
            key = f"{customer_type}:{persona}"
            performance = self.persona_performance_cache.get(key, {
                "success_rate": 0.5,
                "satisfaction_avg": 0.5,
                "resolution_rate": 0.5,
                "call_count": 0
            })
            
            # Calculate composite score
            # Weight: success_rate (40%), satisfaction (30%), resolution (30%)
            score = (
                performance["success_rate"] * 0.4 +
                performance["satisfaction_avg"] * 0.3 +
                performance["resolution_rate"] * 0.3
            )
            
            # Boost score if persona has been used successfully before
            if performance["call_count"] > 0:
                score *= 1.1
            
            if score > best_score:
                best_score = score
                best_persona = persona
        
        # Fallback logic based on sentiment and intent
        if not best_persona or best_score < 0.3:
            sentiment_polarity = sentiment.get("polarity", 0.0)
            emotion = sentiment.get("emotion", "neutral")
            
            if sentiment_polarity < -0.3 or emotion in ["angry", "frustrated"]:
                best_persona = "empathetic_authoritative"
            elif intent == "technical_support":
                best_persona = "patient_educational"
            elif intent == "billing_inquiry":
                best_persona = "efficient_solution_focused"
            else:
                best_persona = "friendly_casual"
        
        return best_persona or "friendly_casual"
    
    async def get_customer_context(
        self,
        customer_id: str,
        current_intent: str,
        current_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get complete customer context for decision making
        
        Args:
            customer_id: Customer identifier
            current_intent: Current conversation intent
            current_sentiment: Current sentiment
            
        Returns:
            Complete context including profile and persona
        """
        # Get customer profile
        profile = await self.get_customer_profile(customer_id)
        
        # Classify customer type
        customer_type = await self.classify_customer_type(
            profile,
            current_intent,
            current_sentiment
        )
        
        # Select optimal persona
        persona = await self.select_optimal_persona(
            customer_type,
            current_intent,
            current_sentiment
        )
        
        return {
            "customer_profile": profile,
            "customer_type": customer_type,
            "selected_persona": persona,
            "context_timestamp": asyncio.get_event_loop().time()
        }
    
    async def update_persona_performance(
        self,
        customer_type: str,
        persona_type: str,
        outcome: Dict[str, Any]
    ):
        """
        Update persona performance metrics after call
        
        Args:
            customer_type: Customer type classification
            persona_type: Persona used in call
            outcome: Call outcome data
        """
        try:
            key = f"{customer_type}:{persona_type}"
            
            # Update cache
            if key not in self.persona_performance_cache:
                self.persona_performance_cache[key] = {
                    "success_rate": 0.5,
                    "satisfaction_avg": 0.5,
                    "resolution_rate": 0.5,
                    "call_count": 0
                }
            
            perf = self.persona_performance_cache[key]
            call_count = perf["call_count"]
            
            # Update metrics with exponential moving average
            alpha = 0.1  # Learning rate
            
            if "satisfaction" in outcome:
                perf["satisfaction_avg"] = (
                    alpha * outcome["satisfaction"] +
                    (1 - alpha) * perf["satisfaction_avg"]
                )
            
            if "resolved" in outcome:
                perf["resolution_rate"] = (
                    alpha * (1.0 if outcome["resolved"] else 0.0) +
                    (1 - alpha) * perf["resolution_rate"]
                )
            
            # Success rate is combination of satisfaction and resolution
            perf["success_rate"] = (
                perf["satisfaction_avg"] * 0.6 +
                perf["resolution_rate"] * 0.4
            )
            
            perf["call_count"] = call_count + 1
            
            # Update database (async)
            asyncio.create_task(self._persist_persona_performance(
                customer_type,
                persona_type,
                perf
            ))
            
        except Exception as e:
            logger.error(f"Error updating persona performance: {e}")
    
    async def _persist_persona_performance(
        self,
        customer_type: str,
        persona_type: str,
        performance: Dict[str, Any]
    ):
        """Persist persona performance to database"""
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(PersonaPerformance).where(
                        PersonaPerformance.customer_type == customer_type,
                        PersonaPerformance.persona_type == persona_type
                    )
                )
                perf = result.scalar_one_or_none()
                
                if perf:
                    perf.success_rate = performance["success_rate"]
                    perf.satisfaction_avg = performance["satisfaction_avg"]
                    perf.resolution_rate = performance["resolution_rate"]
                    perf.call_count = performance["call_count"]
                else:
                    perf = PersonaPerformance(
                        customer_type=customer_type,
                        persona_type=persona_type,
                        success_rate=performance["success_rate"],
                        satisfaction_avg=performance["satisfaction_avg"],
                        resolution_rate=performance["resolution_rate"],
                        call_count=performance["call_count"]
                    )
                    session.add(perf)
                
                await session.commit()
        except Exception as e:
            logger.error(f"Error persisting persona performance: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()

