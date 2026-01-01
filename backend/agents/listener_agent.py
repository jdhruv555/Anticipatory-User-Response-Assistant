"""
Listener Agent
Handles Automatic Speech Recognition (ASR) and Turn Detection
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from google.cloud import speech_v1
from google.cloud.speech_v1 import types
import io

from utils.config import settings

logger = logging.getLogger(__name__)


class ListenerAgent:
    """Agent responsible for ASR and voice activity detection"""
    
    def __init__(self):
        self.client = None
        self.config = None
        self.streaming_config = None
        self.silence_threshold_ms = settings.VAD_SILENCE_THRESHOLD_MS
        self.last_speech_time = None
        self.current_transcript = ""
        
    async def initialize(self):
        """Initialize Google Speech-to-Text client"""
        self.client = None
        self.config = None
        self.streaming_config = None
        
        try:
            if settings.GOOGLE_APPLICATION_CREDENTIALS and settings.GOOGLE_APPLICATION_CREDENTIALS != "":
                try:
                    self.client = speech_v1.SpeechAsyncClient.from_service_account_file(
                        settings.GOOGLE_APPLICATION_CREDENTIALS
                    )
                except Exception as e:
                    logger.warning(f"Failed to load Google credentials from file: {e}")
                    self.client = None
            else:
                # Try default credentials, but don't fail if not available
                try:
                    self.client = speech_v1.SpeechAsyncClient()
                except Exception as e:
                    logger.warning(f"Google Speech-to-Text not available (no credentials): {e}")
                    self.client = None
            
            if self.client:
                # Configure for real-time streaming
                self.config = types.RecognitionConfig(
                    encoding=types.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code="en-US",
                    enable_automatic_punctuation=True,
                    enable_word_time_offsets=True,
                    model="latest_long",
                )
                
                self.streaming_config = types.StreamingRecognitionConfig(
                    config=self.config,
                    interim_results=True,
                    single_utterance=False,
                )
                logger.info("Listener Agent initialized with Google Speech-to-Text")
            else:
                logger.info("Listener Agent initialized with mock transcription (Google Speech-to-Text not configured)")
            
        except Exception as e:
            logger.warning(f"Listener Agent initialized with limited functionality: {e}")
            self.client = None
    
    async def transcribe_audio_chunk(
        self,
        audio_data: bytes,
        is_final: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio chunk using Google Speech-to-Text
        
        Args:
            audio_data: Raw audio bytes
            is_final: Whether this is the final chunk in an utterance
            
        Returns:
            Dictionary with transcription and metadata
        """
        # If client not available, try to extract text from audio_data
        if not self.client:
            # If audio_data looks like text, use it directly
            if isinstance(audio_data, bytes):
                try:
                    text = audio_data.decode('utf-8')
                    if text and len(text) > 0:
                        return {
                            "transcript": text,
                            "confidence": 0.9,
                            "is_final": is_final,
                            "timestamp": asyncio.get_event_loop().time()
                        }
                except:
                    pass
            
            # Otherwise return mock
            return {
                "transcript": "[Mock: Audio received, transcription service not configured]",
                "confidence": 0.8,
                "is_final": is_final,
                "timestamp": asyncio.get_event_loop().time()
            }
        
        try:
            # Create streaming request
            request = types.StreamingRecognizeRequest(
                streaming_config=self.streaming_config if not is_final else None,
                audio_content=audio_data
            )
            
            # For simplicity, using synchronous client in async context
            # In production, use async client properly
            response = await asyncio.to_thread(
                self._process_streaming_request,
                request
            )
            
            transcript = ""
            confidence = 0.0
            is_final_result = False
            
            if response and response.results:
                for result in response.results:
                    if result.alternatives:
                        alternative = result.alternatives[0]
                        transcript = alternative.transcript
                        confidence = alternative.confidence
                        is_final_result = result.is_final_alternative
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "is_final": is_final_result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "transcript": f"[Error: {str(e)}]",
                "confidence": 0.0,
                "is_final": False,
                "error": str(e)
            }
    
    def _process_streaming_request(self, request):
        """Process streaming request (synchronous helper)"""
        # This is a simplified version
        # In production, maintain persistent streaming connections
        responses = self.client.streaming_recognize([request])
        for response in responses:
            return response
        return None
    
    def detect_turn_boundary(
        self,
        audio_data: bytes,
        current_time: float
    ) -> bool:
        """
        Detect if a turn boundary has been reached using silence detection
        
        Args:
            audio_data: Audio chunk to analyze
            current_time: Current timestamp
            
        Returns:
            True if turn boundary detected
        """
        # Simple energy-based VAD
        # In production, use more sophisticated VAD algorithms
        import numpy as np
        
        if len(audio_data) < 2:
            return False
        
        # Convert bytes to numpy array (assuming 16-bit PCM)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        energy = np.mean(np.abs(audio_array))
        
        # Threshold for silence (adjust based on calibration)
        silence_threshold = 500  # Adjust based on audio levels
        
        if energy < silence_threshold:
            if self.last_speech_time is None:
                self.last_speech_time = current_time
            else:
                silence_duration = (current_time - self.last_speech_time) * 1000  # ms
                if silence_duration >= self.silence_threshold_ms:
                    self.last_speech_time = None
                    return True
        else:
            self.last_speech_time = None
        
        return False
    
    async def process_audio_stream(
        self,
        audio_stream,
        call_id: str
    ) -> Dict[str, Any]:
        """
        Process continuous audio stream
        
        Args:
            audio_stream: Async generator of audio chunks
            call_id: Unique call identifier
            
        Returns:
            Transcription results with turn detection
        """
        results = []
        current_utterance = []
        turn_detected = False
        
        async for chunk in audio_stream:
            # Detect turn boundary
            current_time = asyncio.get_event_loop().time()
            if self.detect_turn_boundary(chunk, current_time):
                turn_detected = True
                # Process accumulated utterance
                if current_utterance:
                    audio_bytes = b''.join(current_utterance)
                    result = await self.transcribe_audio_chunk(audio_bytes, is_final=True)
                    results.append(result)
                    current_utterance = []
            else:
                current_utterance.append(chunk)
                # Get interim results
                result = await self.transcribe_audio_chunk(chunk, is_final=False)
                if result.get("transcript"):
                    results.append(result)
        
        return {
            "call_id": call_id,
            "results": results,
            "turn_detected": turn_detected
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            # Close any open streams
            pass

