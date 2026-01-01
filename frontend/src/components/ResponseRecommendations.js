import React from 'react';

function ResponseRecommendations({ recommendations, onSelect }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="glass rounded-xl p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Response Recommendations</h2>
        <div className="text-gray-400">No recommendations available yet</div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl p-6 border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Response Recommendations</h2>
      <div className="space-y-4">
        {recommendations.map((rec, index) => (
          <div
            key={rec.id || index}
            className={`glass-strong rounded-lg p-4 cursor-pointer transition-all border ${
              rec.ranking === 1
                ? 'border-2 border-green-500 bg-green-50'
                : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'
            }`}
            onClick={() => onSelect(rec.id)}
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-600">
                  #{rec.ranking}
                </span>
                {rec.ranking === 1 && (
                  <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded border border-green-300">
                    Recommended
                  </span>
                )}
              </div>
              <div className="text-sm font-semibold text-blue-700">
                {(rec.score * 100).toFixed(1)}%
              </div>
            </div>
            
            <p className="text-gray-900 mb-3">{rec.text}</p>
            
            {rec.breakdown && (
              <div className="text-xs text-gray-500 space-y-1">
                <div>Resolution: {(rec.breakdown.resolution_probability * 100).toFixed(0)}%</div>
                <div>Satisfaction: {(rec.breakdown.satisfaction_estimate * 100).toFixed(0)}%</div>
                <div>Sentiment: {rec.breakdown.sentiment_improvement > 0 ? '+' : ''}
                  {(rec.breakdown.sentiment_improvement * 100).toFixed(0)}%
                </div>
              </div>
            )}

            {rec.predicted_reactions && rec.predicted_reactions.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="text-xs font-medium text-gray-600 mb-2">Predicted Reactions</div>
                <div className="space-y-1">
                  {rec.predicted_reactions.slice(0, 2).map((reaction, idx) => (
                    <div key={idx} className="text-xs text-gray-500">
                      • {reaction.customer_response} 
                      <span className="ml-2 text-gray-400">
                        ({(reaction.probability * 100).toFixed(0)}%)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ResponseRecommendations;
