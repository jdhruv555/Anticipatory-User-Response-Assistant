import React from 'react';

function TranscriptPanel({ transcripts }) {
  return (
    <div className="glass rounded-xl p-6 border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Conversation Transcript</h2>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {transcripts.length === 0 ? (
          <div className="text-gray-400 text-center py-8">No transcripts yet</div>
        ) : (
          transcripts.map((transcript, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg ${
                transcript.speaker === 'customer'
                  ? 'bg-blue-50 border-l-4 border-blue-500'
                  : 'bg-gray-50 border-l-4 border-gray-400'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {transcript.speaker}
                </span>
                <span className="text-xs text-gray-400">
                  {transcript.timestamp ? new Date(transcript.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
              <p className="text-gray-900">{transcript.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TranscriptPanel;
