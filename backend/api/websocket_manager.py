"""WebSocket connection manager"""

from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Map of call_id -> list of WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map of WebSocket -> call_id
        self.connection_to_call: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, call_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        
        if call_id:
            if call_id not in self.active_connections:
                self.active_connections[call_id] = []
            self.active_connections[call_id].append(websocket)
            self.connection_to_call[websocket] = call_id
            logger.info(f"WebSocket connected for call {call_id}")
        else:
            # Connection without specific call_id (general dashboard)
            if "general" not in self.active_connections:
                self.active_connections["general"] = []
            self.active_connections["general"].append(websocket)
            logger.info("WebSocket connected (general)")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        call_id = self.connection_to_call.get(websocket)
        
        if call_id and call_id in self.active_connections:
            self.active_connections[call_id].remove(websocket)
            if not self.active_connections[call_id]:
                del self.active_connections[call_id]
        
        # Also check general connections
        if "general" in self.active_connections:
            if websocket in self.active_connections["general"]:
                self.active_connections["general"].remove(websocket)
        
        if websocket in self.connection_to_call:
            del self.connection_to_call[websocket]
        
        logger.info(f"WebSocket disconnected for call {call_id if call_id else 'general'}")
    
    async def broadcast_to_call(self, call_id: str, message: dict):
        """Broadcast message to all connections for a specific call"""
        if call_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[call_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connections"""
        all_connections = []
        for connections in self.active_connections.values():
            all_connections.extend(connections)
        
        disconnected = []
        for connection in set(all_connections):  # Remove duplicates
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

