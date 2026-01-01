"""
Planner Agent
Handles Dialogue Prediction with 1-2 Step Look-Ahead
"""

import logging
from typing import Dict, Any, List, Optional
import openai
from anthropic import Anthropic

from utils.config import settings

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent responsible for predictive dialogue planning"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
    async def initialize(self):
        """Initialize API clients"""
        try:
            if settings.OPENAI_API_KEY:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            logger.info("Planner Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Planner Agent: {e}")
            raise
    
    async def generate_response_options(
        self,
        customer_utterance: str,
        intent: str,
        sentiment: Dict[str, Any],
        persona: str,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple response options for the agent
        
        Args:
            customer_utterance: Customer's current statement
            intent: Detected intent
            sentiment: Sentiment analysis
            persona: Selected agent persona
            context: Conversation context
            
        Returns:
            List of response options with metadata
        """
        try:
            persona_descriptions = {
                "empathetic_authoritative": "Show empathy while being confident and solution-oriented",
                "efficient_solution_focused": "Be direct, efficient, and focus on solving the problem quickly",
                "friendly_casual": "Be warm, friendly, and conversational",
                "professional_formal": "Be professional, formal, and respectful",
                "patient_educational": "Be patient, explain things clearly, and guide the customer",
                "assertive_direct": "Be assertive, direct, and take charge of the situation",
                "supportive_encouraging": "Be supportive, encouraging, and positive",
                "analytical_detailed": "Be analytical, provide detailed information, and be thorough"
            }
            
            persona_desc = persona_descriptions.get(persona, "Be helpful and professional")
            
            prompt = f"""You are a customer service agent with the following persona: {persona_desc}

Customer said: "{customer_utterance}"
Customer intent: {intent}
Customer sentiment: {sentiment.get('sentiment', 'neutral')} ({sentiment.get('emotion', 'neutral')})

Generate 3-5 different response options for the agent. Each response should:
1. Address the customer's concern appropriately
2. Match the selected persona style
3. Be concise (1-2 sentences)
4. Move the conversation toward resolution

Respond with JSON array:
[
  {{
    "response_text": "<response>",
    "tone": "<tone description>",
    "approach": "<approach description>"
  }},
  ...
]
"""
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at generating customer service responses."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                options = result.get("options", result.get("responses", []))
            else:
                # Fallback to simple template-based responses
                options = self._generate_template_responses(intent, persona)
            
            # Add metadata to each option
            response_options = []
            for i, option in enumerate(options):
                if isinstance(option, dict):
                    response_options.append({
                        "id": f"response_{i}",
                        "text": option.get("response_text", option.get("text", "")),
                        "tone": option.get("tone", ""),
                        "approach": option.get("approach", ""),
                        "persona": persona
                    })
            
            return response_options
            
        except Exception as e:
            logger.error(f"Error generating response options: {e}")
            return []
    
    def _generate_template_responses(self, intent: str, persona: str) -> List[Dict[str, Any]]:
        """Fallback template-based response generation"""
        templates = {
            "billing_inquiry": [
                {"response_text": "I'd be happy to help you with your billing question. Let me pull up your account information.", "tone": "helpful", "approach": "proactive"},
                {"response_text": "I understand you have a billing question. Can you provide me with your account number?", "tone": "professional", "approach": "information_gathering"}
            ],
            "technical_support": [
                {"response_text": "I'm sorry you're experiencing this issue. Let me help you troubleshoot this step by step.", "tone": "empathetic", "approach": "problem_solving"},
                {"response_text": "I can help you resolve this technical issue. Can you describe what's happening?", "tone": "supportive", "approach": "diagnostic"}
            ],
            "complaint": [
                {"response_text": "I sincerely apologize for the inconvenience. Let me see what I can do to make this right.", "tone": "apologetic", "approach": "resolution_focused"},
                {"response_text": "I understand your frustration. I want to help resolve this for you today.", "tone": "empathetic", "approach": "acknowledgment"}
            ]
        }
        
        return templates.get(intent, [
            {"response_text": "I'm here to help. Can you tell me more about what you need?", "tone": "friendly", "approach": "information_gathering"}
        ])
    
    async def predict_customer_reactions(
        self,
        response_option: Dict[str, Any],
        customer_profile: Dict[str, Any],
        current_sentiment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Predict possible customer reactions to a response option (1-2 step look-ahead)
        
        Args:
            response_option: Proposed response option
            customer_profile: Customer profile data
            current_sentiment: Current sentiment state
            
        Returns:
            List of predicted reaction scenarios with probabilities
        """
        try:
            prompt = f"""Given this agent response, predict 2-3 possible customer reactions:

Agent Response: "{response_option.get('text', '')}"
Customer Type: {customer_profile.get('customer_type', 'unknown')}
Current Sentiment: {current_sentiment.get('sentiment', 'neutral')} ({current_sentiment.get('emotion', 'neutral')})

For each possible reaction, estimate:
1. The customer's likely response
2. The probability of that reaction (0-1)
3. The resulting sentiment (positive/neutral/negative)
4. The likelihood of resolution (0-1)

Respond with JSON:
{{
  "reactions": [
    {{
      "customer_response": "<predicted response>",
      "probability": <0-1>,
      "resulting_sentiment": "<positive/neutral/negative>",
      "resolution_likelihood": <0-1>,
      "next_step": "<what would happen next>"
    }},
    ...
  ]
}}
"""
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at predicting customer service conversation outcomes."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                reactions = result.get("reactions", [])
            else:
                # Fallback to simple probability estimates
                reactions = self._estimate_reactions_fallback(response_option, current_sentiment)
            
            return reactions
            
        except Exception as e:
            logger.error(f"Error predicting customer reactions: {e}")
            return []
    
    def _estimate_reactions_fallback(
        self,
        response_option: Dict[str, Any],
        current_sentiment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback reaction estimation"""
        sentiment_polarity = current_sentiment.get("polarity", 0.0)
        
        # Simple heuristics
        if sentiment_polarity < -0.3:
            # Negative sentiment - predict possible outcomes
            return [
                {
                    "customer_response": "That's helpful, thank you",
                    "probability": 0.4,
                    "resulting_sentiment": "neutral",
                    "resolution_likelihood": 0.6,
                    "next_step": "Customer accepts solution"
                },
                {
                    "customer_response": "I'm still not satisfied",
                    "probability": 0.5,
                    "resulting_sentiment": "negative",
                    "resolution_likelihood": 0.3,
                    "next_step": "Escalation needed"
                },
                {
                    "customer_response": "Okay, let's try that",
                    "probability": 0.1,
                    "resulting_sentiment": "positive",
                    "resolution_likelihood": 0.8,
                    "next_step": "Proceed with solution"
                }
            ]
        else:
            # Neutral or positive sentiment
            return [
                {
                    "customer_response": "That sounds good",
                    "probability": 0.7,
                    "resulting_sentiment": "positive",
                    "resolution_likelihood": 0.9,
                    "next_step": "Resolution in progress"
                },
                {
                    "customer_response": "I need to think about it",
                    "probability": 0.2,
                    "resulting_sentiment": "neutral",
                    "resolution_likelihood": 0.5,
                    "next_step": "Follow-up needed"
                },
                {
                    "customer_response": "Actually, I have another question",
                    "probability": 0.1,
                    "resulting_sentiment": "neutral",
                    "resolution_likelihood": 0.4,
                    "next_step": "Additional inquiry"
                }
            ]
    
    async def plan_dialogue(
        self,
        customer_utterance: str,
        intent: str,
        sentiment: Dict[str, Any],
        persona: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete dialogue planning: generate options and predict reactions
        
        Args:
            customer_utterance: Customer's current statement
            intent: Detected intent
            sentiment: Sentiment analysis
            persona: Selected persona
            context: Full conversation context
            
        Returns:
            Complete dialogue plan with options and predictions
        """
        import asyncio
        
        # Generate response options
        options = await self.generate_response_options(
            customer_utterance,
            intent,
            sentiment,
            persona,
            context
        )
        
        # Predict reactions for each option
        plans = []
        for option in options:
            reactions = await self.predict_customer_reactions(
                option,
                context.get("customer_profile", {}),
                sentiment
            )
            
            plans.append({
                "response_option": option,
                "predicted_reactions": reactions,
                "expected_sentiment_improvement": self._calculate_sentiment_improvement(reactions),
                "expected_resolution_probability": self._calculate_resolution_probability(reactions)
            })
        
        return {
            "options": plans,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _calculate_sentiment_improvement(self, reactions: List[Dict[str, Any]]) -> float:
        """Calculate expected sentiment improvement from reactions"""
        if not reactions:
            return 0.0
        
        improvement = 0.0
        for reaction in reactions:
            prob = reaction.get("probability", 0.0)
            sentiment = reaction.get("resulting_sentiment", "neutral")
            
            if sentiment == "positive":
                improvement += prob * 0.5
            elif sentiment == "negative":
                improvement -= prob * 0.3
            # neutral contributes 0
        
        return improvement
    
    def _calculate_resolution_probability(self, reactions: List[Dict[str, Any]]) -> float:
        """Calculate weighted average resolution probability"""
        if not reactions:
            return 0.5
        
        total_prob = 0.0
        total_weight = 0.0
        
        for reaction in reactions:
            prob = reaction.get("probability", 0.0)
            resolution = reaction.get("resolution_likelihood", 0.5)
            
            total_prob += prob * resolution
            total_weight += prob
        
        return total_prob / total_weight if total_weight > 0 else 0.5
    
    async def cleanup(self):
        """Cleanup resources"""
        pass

