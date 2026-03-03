import React, { useState } from 'react';
import { Upload, Play, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadDataset, generatePredictions, optimizeRoster } from '../api/api';
import { useNavigate } from 'react-router-dom';

const UploadPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [salaryCap, setSalaryCap] = useState(10000);
  const [rosterSize, setRosterSize] = useState(25);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('upload'); // upload, predict, optimize, complete
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid CSV file');
    }
  };

  const handleProcess = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Upload
      setStep('upload');
      const uploadResponse = await uploadDataset(file);
      console.log('Upload successful:', uploadResponse);
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 2: Predict
      setStep('predict');
      const predictResponse = await generatePredictions();
      console.log('Predictions generated:', predictResponse);
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 3: Optimize
      setStep('optimize');
      const optimizeResponse = await optimizeRoster(salaryCap, rosterSize);
      console.log('Optimization complete:', optimizeResponse);
      
      setResults({
        upload: uploadResponse,
        predictions: predictResponse,
        optimization: optimizeResponse
      });
      
      setStep('complete');
      setLoading(false);

      // Store results in session storage for other pages
      sessionStorage.setItem('optimizationResults', JSON.stringify(optimizeResponse));
      sessionStorage.setItem('allPlayers', JSON.stringify(predictResponse.players));

    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || err.message || 'An error occurred');
      setLoading(false);
      setStep('upload');
    }
  };

  const getStepStatus = (currentStep) => {
    const steps = ['upload', 'predict', 'optimize', 'complete'];
    const currentIndex = steps.indexOf(step);
    const stepIndex = steps.indexOf(currentStep);

    if (stepIndex < currentIndex) return 'complete';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const StepIndicator = ({ stepName, label, icon: Icon }) => {
    const status = getStepStatus(stepName);
    
    return (
      <div className="flex flex-col items-center">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 ${
          status === 'complete' ? 'bg-green-500 text-white' :
          status === 'active' ? 'bg-blue-500 text-white animate-pulse' :
          'bg-gray-200 text-gray-500'
        }`}>
          {status === 'complete' ? <CheckCircle className="h-6 w-6" /> : <Icon className="h-6 w-6" />}
        </div>
        <span className={`text-sm font-medium ${
          status !== 'pending' ? 'text-gray-900' : 'text-gray-500'
        }`}>
          {label}
        </span>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Upload & Optimize Roster</h2>

        {/* Progress Steps */}
        <div className="flex justify-between items-center mb-8">
          <StepIndicator stepName="upload" label="Upload CSV" icon={Upload} />
          <div className="flex-1 h-1 bg-gray-200 mx-4" />
          <StepIndicator stepName="predict" label="Generate Predictions" icon={Play} />
          <div className="flex-1 h-1 bg-gray-200 mx-4" />
          <StepIndicator stepName="optimize" label="Optimize Roster" icon={Play} />
          <div className="flex-1 h-1 bg-gray-200 mx-4" />
          <StepIndicator stepName="complete" label="Complete" icon={CheckCircle} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Error</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {step === 'complete' && results && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-start mb-4">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-green-800">Process Complete!</p>
                <p className="text-sm text-green-700">Successfully optimized roster with {results.optimization.roster_size} players</p>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-gray-600">Players Uploaded</p>
                <p className="text-2xl font-bold text-gray-900">{results.upload.rows}</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-gray-600">Total Salary Used</p>
                <p className="text-2xl font-bold text-gray-900">₹{results.optimization.total_salary.toFixed(0)}L</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-gray-600">Performance Score</p>
                <p className="text-2xl font-bold text-gray-900">{results.optimization.total_predicted_score.toFixed(1)}</p>
              </div>
            </div>

            <div className="mt-4 flex gap-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-primary flex-1"
              >
                View Dashboard
              </button>
              <button
                onClick={() => {
                  setStep('upload');
                  setFile(null);
                  setResults(null);
                }}
                className="btn-secondary"
              >
                Upload New Dataset
              </button>
            </div>
          </div>
        )}

        {/* Upload Form */}
        {step !== 'complete' && (
          <>
            <div className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Player Dataset (CSV)
                </label>
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-10 h-10 mb-3 text-gray-400" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">CSV file only</p>
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      accept=".csv"
                      onChange={handleFileChange}
                      disabled={loading}
                    />
                  </label>
                </div>
                {file && (
                  <p className="mt-2 text-sm text-green-600 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    {file.name}
                  </p>
                )}
              </div>

              {/* Salary Cap */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Cap (Lakhs)
                </label>
                <input
                  type="number"
                  value={salaryCap}
                  onChange={(e) => setSalaryCap(Number(e.target.value))}
                  className="input-field"
                  disabled={loading}
                  min="1000"
                  max="20000"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Maximum total salary for the roster (₹{salaryCap.toLocaleString()} lakhs = ₹{(salaryCap / 100).toFixed(1)} crores)
                </p>
              </div>

              {/* Roster Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Roster Size
                </label>
                <input
                  type="number"
                  value={rosterSize}
                  onChange={(e) => setRosterSize(Number(e.target.value))}
                  className="input-field"
                  disabled={loading}
                  min="11"
                  max="30"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Number of players to select (11-30)
                </p>
              </div>
            </div>

            {/* Action Button */}
            <div className="mt-6">
              <button
                onClick={handleProcess}
                disabled={!file || loading}
                className="btn-primary w-full"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    {step === 'upload' && 'Uploading...'}
                    {step === 'predict' && 'Generating Predictions...'}
                    {step === 'optimize' && 'Optimizing Roster...'}
                  </span>
                ) : (
                  'Process & Optimize'
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default UploadPage;
