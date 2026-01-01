"""
AURA Main Application
FastAPI backend with WebSocket support for real-time agent assistance
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from api.routes import router
from api.websocket_manager import ConnectionManager
from services.pipeline import ConversationPipeline
from utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection manager
manager = ConnectionManager()

# Global pipeline instance
pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global pipeline
    
    # Startup
    logger.info("Initializing AURA system...")
    pipeline = ConversationPipeline()
    await pipeline.initialize()
    logger.info("AURA system initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AURA system...")
    await pipeline.cleanup()
    logger.info("AURA system shut down")


app = FastAPI(
    title="AURA API",
    description="Anticipatory User Response Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time conversation updates"""
    call_id = None
    await manager.connect(websocket, call_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "audio_chunk":
                # Process audio chunk through pipeline
                call_id = data.get("call_id")
                audio_data = data.get("audio_data")
                speaker = data.get("speaker", "customer")
                
                # Decode base64 audio data if it's a text message
                import base64
                try:
                    # Try to decode as base64, if it fails, treat as raw bytes
                    if isinstance(audio_data, str):
                        decoded_audio = base64.b64decode(audio_data)
                        # If it decodes to text, use it as transcript directly
                        try:
                            text_transcript = decoded_audio.decode('utf-8')
                            # Use text directly instead of audio processing
                            audio_data = text_transcript.encode('utf-8')
                        except:
                            # If decode fails, try hex
                            try:
                                text_transcript = bytes.fromhex(audio_data).decode('utf-8')
                                audio_data = text_transcript.encode('utf-8')
                            except:
                                pass
                except:
                    # If it's already bytes or hex string, try hex decode
                    if isinstance(audio_data, str) and len(audio_data) > 0:
                        try:
                            text_transcript = bytes.fromhex(audio_data).decode('utf-8')
                            audio_data = text_transcript.encode('utf-8')
                        except:
                            pass
                
                if pipeline:
                    result = await pipeline.process_audio_chunk(
                        call_id=call_id,
                        audio_data=audio_data,
                        speaker=speaker
                    )
                    # Add type for frontend
                    result["type"] = "call_update"
                    # Send updates to call-specific connections
                    await manager.broadcast_to_call(call_id, result)
                    # Also send to general dashboard connections
                    await manager.broadcast_to_all(result)
                    # Also send response back to sender
                    await websocket.send_json(result)
            
            elif message_type == "call_start":
                call_id = data.get("call_id")
                customer_id = data.get("customer_id")
                # Store call_id for this connection
                manager.connection_to_call[websocket] = call_id
                if call_id not in manager.active_connections:
                    manager.active_connections[call_id] = []
                if websocket not in manager.active_connections[call_id]:
                    manager.active_connections[call_id].append(websocket)
                
                await pipeline.start_call(call_id, customer_id)
                response = {"type": "call_started", "call_id": call_id}
                await manager.broadcast_to_call(call_id, response)
                await manager.broadcast_to_all(response)
            
            elif message_type == "call_end":
                call_id = data.get("call_id")
                outcome = data.get("outcome", {})
                await pipeline.end_call(call_id, outcome)
                await manager.broadcast_to_call(
                    call_id,
                    {"type": "call_ended", "call_id": call_id}
                )
            
            elif message_type == "agent_response_selected":
                call_id = data.get("call_id")
                response_id = data.get("response_id")
                await pipeline.record_response_selection(call_id, response_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AURA API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "pipeline_initialized": pipeline is not None,
        "active_connections": len(manager.active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

