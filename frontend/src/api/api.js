/**
 * API Client for Apex Zero Roster Optimizer
 * Matches the API contract specification
 */

import axios from 'axios';

// Configurable base URL
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('🚀 API Base URL:', BASE_URL);
console.log('🔧 VITE_API_URL from env:', import.meta.env.VITE_API_URL);
console.log('🌍 All env vars:', import.meta.env);


const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload API - POST /upload
 * Uploads dataset CSV file
 */
export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  // Map response to contract format
  return {
    status: 'ok',
    rows: response.data.players_count
  };
};

/**
 * Predict API - POST /predict
 * Runs ML inference and returns predictions
 */
export const generatePredictions = async () => {
  const response = await api.post('/api/predict/');
  
  // Get full predictions
  const playersResponse = await api.get('/api/predict/players');
  
  // Map response to contract format
  return {
    status: 'ok',
    count: response.data.players_count,
    players: playersResponse.data
  };
};

/**
 * Optimize API - POST /optimize
 * Runs roster optimization
 */
export const optimizeRoster = async (salaryCapInput, rosterSizeInput) => {
  const response = await api.post('/api/optimize/roster', {
    salary_cap: salaryCapInput,
    roster_size: rosterSizeInput,
    role_constraints: [
      { role: 'Batsman', min_count: 3, max_count: 8 },
      { role: 'Bowler', min_count: 3, max_count: 8 },
      { role: 'Allrounder', min_count: 1, max_count: 5 },
      { role: 'Wicketkeeper', min_count: 1, max_count: 3 }
    ]
  });
  
  // Map response to contract format
  return {
    status: 'ok',
    salary_cap: salaryCapInput,
    roster_size: rosterSizeInput,
    selected_players: response.data.selected_players,
    total_salary: response.data.total_salary,
    total_predicted_score: response.data.total_performance,
    cap_remaining: response.data.salary_remaining
  };
};

/**
 * Dashboard API - GET /dashboard
 * Returns aggregated analytics
 */
export const getDashboard = async () => {
  const response = await api.get('/api/dashboard/', {
    params: { limit: 10 }
  });
  
  // Calculate avg value by role
  const avgValueByRole = {};
  if (response.data.role_distribution) {
    const players = await api.get('/api/predict/players');
    const playerData = players.data;
    
    ['Batsman', 'Bowler', 'Allrounder', 'Wicketkeeper'].forEach(role => {
      const rolePlayers = playerData.filter(p => p.Paying_Role === role);
      if (rolePlayers.length > 0) {
        avgValueByRole[role] = rolePlayers.reduce((sum, p) => sum + p.value_index, 0) / rolePlayers.length;
      }
    });
  }
  
  // Map response to contract format
  return {
    top_undervalued: response.data.top_undervalued.map(p => ({
      Player: p.Player,
      value_index: p.value_index,
      ...p
    })),
    top_overpaid: response.data.top_overpaid.map(p => ({
      Player: p.Player,
      value_index: p.value_index,
      ...p
    })),
    avg_value_by_role: avgValueByRole,
    total_players: response.data.stats.total_players
  };
};

/**
 * Additional API methods
 */

export const getTopValuePlayers = async (limit = 10) => {
  const response = await api.get('/api/predict/top-value', {
    params: { limit }
  });
  return response.data;
};

export const getOverpaidPlayers = async (limit = 10) => {
  const response = await api.get('/api/predict/overpaid', {
    params: { limit, min_salary: 100 }
  });
  return response.data;
};

export const simulateTrade = async (tradeOutPlayer, tradeInPlayer) => {
  const response = await api.post('/api/optimize/trade-simulation', {
    trade_out_player: tradeOutPlayer,
    trade_in_player: tradeInPlayer
  });
  return response.data;
};

export const getContractExtensions = async (limit = 10) => {
  const response = await api.get('/api/optimize/contract-extensions', {
    params: { limit }
  });
  return response.data;
};

export const getAllPlayers = async () => {
  const response = await api.get('/api/predict/players');
  return response.data;
};

export const getHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
