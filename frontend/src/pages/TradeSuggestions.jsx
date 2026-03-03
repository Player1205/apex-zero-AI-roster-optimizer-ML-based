import React, { useState, useEffect } from 'react';
import { ArrowRightLeft, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react';
import PlayerTable from '../components/PlayerTable';
import { getOverpaidPlayers, getTopValuePlayers, simulateTrade, getAllPlayers } from '../api/api';

const TradeSuggestions = () => {
  const [loading, setLoading] = useState(true);
  const [overpaid, setOverpaid] = useState([]);
  const [undervalued, setUndervalued] = useState([]);
  const [allPlayers, setAllPlayers] = useState([]);
  
  // Trade simulation state
  const [tradeOutPlayer, setTradeOutPlayer] = useState('');
  const [tradeInPlayer, setTradeInPlayer] = useState('');
  const [tradeResult, setTradeResult] = useState(null);
  const [simulatingTrade, setSimulatingTrade] = useState(false);
  const [tradeError, setTradeError] = useState(null);

  useEffect(() => {
    loadTradeData();
  }, []);

  const loadTradeData = async () => {
    try {
      setLoading(true);
      
      const [overpaidData, undervaluedData, playersData] = await Promise.all([
        getOverpaidPlayers(15),
        getTopValuePlayers(15),
        getAllPlayers()
      ]);

      setOverpaid(overpaidData);
      setUndervalued(undervaluedData);
      setAllPlayers(playersData);
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading trade data:', err);
      setLoading(false);
    }
  };

  const handleSimulateTrade = async () => {
    if (!tradeOutPlayer || !tradeInPlayer) {
      setTradeError('Please select both players');
      return;
    }

    if (tradeOutPlayer === tradeInPlayer) {
      setTradeError('Please select different players');
      return;
    }

    try {
      setSimulatingTrade(true);
      setTradeError(null);
      
      const result = await simulateTrade(tradeOutPlayer, tradeInPlayer);
      setTradeResult(result);
      
      setSimulatingTrade(false);
    } catch (err) {
      console.error('Error simulating trade:', err);
      setTradeError(err.response?.data?.detail || 'Failed to simulate trade');
      setSimulatingTrade(false);
    }
  };

  const getImpactColor = (value) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getImpactIcon = (value) => {
    if (value > 0) return <TrendingUp className="h-4 w-4" />;
    if (value < 0) return <TrendingDown className="h-4 w-4" />;
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading trade analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Trade Analysis</h1>
        <p className="text-gray-600 mt-1">Identify trade opportunities and simulate player exchanges</p>
      </div>

      {/* Trade Simulator */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Trade Simulator</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Trade Out */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trade Away
            </label>
            <select
              value={tradeOutPlayer}
              onChange={(e) => setTradeOutPlayer(e.target.value)}
              className="input-field"
            >
              <option value="">Select player to trade away...</option>
              {overpaid.map((player, idx) => (
                <option key={idx} value={player.Player}>
                  {player.Player} - ₹{player.salary_lakhs.toFixed(0)}L
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Select an overpaid player</p>
          </div>

          {/* Trade In */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Acquire
            </label>
            <select
              value={tradeInPlayer}
              onChange={(e) => setTradeInPlayer(e.target.value)}
              className="input-field"
            >
              <option value="">Select player to acquire...</option>
              {undervalued.map((player, idx) => (
                <option key={idx} value={player.Player}>
                  {player.Player} - ₹{player.salary_lakhs.toFixed(0)}L
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Select an undervalued player</p>
          </div>
        </div>

        <button
          onClick={handleSimulateTrade}
          disabled={simulatingTrade || !tradeOutPlayer || !tradeInPlayer}
          className="btn-primary w-full"
        >
          {simulatingTrade ? (
            <span className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Simulating...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <ArrowRightLeft className="h-5 w-5 mr-2" />
              Simulate Trade
            </span>
          )}
        </button>

        {/* Trade Error */}
        {tradeError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{tradeError}</p>
          </div>
        )}

        {/* Trade Results */}
        {tradeResult && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="font-semibold text-lg mb-4">Trade Impact Analysis</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              {/* Salary Change */}
              <div className="bg-white p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Salary Change</span>
                  {getImpactIcon(tradeResult.impact.salary_change)}
                </div>
                <p className={`text-2xl font-bold ${getImpactColor(tradeResult.impact.salary_change)}`}>
                  {tradeResult.impact.salary_change > 0 ? '+' : ''}
                  ₹{tradeResult.impact.salary_change.toFixed(0)}L
                </p>
              </div>

              {/* Performance Change */}
              <div className="bg-white p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Performance Change</span>
                  {getImpactIcon(tradeResult.impact.performance_change)}
                </div>
                <p className={`text-2xl font-bold ${getImpactColor(tradeResult.impact.performance_change)}`}>
                  {tradeResult.impact.performance_change > 0 ? '+' : ''}
                  {tradeResult.impact.performance_change.toFixed(2)}
                </p>
              </div>

              {/* Value Index Change */}
              <div className="bg-white p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Value Change</span>
                  {getImpactIcon(tradeResult.impact.value_index_change)}
                </div>
                <p className={`text-2xl font-bold ${getImpactColor(tradeResult.impact.value_index_change)}`}>
                  {tradeResult.impact.value_index_change > 0 ? '+' : ''}
                  {tradeResult.impact.value_index_change.toFixed(4)}
                </p>
              </div>
            </div>

            {/* Recommendation */}
            <div className={`p-4 rounded-lg ${
              tradeResult.recommendation.includes('Highly Recommended') ? 'bg-green-100 border-green-200' :
              tradeResult.recommendation.includes('Recommended') ? 'bg-blue-100 border-blue-200' :
              tradeResult.recommendation.includes('Consider') ? 'bg-yellow-100 border-yellow-200' :
              'bg-red-100 border-red-200'
            } border`}>
              <p className="font-semibold text-lg">{tradeResult.recommendation}</p>
            </div>
          </div>
        )}
      </div>

      {/* Overpaid Players */}
      <div>
        <div className="flex items-center mb-4">
          <TrendingDown className="h-6 w-6 text-red-500 mr-2" />
          <h2 className="text-xl font-bold">Overpaid Players (Trade Candidates)</h2>
        </div>
        <PlayerTable
          players={overpaid}
          title="Players with Low Value Index"
          maxHeight="400px"
        />
        <p className="text-sm text-gray-600 mt-2">
          These players have low value index scores relative to their salaries. Consider trading them to free up salary cap space.
        </p>
      </div>

      {/* Undervalued Players */}
      <div>
        <div className="flex items-center mb-4">
          <TrendingUp className="h-6 w-6 text-green-500 mr-2" />
          <h2 className="text-xl font-bold">Undervalued Players (Acquisition Targets)</h2>
        </div>
        <PlayerTable
          players={undervalued}
          title="Players with High Value Index"
          maxHeight="400px"
        />
        <p className="text-sm text-gray-600 mt-2">
          These players provide excellent value for their salaries. Consider acquiring them to improve roster efficiency.
        </p>
      </div>
    </div>
  );
};

export default TradeSuggestions;
