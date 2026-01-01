import React from 'react';

function MetricsPanel({ metrics }) {
  const metricCards = [
    {
      label: 'Active Calls',
      value: metrics.activeCalls,
      unit: '',
      color: 'from-blue-600 to-blue-700'
    },
    {
      label: 'Avg Latency',
      value: metrics.avgLatency.toFixed(0),
      unit: 'ms',
      color: 'from-green-600 to-green-700'
    },
    {
      label: 'Avg Satisfaction',
      value: (metrics.avgSatisfaction * 100).toFixed(1),
      unit: '%',
      color: 'from-purple-600 to-purple-700'
    },
    {
      label: 'Resolution Rate',
      value: (metrics.resolutionRate * 100).toFixed(1),
      unit: '%',
      color: 'from-orange-600 to-orange-700'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {metricCards.map((metric, index) => (
        <div key={index} className="glass-strong rounded-xl p-6 hover:scale-105 transition-transform border border-gray-200">
          <div className="text-gray-600 text-sm font-medium mb-2">{metric.label}</div>
          <div className="flex items-baseline">
            <span className={`text-4xl font-bold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent`}>
              {metric.value}
            </span>
            {metric.unit && (
              <span className="text-gray-500 text-lg ml-2">{metric.unit}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default MetricsPanel;
