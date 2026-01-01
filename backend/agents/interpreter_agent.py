"""
Interpreter Agent
Handles Intent, Sentiment, and Entity Extraction
"""

import logging
from typing import Dict, Any, List, Optional
import openai
from anthropic import Anthropic
import spacy
from textblob import TextBlob

from utils.config import settings

logger = logging.getLogger(__name__)


class InterpreterAgent:
    """Agent responsible for NLU: intent, sentiment, and entity extraction"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.nlp = None
        self.intent_categories = [
            "billing_inquiry",
            "technical_support",
            "product_information",
            "complaint",
            "refund_request",
            "account_management",
            "general_inquiry",
            "other"
        ]
        
    async def initialize(self):
        """Initialize NLP models and API clients"""
        try:
            # Initialize OpenAI client
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Initialize Anthropic client
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            # Load spaCy model for entity extraction
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            logger.info("Interpreter Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Interpreter Agent: {e}")
            raise
    
    async def extract_intent(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract customer intent from transcript
        
        Args:
            transcript: Customer speech transcript
            context: Previous conversation context
            
        Returns:
            Intent classification with confidence
        """
        try:
            if self.openai_client:
                # Use OpenAI for intent classification
                prompt = f"""Classify the customer's intent from the following transcript:
                
Transcript: "{transcript}"

Intent categories: {', '.join(self.intent_categories)}

Respond with JSON: {{"intent": "<category>", "confidence": <0-1>, "reasoning": "<brief explanation>"}}
"""
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are an expert at classifying customer service intents."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                return {
                    "intent": result.get("intent", "other"),
                    "confidence": result.get("confidence", 0.5),
                    "reasoning": result.get("reasoning", "")
                }
            else:
                # Fallback to rule-based classification
                return self._rule_based_intent(transcript)
                
        except Exception as e:
            logger.error(f"Intent extraction error: {e}")
            return {
                "intent": "other",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _rule_based_intent(self, transcript: str) -> Dict[str, Any]:
        """Fallback rule-based intent classification"""
        transcript_lower = transcript.lower()
        
        intent_keywords = {
            "billing_inquiry": ["bill", "billing", "charge", "charges", "payment", "invoice", "cost", "price", "statement", "frustrated with my billing"],
            "technical_support": ["not working", "broken", "error", "issue", "problem", "bug", "help with", "trouble", "can't"],
            "product_information": ["what is", "tell me about", "information", "details", "how does"],
            "complaint": ["complaint", "unhappy", "dissatisfied", "terrible", "awful", "frustrated", "angry"],
            "refund_request": ["refund", "money back", "return", "cancel", "want a refund", "get my money back"],
            "account_management": ["account", "password", "login", "profile", "settings", "reset password", "account login"]
        }
        
        scores = {}
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in transcript_lower)
            if score > 0:
                scores[intent] = score / len(keywords)
        
        if scores:
            best_intent = max(scores, key=scores.get)
            return {
                "intent": best_intent,
                "confidence": min(scores[best_intent], 0.9)
            }
        
        return {"intent": "other", "confidence": 0.5}
    
    async def extract_sentiment(
        self,
        transcript: str
    ) -> Dict[str, Any]:
        """
        Extract sentiment from transcript
        
        Args:
            transcript: Customer speech transcript
            
        Returns:
            Sentiment analysis with polarity and emotion
        """
        try:
            # Use TextBlob for sentiment
            blob = TextBlob(transcript)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            # Enhanced sentiment with OpenAI if available
            emotion = "neutral"
            if self.openai_client:
                try:
                    prompt = f"""Analyze the emotional tone of this customer statement:
"{transcript}"

Respond with JSON: {{"emotion": "<emotion>", "intensity": <0-1>}}
Emotions: angry, frustrated, satisfied, happy, neutral, anxious, confused
"""
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        response_format={"type": "json_object"}
                    )
                    import json
                    result = json.loads(response.choices[0].message.content)
                    emotion = result.get("emotion", "neutral")
                except Exception as e:
                    logger.warning(f"OpenAI emotion detection failed: {e}")
            
            return {
                "sentiment": sentiment_label,
                "polarity": float(polarity),
                "subjectivity": float(subjectivity),
                "emotion": emotion,
                "confidence": abs(polarity)  # Confidence based on polarity strength
            }
            
        except Exception as e:
            logger.error(f"Sentiment extraction error: {e}")
            return {
                "sentiment": "neutral",
                "polarity": 0.0,
                "subjectivity": 0.5,
                "emotion": "neutral",
                "confidence": 0.0
            }
    
    async def extract_entities(
        self,
        transcript: str
    ) -> List[Dict[str, Any]]:
        """
        Extract named entities from transcript
        
        Args:
            transcript: Customer speech transcript
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        try:
            # Use spaCy for entity extraction
            if self.nlp:
                doc = self.nlp(transcript)
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8  # spaCy doesn't provide confidence
                    })
            
            # Extract domain-specific entities (billing amounts, dates, etc.)
            import re
            
            # Extract monetary amounts
            money_pattern = r'\$[\d,]+\.?\d*'
            for match in re.finditer(money_pattern, transcript):
                entities.append({
                    "text": match.group(),
                    "label": "MONEY",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9
                })
            
            # Extract dates
            date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
            for match in re.finditer(date_pattern, transcript):
                entities.append({
                    "text": match.group(),
                    "label": "DATE",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8
                })
            
            # Extract account numbers (pattern: 6+ digits)
            account_pattern = r'\b\d{6,}\b'
            for match in re.finditer(account_pattern, transcript):
                entities.append({
                    "text": match.group(),
                    "label": "ACCOUNT_NUMBER",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.7
                })
            
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
        
        return entities
    
    async def interpret(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete interpretation: intent, sentiment, and entities
        
        Args:
            transcript: Customer speech transcript
            context: Previous conversation context
            
        Returns:
            Complete interpretation results
        """
        # Run all extractions in parallel
        import asyncio
        
        intent_task = self.extract_intent(transcript, context)
        sentiment_task = self.extract_sentiment(transcript)
        entities_task = self.extract_entities(transcript)
        
        intent, sentiment, entities = await asyncio.gather(
            intent_task,
            sentiment_task,
            entities_task
        )
        
        return {
            "transcript": transcript,
            "intent": intent,
            "sentiment": sentiment,
            "entities": entities,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        pass

