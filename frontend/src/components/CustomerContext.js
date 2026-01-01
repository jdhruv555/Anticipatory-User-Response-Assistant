import React from 'react';

function CustomerContext({ context }) {
  if (!context) {
    return (
      <div className="glass rounded-xl p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Context</h2>
        <div className="text-gray-400">No context available</div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl p-6 border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Context</h2>
      <div className="space-y-4">
        <div>
          <span className="text-sm font-medium text-gray-600">Customer Type</span>
          <div className="mt-1 text-lg font-semibold text-blue-700">
            {context.customer_type || 'Unknown'}
          </div>
        </div>
        
        <div>
          <span className="text-sm font-medium text-gray-600">Selected Persona</span>
          <div className="mt-1 text-base text-gray-900">
            {context.selected_persona?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Default'}
          </div>
        </div>

        {context.customer_profile && (
          <div className="pt-4 border-t border-gray-200 space-y-3">
            <div className="text-sm">
              <span className="text-gray-600">Total Calls</span>
              <span className="font-semibold text-gray-900 ml-2">{context.customer_profile.total_calls || 0}</span>
            </div>
            <div className="text-sm">
              <span className="text-gray-600">Avg Satisfaction</span>
              <span className="font-semibold text-gray-900 ml-2">
                {((context.customer_profile.satisfaction_avg || 0) * 100).toFixed(0)}%
              </span>
            </div>
            <div className="text-sm">
              <span className="text-gray-600">Resolution Rate</span>
              <span className="font-semibold text-gray-900 ml-2">
                {((context.customer_profile.resolution_rate || 0) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CustomerContext;
