import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function CustomerProfile() {
  const { customerId } = useParams();
  const [profile, setProfile] = useState(null);
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileRes, callsRes] = await Promise.all([
          axios.get(`${process.env.REACT_APP_API_URL}/api/v1/customers/${customerId}`),
          axios.get(`${process.env.REACT_APP_API_URL}/api/v1/customers/${customerId}/calls`)
        ]);
        
        setProfile(profileRes.data);
        setCalls(callsRes.data);
      } catch (error) {
        console.error('Error fetching customer data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (customerId) {
      fetchData();
    }
  }, [customerId]);

  if (loading) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-2xl p-12 text-center">
            <p className="text-white/60 text-lg">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen p-6">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-2xl p-12 text-center">
            <p className="text-white/60 text-lg">Customer not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-2xl p-8 mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Customer Profile</h1>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="glass rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Profile Information</h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-white/60">Customer ID</span>
                <div className="font-medium text-white mt-1">{profile.id}</div>
              </div>
              <div>
                <span className="text-sm text-white/60">Customer Type</span>
                <div className="font-medium text-blue-300 mt-1">{profile.customer_type}</div>
              </div>
              <div>
                <span className="text-sm text-white/60">Total Calls</span>
                <div className="font-medium text-white mt-1">{profile.total_calls}</div>
              </div>
              <div>
                <span className="text-sm text-white/60">Preferred Persona</span>
                <div className="font-medium text-white mt-1">{profile.preferred_persona || 'None'}</div>
              </div>
            </div>
          </div>

          <div className="glass rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Performance Metrics</h2>
            <div className="space-y-4">
              <div>
                <span className="text-sm text-white/60">Average Satisfaction</span>
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent mt-2">
                  {(profile.satisfaction_avg * 100).toFixed(1)}%
                </div>
              </div>
              <div>
                <span className="text-sm text-white/60">Resolution Rate</span>
                <div className="text-3xl font-bold bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent mt-2">
                  {(profile.resolution_rate * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="glass rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Call History</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Call ID</th>
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Intent</th>
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Persona</th>
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Satisfaction</th>
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Resolved</th>
                  <th className="text-left py-3 px-4 text-white/60 font-medium text-sm">Date</th>
                </tr>
              </thead>
              <tbody>
                {calls.map(call => (
                  <tr key={call.id} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 px-4 text-white text-sm">{call.id.slice(0, 8)}...</td>
                    <td className="py-3 px-4 text-white text-sm">{call.intent || 'N/A'}</td>
                    <td className="py-3 px-4 text-white text-sm">{call.persona_used || 'N/A'}</td>
                    <td className="py-3 px-4 text-white text-sm">
                      {call.satisfaction_score ? (call.satisfaction_score * 100).toFixed(0) + '%' : 'N/A'}
                    </td>
                    <td className="py-3 px-4">
                      {call.resolved ? (
                        <span className="text-green-300">Yes</span>
                      ) : (
                        <span className="text-red-300">No</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-white/60 text-sm">
                      {call.timestamp ? new Date(call.timestamp).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {calls.length === 0 && (
              <div className="text-center py-8 text-white/40">No call history</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomerProfile;
