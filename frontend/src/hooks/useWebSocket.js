import { useState, useEffect, useRef } from 'react';

export function useWebSocket() {
  const [ws, setWs] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setWs(websocket);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      console.error('Error details:', error.message || error.type || 'Unknown error');
    };

    websocket.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      setWs(null);
      // Only attempt to reconnect if it wasn't a normal closure
      if (event.code !== 1000) {
        setTimeout(() => {
          if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
            console.log('Attempting to reconnect...');
            const newWs = new WebSocket(wsUrl);
            wsRef.current = newWs;
          }
        }, 3000);
      }
    };
    
    websocket.onmessage = (event) => {
      // Log all messages for debugging
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
      } catch (e) {
        console.log('WebSocket raw message:', event.data);
      }
    };

    wsRef.current = websocket;

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  return ws;
}

