import React from 'react';

function SentimentIndicator({ sentiment }) {
  if (!sentiment) return null;

  const sentimentColors = {
    positive: 'text-green-700 border-green-300 bg-green-50',
    negative: 'text-red-700 border-red-300 bg-red-50',
    neutral: 'text-gray-700 border-gray-300 bg-gray-50'
  };

  const color = sentimentColors[sentiment.sentiment] || sentimentColors.neutral;
  const polarity = sentiment.polarity || 0;
  const emotion = sentiment.emotion || 'neutral';

  return (
    <div className="space-y-3">
      <div>
        <span className="text-gray-600 text-sm font-medium">Sentiment</span>
        <div className={`mt-2 px-3 py-2 rounded-lg border ${color} inline-block`}>
          {sentiment.sentiment} ({emotion})
        </div>
      </div>
      <div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <div
            className={`h-2 rounded-full transition-all ${
              polarity > 0 ? 'bg-gradient-to-r from-green-500 to-green-600' : 
              polarity < 0 ? 'bg-gradient-to-r from-red-500 to-red-600' : 
              'bg-gray-400'
            }`}
            style={{ width: `${Math.abs(polarity) * 100}%` }}
          />
        </div>
        <div className="text-xs text-gray-500 mt-2">
          Polarity: {polarity.toFixed(2)} | Confidence: {(sentiment.confidence * 100).toFixed(0)}%
        </div>
      </div>
    </div>
  );
}

export default SentimentIndicator;
