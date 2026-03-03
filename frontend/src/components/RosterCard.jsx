import React from 'react';
import { Users, DollarSign, TrendingUp, Target } from 'lucide-react';

const RosterCard = ({ optimizedRoster }) => {
  if (!optimizedRoster) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Optimized Roster</h3>
        <div className="text-center text-gray-500 py-8">
          Run optimization to see results
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: 'Total Players',
      value: optimizedRoster.selected_players?.length || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      label: 'Total Salary',
      value: `₹${optimizedRoster.total_salary?.toFixed(0)}L`,
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      label: 'Total Performance',
      value: optimizedRoster.total_predicted_score?.toFixed(2),
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      label: 'Cap Remaining',
      value: `₹${optimizedRoster.cap_remaining?.toFixed(0)}L`,
      icon: Target,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    }
  ];

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Optimized Roster Summary</h3>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">{stat.label}</span>
                <div className={`${stat.bgColor} p-2 rounded-lg`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Role Distribution */}
      {optimizedRoster.selected_players && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Role Distribution</h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {['Batsman', 'Bowler', 'Allrounder', 'Wicketkeeper'].map(role => {
              const count = optimizedRoster.selected_players.filter(
                p => p.Paying_Role === role
              ).length;
              
              return (
                <div key={role} className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-xs text-gray-600">{role}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Status Badge */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Optimization Status</span>
          <span className="px-3 py-1 text-sm font-medium rounded-full bg-green-100 text-green-800">
            {optimizedRoster.status === 'ok' ? 'Optimal' : optimizedRoster.status}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RosterCard;
