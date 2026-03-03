import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import UploadPage from './pages/UploadPage';
import Dashboard from './pages/Dashboard';
import TradeSuggestions from './pages/TradeSuggestions';
import ContractRecommendations from './pages/ContractRecommendations';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/trades" element={<TradeSuggestions />} />
            <Route path="/contracts" element={<ContractRecommendations />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col sm:flex-row justify-between items-center">
              <p className="text-sm text-gray-600">
                © 2026 Apex Zero. AI-Driven Roster Optimizer.
              </p>
              <p className="text-sm text-gray-500 mt-2 sm:mt-0">
                Powered by Machine Learning & Optimization
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
