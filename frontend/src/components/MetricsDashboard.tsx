import React from 'react';
import { BarChart3, TrendingUp, Target, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MetricsDashboard: React.FC = () => {
  // Mock metrics data - replace with actual API data
  const accuracyData = [
    { name: 'Baseline', accuracy: 75 },
    { name: 'Tuned Model', accuracy: 86.67 },
    { name: 'Test Set', accuracy: 100 },
  ];

  const featureImportance = [
    { name: 'Fraud Score', importance: 51.54 },
    { name: 'Avg Balance', importance: 48.46 },
    { name: 'Revenue', importance: 0 },
    { name: 'Net Profit', importance: 0 },
    { name: 'Debt/Equity', importance: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <BarChart3 className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Model Performance Metrics</h2>
        </div>
        <p className="text-gray-600">
          Comprehensive analysis of the XGBoost credit scoring model's performance
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <Target className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">Test Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">100.00%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">CV Accuracy</p>
              <p className="text-2xl font-bold text-gray-900">86.67%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="w-8 h-8 text-yellow-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">ROC-AUC</p>
              <p className="text-2xl font-bold text-gray-900">1.000</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center">
            <BarChart3 className="w-8 h-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm font-medium text-gray-600">F1-Score</p>
              <p className="text-2xl font-bold text-gray-900">1.000</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Accuracy Comparison */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Accuracy Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 100]} />
              <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
              <Bar dataKey="accuracy" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Feature Importance */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Importance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={featureImportance} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 60]} />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip formatter={(value) => [`${value}%`, 'Importance']} />
              <Bar dataKey="importance" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Confusion Matrix */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Confusion Matrix</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Predicted →<br/>Actual ↓</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Reject</th>
                <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Approve</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="px-4 py-2 text-sm font-medium text-gray-700">Reject</td>
                <td className="px-4 py-2 text-center bg-green-50 text-green-700 font-semibold">2</td>
                <td className="px-4 py-2 text-center bg-red-50 text-red-700">0</td>
              </tr>
              <tr>
                <td className="px-4 py-2 text-sm font-medium text-gray-700">Approve</td>
                <td className="px-4 py-2 text-center bg-red-50 text-red-700">0</td>
                <td className="px-4 py-2 text-center bg-green-50 text-green-700 font-semibold">2</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Model Details */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Hyperparameters</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• n_estimators: 100</li>
              <li>• max_depth: 3</li>
              <li>• learning_rate: 0.01</li>
              <li>• subsample: 1.0</li>
              <li>• colsample_bytree: 0.8</li>
              <li>• min_child_weight: 1</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Dataset Info</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Total samples: 20</li>
              <li>• Training samples: 16</li>
              <li>• Test samples: 4</li>
              <li>• Features: 5</li>
              <li>• Classes: Approve (12), Reject (8)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;