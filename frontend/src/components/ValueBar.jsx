import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const ValueBar = ({ players, title = 'Top Value Players', limit = 10 }) => {
  if (!players || players.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">{title}</h3>
        <div className="text-center text-gray-500 py-8">
          No data available
        </div>
      </div>
    );
  }

  // Sort by value_index and take top N
  const topPlayers = [...players]
    .sort((a, b) => b.value_index - a.value_index)
    .slice(0, limit)
    .map(player => ({
      name: player.Player,
      value_index: player.value_index,
      salary: player.salary_lakhs,
      performance: player.predicted_performance
    }));

  const getBarColor = (value) => {
    if (value > 0.5) return '#10b981'; // green for elite value
    if (value > 0.3) return '#3b82f6'; // blue for good value
    if (value > 0.1) return '#f59e0b'; // yellow for fair value
    return '#ef4444'; // red for poor value
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <p className="text-sm">Value Index: {data.value_index.toFixed(4)}</p>
          <p className="text-sm">Salary: ₹{data.salary.toFixed(0)}L</p>
          <p className="text-sm">Performance: {data.performance.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={topPlayers}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" label={{ value: 'Value Index', position: 'insideBottom', offset: -5 }} />
          <YAxis
            dataKey="name"
            type="category"
            width={90}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="value_index" radius={[0, 8, 8, 0]}>
            {topPlayers.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.value_index)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full mr-2 bg-green-500" />
          <span>Elite Value (&gt;0.5)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full mr-2 bg-blue-500" />
          <span>Good Value (0.3-0.5)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full mr-2 bg-yellow-500" />
          <span>Fair Value (0.1-0.3)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 rounded-full mr-2 bg-red-500" />
          <span>Poor Value (&lt;0.1)</span>
        </div>
      </div>
    </div>
  );
};

export default ValueBar;
