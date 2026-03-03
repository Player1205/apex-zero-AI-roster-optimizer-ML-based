import React, { useState, useEffect } from 'react';
import { FileText, Star, TrendingUp, AlertCircle } from 'lucide-react';
import PlayerTable from '../components/PlayerTable';
import { getContractExtensions, getAllPlayers } from '../api/api';

const ContractRecommendations = () => {
  const [loading, setLoading] = useState(true);
  const [extensions, setExtensions] = useState([]);
  const [youngTalent, setYoungTalent] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadContractData();
  }, []);

  const loadContractData = async () => {
    try {
      setLoading(true);
      
      // Get contract extension recommendations
      const extensionsResponse = await getContractExtensions(15);
      setExtensions(extensionsResponse.extension_candidates || []);

      // Get all players and filter for young talent
      const allPlayers = await getAllPlayers();
      const young = allPlayers
        .filter(p => p.AGE < 27 && p.value_index > 0.3)
        .sort((a, b) => b.value_index - a.value_index)
        .slice(0, 15);
      setYoungTalent(young);

      setLoading(false);
    } catch (err) {
      console.error('Error loading contract data:', err);
      setError(err.response?.data?.detail || 'Failed to load contract data');
      setLoading(false);
    }
  };

  const getPriorityBadge = (valueIndex) => {
    if (valueIndex > 0.5) {
      return <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">High Priority</span>;
    } else if (valueIndex > 0.3) {
      return <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">Medium Priority</span>;
    } else {
      return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Low Priority</span>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading contract recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Error Loading Data</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={loadContractData}
              className="mt-3 btn-primary text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Contract Recommendations</h1>
        <p className="text-gray-600 mt-1">Strategic guidance for contract extensions and renewals</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Extension Candidates</span>
            <div className="bg-blue-100 p-2 rounded-lg">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">{extensions.length}</p>
          <p className="text-xs text-gray-500 mt-1">High-value players</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Young Talent</span>
            <div className="bg-green-100 p-2 rounded-lg">
              <Star className="h-5 w-5 text-green-600" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">{youngTalent.length}</p>
          <p className="text-xs text-gray-500 mt-1">Under 27 years</p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Avg Value Index</span>
            <div className="bg-purple-100 p-2 rounded-lg">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {extensions.length > 0
              ? (extensions.reduce((sum, p) => sum + p.value_index, 0) / extensions.length).toFixed(3)
              : '0.000'}
          </p>
          <p className="text-xs text-gray-500 mt-1">Extension candidates</p>
        </div>
      </div>

      {/* Contract Extension Recommendations */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">Priority Extension Candidates</h2>
            <p className="text-sm text-gray-600 mt-1">
              Players providing strong value who should be prioritized for contract extensions
            </p>
          </div>
        </div>

        {extensions.length > 0 ? (
          <div className="space-y-4">
            {extensions.slice(0, 10).map((player, idx) => (
              <div key={idx} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{player.Player}</h3>
                      {getPriorityBadge(player.value_index)}
                    </div>
                    
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">Team:</span>
                        <span className="ml-1 font-medium">{player.TEAM}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Role:</span>
                        <span className="ml-1 font-medium">{player.Paying_Role}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Age:</span>
                        <span className="ml-1 font-medium">{player.AGE}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Current Salary:</span>
                        <span className="ml-1 font-medium">₹{player.salary_lakhs.toFixed(0)}L</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3 text-sm">
                      <div>
                        <span className="text-gray-600">Performance:</span>
                        <span className="ml-1 font-medium">{player.predicted_performance?.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Value Index:</span>
                        <span className="ml-1 font-medium text-green-600">{player.value_index?.toFixed(4)}</span>
                      </div>
                      {player.suggested_salary && (
                        <div>
                          <span className="text-gray-600">Suggested Salary:</span>
                          <span className="ml-1 font-medium">₹{player.suggested_salary.toFixed(0)}L</span>
                        </div>
                      )}
                    </div>

                    {player.extension_reason && (
                      <div className="mt-3 p-2 bg-blue-50 rounded text-sm text-blue-800">
                        <span className="font-medium">Reason:</span> {player.extension_reason}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No extension candidates available
          </div>
        )}
      </div>

      {/* Young Talent Section */}
      <div>
        <div className="flex items-center mb-4">
          <Star className="h-6 w-6 text-yellow-500 mr-2" />
          <h2 className="text-xl font-bold">Young Talent (Under 27)</h2>
        </div>
        
        {youngTalent.length > 0 ? (
          <PlayerTable
            players={youngTalent}
            title="High-Value Young Players"
            maxHeight="500px"
          />
        ) : (
          <div className="card text-center py-8 text-gray-500">
            No young talent data available
          </div>
        )}
        
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start">
            <Star className="h-5 w-5 text-yellow-600 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-800">Investment Opportunity</p>
              <p className="text-sm text-yellow-700 mt-1">
                These young players (under 27) provide strong value and have significant room for growth. 
                Consider long-term contracts to secure their services at current rates before their market value increases.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* All Extension Candidates Table */}
      {extensions.length > 10 && (
        <div>
          <h2 className="text-xl font-bold mb-4">All Extension Candidates</h2>
          <PlayerTable
            players={extensions}
            title={`All ${extensions.length} Candidates`}
            maxHeight="600px"
          />
        </div>
      )}

      {/* Contract Strategy Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-lg mb-3 text-blue-900">Contract Extension Strategy</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>High Priority:</strong> Players with value index &gt; 0.5 - immediate extensions recommended</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Medium Priority:</strong> Players with value index 0.3-0.5 - negotiate within next season</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Young Talent:</strong> Players under 27 with high value - secure long-term deals</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">•</span>
            <span><strong>Performance Bonus:</strong> Consider performance-based incentives for top performers</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default ContractRecommendations;
