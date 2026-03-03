import React, { useState, useEffect } from 'react';
import { Users, DollarSign, TrendingUp, AlertCircle } from 'lucide-react';
import SalaryScatter from '../components/SalaryScatter';
import ValueBar from '../components/ValueBar';
import PlayerTable from '../components/PlayerTable';
import RosterCard from '../components/RosterCard';
import { getDashboard } from '../api/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [allPlayers, setAllPlayers] = useState([]);
  const [optimizedRoster, setOptimizedRoster] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard data
      const data = await getDashboard();
      setDashboardData(data);

      // Load all players from session storage (set during upload)
      const playersData = sessionStorage.getItem('allPlayers');
      if (playersData) {
        setAllPlayers(JSON.parse(playersData));
      }

      // Load optimization results from session storage
      const optimizationData = sessionStorage.getItem('optimizationResults');
      if (optimizationData) {
        setOptimizedRoster(JSON.parse(optimizationData));
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load dashboard data');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
            <p className="text-sm font-medium text-red-800">Error Loading Dashboard</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={loadDashboardData}
              className="mt-3 btn-primary text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="card">
        <div className="text-center py-8">
          <p className="text-gray-600">No data available. Please upload a dataset first.</p>
          <button
            onClick={() => window.location.href = '/'}
            className="mt-4 btn-primary"
          >
            Upload Dataset
          </button>
        </div>
      </div>
    );
  }

  const summaryCards = [
    {
      label: 'Total Players',
      value: dashboardData.total_players,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      label: 'Avg Value by Role',
      value: Object.values(dashboardData.avg_value_by_role || {}).length > 0
        ? (Object.values(dashboardData.avg_value_by_role).reduce((a, b) => a + b, 0) / 
           Object.values(dashboardData.avg_value_by_role).length).toFixed(3)
        : '0.000',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      label: 'Top Value Index',
      value: dashboardData.top_undervalued?.[0]?.value_index?.toFixed(3) || '0.000',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      label: 'Lowest Value Index',
      value: dashboardData.top_overpaid?.[0]?.value_index?.toFixed(3) || '0.000',
      icon: AlertCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Comprehensive roster analytics and insights</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {summaryCards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div key={idx} className="card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">{card.label}</span>
                <div className={`${card.bgColor} p-2 rounded-lg`}>
                  <Icon className={`h-5 w-5 ${card.color}`} />
                </div>
              </div>
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
            </div>
          );
        })}
      </div>

      {/* Optimized Roster Summary */}
      {optimizedRoster && <RosterCard optimizedRoster={optimizedRoster} />}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scatter Plot */}
        <SalaryScatter players={allPlayers} />

        {/* Value Bar Chart */}
        <ValueBar 
          players={dashboardData.top_undervalued} 
          title="Top 10 Value Players"
          limit={10}
        />
      </div>

      {/* Average Value by Role Chart */}
      {dashboardData.avg_value_by_role && Object.keys(dashboardData.avg_value_by_role).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Average Value Index by Role</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {Object.entries(dashboardData.avg_value_by_role).map(([role, value]) => (
              <div key={role} className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-900">{value.toFixed(3)}</div>
                <div className="text-sm text-gray-600 mt-1">{role}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tables Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Optimized Roster Table */}
        {optimizedRoster && optimizedRoster.selected_players && (
          <PlayerTable
            players={optimizedRoster.selected_players}
            title="Optimized Roster"
            maxHeight="400px"
          />
        )}

        {/* Top Undervalued Players */}
        <PlayerTable
          players={dashboardData.top_undervalued}
          title="Top Undervalued Players"
          maxHeight="400px"
        />
      </div>

      {/* All Players Table */}
      {allPlayers.length > 0 && (
        <PlayerTable
          players={allPlayers}
          title="All Players"
          maxHeight="600px"
        />
      )}
    </div>
  );
};

export default Dashboard;
