import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket';
import TranscriptPanel from './TranscriptPanel';
import ResponseRecommendations from './ResponseRecommendations';
import SentimentIndicator from './SentimentIndicator';
import CustomerContext from './CustomerContext';

function CallView() {
  const { callId } = useParams();
  const [callData, setCallData] = useState(null);
  const [transcripts, setTranscripts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const ws = useWebSocket();

  useEffect(() => {
    if (ws && callId) {
      ws.send(JSON.stringify({
        type: 'subscribe_call',
        call_id: callId
      }));

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('CallView received:', data);
          
          if (data.call_id === callId || data.type === 'call_update') {
            setCallData(prev => ({ ...prev, ...data }));
            
            if (data.transcript) {
              setTranscripts(prev => {
                // Avoid duplicates
                const exists = prev.some(t => t.text === data.transcript && t.timestamp === data.timestamp);
                if (!exists) {
                  return [...prev, {
                    text: data.transcript,
                    timestamp: data.timestamp,
                    speaker: 'customer'
                  }];
                }
                return prev;
              });
            }
            
            if (data.ranked_responses && data.ranked_responses.length > 0) {
              setRecommendations(data.ranked_responses);
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    }

    return () => {
      if (ws) {
        ws.send(JSON.stringify({
          type: 'unsubscribe_call',
          call_id: callId
        }));
      }
    };
  }, [ws, callId]);

  const handleResponseSelect = (responseId) => {
    if (ws) {
      ws.send(JSON.stringify({
        type: 'agent_response_selected',
        call_id: callId,
        response_id: responseId
      }));
    }
  };

  if (!callData) {
    return (
      <div className="min-h-screen p-6 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-2xl p-12 text-center border border-gray-200">
            <p className="text-gray-500 text-lg">Loading call data...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-2xl p-6 mb-6 border border-gray-200">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Call: {callId}</h1>
          {callData.latency_ms && (
            <div className="text-sm text-gray-500">
              Latency: {callData.latency_ms.toFixed(0)}ms
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <TranscriptPanel transcripts={transcripts} />
            
            {callData.interpretation && (
              <div className="glass rounded-xl p-6 border border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis</h2>
                <div className="space-y-4">
                  <div>
                    <span className="text-gray-600 text-sm font-medium">Intent</span>
                    <div className="text-gray-900 mt-1">
                      <span className="text-blue-700 font-medium">
                        {callData.interpretation.intent?.intent || 'Unknown'}
                      </span>
                      <span className="text-gray-500 ml-2 text-sm">
                        ({(callData.interpretation.intent?.confidence * 100).toFixed(0)}% confidence)
                      </span>
                    </div>
                  </div>
                  <SentimentIndicator sentiment={callData.interpretation.sentiment} />
                </div>
              </div>
            )}

            <ResponseRecommendations
              recommendations={recommendations}
              onSelect={handleResponseSelect}
            />
          </div>

          <div>
            <CustomerContext context={callData.customer_context} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default CallView;
