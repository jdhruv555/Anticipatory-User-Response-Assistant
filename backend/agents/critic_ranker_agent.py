"""
Critic/Ranker Agent
Handles RL-Weighted Response Scoring
"""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
import torch
import torch.nn as nn

from utils.config import settings

logger = logging.getLogger(__name__)


class ValueNetwork(nn.Module):
    """Neural network for value function estimation"""
    
    def __init__(self, state_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Single value output
        )
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class CriticRankerAgent:
    """Agent responsible for RL-weighted response scoring"""
    
    def __init__(self):
        self.value_network = None
        self.state_dim = 128
        self.weights = {
            "resolution_probability": 0.4,
            "satisfaction_score": 0.3,
            "sentiment_improvement": 0.2,
            "efficiency": 0.1
        }
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    async def initialize(self):
        """Initialize value network"""
        try:
            self.value_network = ValueNetwork(
                state_dim=self.state_dim,
                hidden_dim=256
            ).to(self.device)
            
            # Try to load pre-trained weights if available
            try:
                import os
                model_path = "models/checkpoints/value_network.pth"
                if os.path.exists(model_path):
                    self.value_network.load_state_dict(torch.load(model_path, map_location=self.device))
                    logger.info("Loaded pre-trained value network")
            except Exception as e:
                logger.warning(f"Could not load pre-trained model: {e}")
            
            self.value_network.eval()
            logger.info("Critic/Ranker Agent initialized successfully")
        except Exception as e:
            logger.warning(f"Critic/Ranker Agent initialized with default weights: {e}")
            # Initialize with default weights if loading fails
            try:
                self.value_network = ValueNetwork(
                    state_dim=self.state_dim,
                    hidden_dim=256
                ).to(self.device)
                self.value_network.eval()
            except Exception:
                self.value_network = None
                logger.warning("Value network not available, using simplified scoring")
    
    def _encode_state(
        self,
        response_option: Dict[str, Any],
        dialogue_plan: Dict[str, Any],
        customer_context: Dict[str, Any],
        current_sentiment: Dict[str, Any]
    ) -> torch.Tensor:
        """
        Encode conversation state into feature vector
        
        Args:
            response_option: Response option to evaluate
            dialogue_plan: Dialogue planning results
            customer_context: Customer context
            current_sentiment: Current sentiment
            
        Returns:
            State embedding tensor
        """
        features = []
        
        # Response features
        response_text = response_option.get("text", "")
        features.append(len(response_text) / 500.0)  # Normalized length
        features.append(response_option.get("tone", "").count("positive") / 10.0)
        
        # Dialogue plan features
        reactions = dialogue_plan.get("predicted_reactions", [])
        if reactions:
            avg_resolution = np.mean([r.get("resolution_likelihood", 0.5) for r in reactions])
            avg_prob = np.mean([r.get("probability", 0.0) for r in reactions])
            sentiment_improvement = dialogue_plan.get("expected_sentiment_improvement", 0.0)
        else:
            avg_resolution = 0.5
            avg_prob = 0.0
            sentiment_improvement = 0.0
        
        features.append(avg_resolution)
        features.append(avg_prob)
        features.append(sentiment_improvement)
        
        # Customer context features
        customer_type = customer_context.get("customer_type", "unknown")
        customer_type_encoded = hash(customer_type) % 100 / 100.0
        features.append(customer_type_encoded)
        
        features.append(customer_context.get("satisfaction_avg", 0.5))
        features.append(customer_context.get("resolution_rate", 0.5))
        
        # Sentiment features
        features.append(current_sentiment.get("polarity", 0.0))
        features.append(current_sentiment.get("confidence", 0.5))
        
        # Intent features (one-hot encoding would be better, simplified here)
        intent = customer_context.get("intent", "other")
        intent_encoded = hash(intent) % 100 / 100.0
        features.append(intent_encoded)
        
        # Pad or truncate to state_dim
        while len(features) < self.state_dim:
            features.append(0.0)
        features = features[:self.state_dim]
        
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
    
    async def score_response(
        self,
        response_option: Dict[str, Any],
        dialogue_plan: Dict[str, Any],
        customer_context: Dict[str, Any],
        current_sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score a response option using RL-weighted value function
        
        Args:
            response_option: Response option to score
            dialogue_plan: Dialogue planning results for this option
            customer_context: Customer context
            current_sentiment: Current sentiment
            
        Returns:
            Score and breakdown
        """
        try:
            # Encode state
            state = self._encode_state(
                response_option,
                dialogue_plan,
                customer_context,
                current_sentiment
            )
            
            # Get value estimate from network
            with torch.no_grad():
                value_estimate = self.value_network(state).item()
            
            # Calculate component scores
            reactions = dialogue_plan.get("predicted_reactions", [])
            
            # Resolution probability score
            resolution_score = dialogue_plan.get("expected_resolution_probability", 0.5)
            
            # Satisfaction estimate (based on sentiment improvement)
            sentiment_improvement = dialogue_plan.get("expected_sentiment_improvement", 0.0)
            satisfaction_estimate = 0.5 + sentiment_improvement  # Map to 0-1 range
            
            # Efficiency score (based on response length and predicted steps)
            response_length = len(response_option.get("text", ""))
            efficiency_score = max(0.0, 1.0 - (response_length - 50) / 200.0)  # Prefer concise responses
            
            # Calculate weighted composite score
            composite_score = (
                self.weights["resolution_probability"] * resolution_score +
                self.weights["satisfaction_score"] * satisfaction_estimate +
                self.weights["sentiment_improvement"] * (sentiment_improvement + 0.5) +
                self.weights["efficiency"] * efficiency_score
            )
            
            # Combine with value network estimate (weighted average)
            final_score = 0.6 * composite_score + 0.4 * (value_estimate + 0.5)  # Normalize value estimate
            
            return {
                "response_id": response_option.get("id", ""),
                "score": float(final_score),
                "value_estimate": float(value_estimate),
                "composite_score": float(composite_score),
                "breakdown": {
                    "resolution_probability": float(resolution_score),
                    "satisfaction_estimate": float(satisfaction_estimate),
                    "sentiment_improvement": float(sentiment_improvement),
                    "efficiency": float(efficiency_score)
                },
                "ranking": 0  # Will be set after all responses are scored
            }
            
        except Exception as e:
            logger.error(f"Error scoring response: {e}")
            return {
                "response_id": response_option.get("id", ""),
                "score": 0.5,
                "error": str(e)
            }
    
    async def rank_responses(
        self,
        dialogue_plans: List[Dict[str, Any]],
        customer_context: Dict[str, Any],
        current_sentiment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Rank all response options by score
        
        Args:
            dialogue_plans: List of dialogue plans (one per response option)
            customer_context: Customer context
            current_sentiment: Current sentiment
            
        Returns:
            Ranked list of responses with scores
        """
        scored_responses = []
        
        for plan in dialogue_plans:
            response_option = plan.get("response_option", {})
            
            score_result = await self.score_response(
                response_option,
                plan,
                customer_context,
                current_sentiment
            )
            
            scored_responses.append({
                **response_option,
                **score_result,
                "predicted_reactions": plan.get("predicted_reactions", [])
            })
        
        # Sort by score (descending)
        scored_responses.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        # Add ranking
        for i, response in enumerate(scored_responses):
            response["ranking"] = i + 1
        
        return scored_responses
    
    def update_weights(self, new_weights: Dict[str, float]):
        """Update scoring weights (can be learned through RL)"""
        self.weights.update(new_weights)
        logger.info(f"Updated scoring weights: {self.weights}")
    
    async def save_model(self, path: str = "models/checkpoints/value_network.pth"):
        """Save value network model"""
        try:
            import os
            os.makedirs(os.path.dirname(path), exist_ok=True)
            torch.save(self.value_network.state_dict(), path)
            logger.info(f"Saved value network to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        pass

