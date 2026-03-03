import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ZAxis } from 'recharts';

const ROLE_COLORS = {
  'Batsman': '#3b82f6',
  'Bowler': '#ef4444',
  'Allrounder': '#10b981',
  'Wicketkeeper': '#f59e0b'
};

const SalaryScatter = ({ players }) => {
  if (!players || players.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Salary vs Performance</h3>
        <div className="text-center text-gray-500 py-8">
          No data available
        </div>
      </div>
    );
  }

  // Group players by role
  const playersByRole = {
    Batsman: [],
    Bowler: [],
    Allrounder: [],
    Wicketkeeper: []
  };

  players.forEach(player => {
    const role = player.Paying_Role;
    if (playersByRole[role]) {
      playersByRole[role].push({
        x: player.salary_lakhs,
        y: player.predicted_performance,
        name: player.Player,
        team: player.TEAM,
        z: 100
      });
    }
  });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold">{data.name}</p>
          <p className="text-sm text-gray-600">{data.team}</p>
          <p className="text-sm">Salary: ₹{data.x.toFixed(0)}L</p>
          <p className="text-sm">Performance: {data.y.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Salary vs Performance Analysis</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name="Salary"
            unit="L"
            label={{ value: 'Salary (Lakhs)', position: 'insideBottom', offset: -10 }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="Performance"
            label={{ value: 'Predicted Performance', angle: -90, position: 'insideLeft' }}
          />
          <ZAxis type="number" dataKey="z" range={[50, 200]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {Object.entries(playersByRole).map(([role, data]) => (
            data.length > 0 && (
              <Scatter
                key={role}
                name={role}
                data={data}
                fill={ROLE_COLORS[role]}
                opacity={0.7}
              />
            )
          ))}
        </ScatterChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        {Object.entries(ROLE_COLORS).map(([role, color]) => (
          <div key={role} className="flex items-center">
            <div
              className="w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: color }}
            />
            <span>{role}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SalaryScatter;
