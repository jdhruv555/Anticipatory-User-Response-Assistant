import React from 'react';

function CallCard({ call, onClick }) {
  const sentiment = call.interpretation?.sentiment;
  
  const getSentimentColor = (sentiment) => {
    if (sentiment === 'positive') return 'text-green-700';
    if (sentiment === 'negative') return 'text-red-700';
    return 'text-gray-700';
  };

  return (
    <div
      onClick={onClick}
      className="glass-strong rounded-xl p-6 cursor-pointer hover:scale-105 transition-all hover:shadow-xl border border-gray-200"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg mb-1">
            Call {call.call_id?.slice(0, 8) || 'Unknown'}
          </h3>
          <p className="text-gray-500 text-sm">
            {call.timestamp ? new Date(call.timestamp).toLocaleString() : 'Active'}
          </p>
        </div>
        {call.latency_ms && (
          <span className={`text-xs px-3 py-1 rounded-full font-medium ${
            call.latency_ms < 2000 ? 'bg-green-100 text-green-700 border border-green-300' :
            call.latency_ms < 3000 ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' :
            'bg-red-100 text-red-700 border border-red-300'
          }`}>
            {call.latency_ms.toFixed(0)}ms
          </span>
        )}
      </div>

      {call.interpretation && (
        <div className="space-y-3 mb-4">
          <div>
            <span className="text-gray-500 text-xs uppercase tracking-wide">Intent</span>
            <div className="text-sm font-medium text-blue-700 mt-1">
              {call.interpretation.intent?.intent || 'Unknown'}
            </div>
          </div>
          {sentiment && (
            <div>
              <span className="text-gray-500 text-xs uppercase tracking-wide">Sentiment</span>
              <div className={`text-sm font-medium mt-1 ${getSentimentColor(sentiment.sentiment)}`}>
                {sentiment.sentiment} ({sentiment.emotion})
              </div>
            </div>
          )}
        </div>
      )}

      {call.ranked_responses && call.ranked_responses.length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <div className="text-gray-500 text-xs mb-2">
            {call.ranked_responses.length} response recommendations available
          </div>
          <div className="text-sm font-semibold text-green-700">
            Top: {(call.ranked_responses[0].score * 100).toFixed(0)}% confidence
          </div>
        </div>
      )}
    </div>
  );
}

export default CallCard;
