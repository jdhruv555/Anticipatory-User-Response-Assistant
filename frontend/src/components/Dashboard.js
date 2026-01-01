import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import CallCard from './CallCard';
import MetricsPanel from './MetricsPanel';

function Dashboard() {
  const [activeCalls, setActiveCalls] = useState([]);
  const [metrics, setMetrics] = useState({
    activeCalls: 0,
    avgLatency: 0,
    avgSatisfaction: 0,
    resolutionRate: 0
  });
  const navigate = useNavigate();
  const ws = useWebSocket();

  useEffect(() => {
    if (ws) {
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Dashboard received:', data);
          
          if (data.type === 'call_update' || data.status === 'complete') {
            setActiveCalls(prev => {
              const existing = prev.find(c => c.call_id === data.call_id);
              if (existing) {
                return prev.map(c => 
                  c.call_id === data.call_id ? { ...c, ...data } : c
                );
              }
              return [...prev, data];
            });
            
            // Update metrics
            if (data.latency_ms) {
              setMetrics(prev => ({
                ...prev,
                activeCalls: activeCalls.length + 1,
                avgLatency: (prev.avgLatency + data.latency_ms) / 2
              }));
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }
  }, [ws, activeCalls.length]);

  const handleCallClick = (callId) => {
    navigate(`/call/${callId}`);
  };

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="glass rounded-2xl p-8 mb-8 border border-gray-200">
          <h1 className="text-5xl font-bold text-gray-900 mb-2">AURA</h1>
          <p className="text-gray-600 text-lg">Anticipatory User Response Assistant</p>
        </div>
        
        <MetricsPanel metrics={metrics} />
        
        <div className="mt-8">
          <div className="glass rounded-2xl p-6 mb-6 border border-gray-200">
            <h2 className="text-2xl font-semibold text-gray-900 mb-1">Active Calls</h2>
            <p className="text-gray-500 text-sm">Real-time conversation monitoring</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeCalls.map(call => (
              <CallCard
                key={call.call_id}
                call={call}
                onClick={() => handleCallClick(call.call_id)}
              />
            ))}
          </div>
          
          {activeCalls.length === 0 && (
            <div className="glass rounded-2xl p-12 text-center border border-gray-200">
              <p className="text-gray-500 text-lg">No active calls</p>
              <p className="text-gray-400 text-sm mt-2">Waiting for incoming conversations...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
