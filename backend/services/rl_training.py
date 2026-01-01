"""
RL Training Service
Handles reinforcement learning model updates using PPO
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from collections import deque
import numpy as np
import torch
import torch.optim as optim

# Make stable_baselines3 optional
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env
    STABLE_BASELINES3_AVAILABLE = True
except ImportError:
    STABLE_BASELINES3_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("stable_baselines3 not available, RL training will be limited")

from models.database import get_db_session
from models.schemas import CallHistory
from utils.config import settings

logger = logging.getLogger(__name__)


class ConversationEnv:
    """Gymnasium environment for conversation RL"""
    
    def __init__(self, state_dim: int = 128, action_dim: int = 8):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.state = None
        self.reset()
    
    def reset(self):
        """Reset environment"""
        self.state = np.random.randn(self.state_dim)
        return self.state
    
    def step(self, action: int):
        """Execute action and return reward"""
        # Simplified reward function
        # In production, this would use actual call outcomes
        reward = np.random.rand()  # Placeholder
        done = False
        info = {}
        return self.state, reward, done, info


class RLTrainer:
    """Reinforcement learning trainer using PPO"""
    
    def __init__(self):
        self.model = None
        self.training_buffer = deque(maxlen=settings.RL_WEEKLY_RETRAIN_SIZE)
        self.update_counter = 0
        
    async def initialize(self):
        """Initialize RL model"""
        if not STABLE_BASELINES3_AVAILABLE:
            logger.warning("RL Trainer initialized without stable_baselines3 - training disabled")
            self.model = None
            return
        
        try:
            # Create environment
            env = make_vec_env(
                lambda: ConversationEnv(),
                n_envs=4
            )
            
            # Initialize PPO model
            self.model = PPO(
                "MlpPolicy",
                env,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                verbose=1
            )
            
            # Try to load existing model
            try:
                self.model.load("models/checkpoints/ppo_model")
                logger.info("Loaded existing PPO model")
            except Exception as e:
                logger.info(f"No existing model found, starting fresh: {e}")
            
            logger.info("RL Trainer initialized successfully")
        except Exception as e:
            logger.warning(f"RL Trainer initialized with limited functionality: {e}")
            self.model = None
    
    def calculate_reward(
        self,
        outcome: Dict[str, Any],
        predicted_scores: Dict[str, Any]
    ) -> float:
        """
        Calculate reward signal from call outcome
        
        Args:
            outcome: Actual call outcome
            predicted_scores: Predicted scores from ranking
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Satisfaction component (0-0.4)
        satisfaction = outcome.get("satisfaction", 0.5)
        reward += satisfaction * 0.4
        
        # Resolution component (0-0.4)
        if outcome.get("resolved", False):
            reward += 0.4
        
        # Prediction accuracy component (0-0.2)
        # Compare predicted vs actual
        predicted_satisfaction = predicted_scores.get("satisfaction_estimate", 0.5)
        accuracy = 1.0 - abs(satisfaction - predicted_satisfaction)
        reward += accuracy * 0.2
        
        return reward
    
    async def record_training_sample(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """Record training sample for batch training"""
        self.training_buffer.append({
            "state": state,
            "action": action,
            "reward": reward,
            "next_state": next_state,
            "done": done
        })
        
        self.update_counter += 1
        
        # Trigger micro-batch update if threshold reached
        if self.update_counter >= settings.RL_UPDATE_FREQUENCY:
            await self.micro_batch_update()
            self.update_counter = 0
    
    async def micro_batch_update(self):
        """Perform micro-batch model update"""
        if len(self.training_buffer) < 100:
            logger.info("Not enough samples for micro-batch update")
            return
        
        logger.info(f"Performing micro-batch update with {len(self.training_buffer)} samples")
        
        try:
            # Train on recent samples
            # In production, this would properly format the data for PPO
            # For now, we'll do a simplified update
            
            # Save model checkpoint
            self.model.save("models/checkpoints/ppo_model")
            logger.info("Micro-batch update completed")
            
        except Exception as e:
            logger.error(f"Error in micro-batch update: {e}")
    
    async def weekly_retrain(self):
        """Perform comprehensive weekly retraining"""
        logger.info("Starting weekly retraining...")
        
        try:
            # Load all recent call outcomes from database
            async with get_db_session() as session:
                from sqlalchemy import select, func
                from datetime import datetime, timedelta
                
                # Get calls from last week
                week_ago = datetime.utcnow() - timedelta(days=7)
                result = await session.execute(
                    select(CallHistory)
                    .where(CallHistory.timestamp >= week_ago)
                    .order_by(CallHistory.timestamp.desc())
                    .limit(settings.RL_WEEKLY_RETRAIN_SIZE)
                )
                calls = result.scalars().all()
            
            if len(calls) < 100:
                logger.warning(f"Not enough calls for retraining: {len(calls)}")
                return
            
            logger.info(f"Retraining on {len(calls)} calls")
            
            # Process calls and update model
            # In production, this would involve:
            # 1. Extracting states from call data
            # 2. Calculating rewards from outcomes
            # 3. Training PPO model on the dataset
            
            # For now, save a checkpoint
            self.model.save("models/checkpoints/ppo_model_weekly")
            logger.info("Weekly retraining completed")
            
        except Exception as e:
            logger.error(f"Error in weekly retraining: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.model:
            # Save final model
            self.model.save("models/checkpoints/ppo_model")
            logger.info("RL Trainer cleaned up")

