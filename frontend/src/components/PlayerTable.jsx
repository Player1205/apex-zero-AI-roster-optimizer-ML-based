import React, { useState } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

const PlayerTable = ({ players, title = 'Players', maxHeight = '500px' }) => {
  const [sortField, setSortField] = useState('value_index');
  const [sortDirection, setSortDirection] = useState('desc');

  if (!players || players.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="text-center text-gray-500 py-8">
          No players available
        </div>
      </div>
    );
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedPlayers = [...players].sort((a, b) => {
    const aVal = a[sortField] || 0;
    const bVal = b[sortField] || 0;
    
    if (sortDirection === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="inline h-4 w-4" />
    ) : (
      <ChevronDown className="inline h-4 w-4" />
    );
  };

  const getValueBadge = (valueIndex) => {
    if (valueIndex > 0.5) {
      return <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">Elite</span>;
    } else if (valueIndex > 0.3) {
      return <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">Good</span>;
    } else if (valueIndex > 0.1) {
      return <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">Fair</span>;
    } else {
      return <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-800">Poor</span>;
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">
        {title} ({players.length})
      </h3>
      
      <div className="overflow-x-auto" style={{ maxHeight }}>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('Player')}
              >
                Player <SortIcon field="Player" />
              </th>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('TEAM')}
              >
                Team <SortIcon field="TEAM" />
              </th>
              <th
                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('Paying_Role')}
              >
                Role <SortIcon field="Paying_Role" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('salary_lakhs')}
              >
                Salary (L) <SortIcon field="salary_lakhs" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('predicted_performance')}
              >
                Performance <SortIcon field="predicted_performance" />
              </th>
              <th
                className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('value_index')}
              >
                Value Index <SortIcon field="value_index" />
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rating
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedPlayers.map((player, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                  {player.Player}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {player.TEAM}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {player.Paying_Role}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right">
                  ₹{player.salary_lakhs?.toFixed(0)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right">
                  {player.predicted_performance?.toFixed(2)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
                  {player.value_index?.toFixed(4)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  {getValueBadge(player.value_index)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlayerTable;
