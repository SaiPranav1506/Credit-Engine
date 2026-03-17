import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, TrendingUp, FileText, Shield, Database, BarChart3, Download } from 'lucide-react';
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, 
  BarChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  ScatterChart, Scatter, Bar
} from 'recharts';

export type ProcessingResult = {
  decision: 'APPROVE' | 'REJECT';
  credit_score: number;
  loan_limit: number;
  risk_premium_pct: number;
  five_cs: {
    character: { score: number; rationale: string };
    capacity: { score: number; rationale: string };
    capital: { score: number; rationale: string };
    collateral: { score: number; rationale: string };
    conditions: { score: number; rationale: string };
  };
  narrative: string;
  processing_status: string[];
  cam_path?: string;
  fraud_analysis?: {
    fraud_score: number;
    total_flags: number;
    high_severity_count: number;
  };
  bank_analysis?: {
    avg_balance: number;
    total_inflow: number;
    total_outflow: number;
  };
};

interface ResultsDisplayProps {
  result?: ProcessingResult | null;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  // If no result yet, show empty state
  if (!result) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No Results Yet</h3>
        <p className="text-gray-500">Submit a credit assessment from the form to see results here.</p>
      </div>
    );
  }

  const displayResult = result;

  const getDecisionColor = (decision: string) => {
    switch (decision) {
      case 'APPROVE':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'REJECT':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    }
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'APPROVE':
        return <CheckCircle className="w-8 h-8" />;
      case 'REJECT':
        return <XCircle className="w-8 h-8" />;
      default:
        return <AlertTriangle className="w-8 h-8" />;
    }
  };

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { level: 'Low', color: 'text-green-600' };
    if (score >= 40) return { level: 'Medium', color: 'text-yellow-600' };
    return { level: 'High', color: 'text-red-600' };
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-8">
      {/* Results Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Credit Assessment Results</h1>
        <p className="text-lg text-gray-600">Analysis completed successfully</p>
      </div>
      {/* Processing Status */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <BarChart3 className="w-6 h-6 text-blue-600 mr-2" />
          <h3 className="text-xl font-bold text-gray-900">Processing Status</h3>
        </div>
        <div className="space-y-2">
          {displayResult.processing_status.map((status, index) => (
            <div key={index} className="flex items-center text-sm text-gray-700">
              <span className="text-green-500 mr-2">✓</span>
              {status}
            </div>
          ))}
        </div>
      </div>

      {/* Main Decision Card */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-6">
          <TrendingUp className="w-6 h-6 text-blue-600 mr-2" />
          <h2 className="text-2xl font-bold text-gray-900">Credit Decision</h2>
        </div>

        <div className={`p-6 rounded-lg border-2 ${getDecisionColor(displayResult.decision)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {getDecisionIcon(displayResult.decision)}
              <div className="ml-4">
                <h3 className="text-3xl font-bold">
                  {displayResult.decision}
                </h3>
                <p className="text-lg opacity-75">
                  Credit Score: {displayResult.credit_score}/100
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className={`text-4xl font-bold ${getRiskLevel(displayResult.credit_score).color}`}>
                {getRiskLevel(displayResult.credit_score).level}
              </div>
              <div className="text-sm opacity-75">Risk Level</div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Loan Limit</h4>
            <div className="text-2xl font-bold text-blue-600">
              ₹{displayResult.loan_limit.toLocaleString()}
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Risk Premium</h4>
            <div className="text-2xl font-bold text-orange-600">
              {displayResult.risk_premium_pct}%
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Fraud Score</h4>
            <div className="text-2xl font-bold text-red-600">
              {displayResult.fraud_analysis?.fraud_score}/100
            </div>
          </div>
        </div>
      </div>

      {/* Five Cs Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-4">
          <Shield className="w-6 h-6 text-blue-600 mr-2" />
          <h3 className="text-xl font-bold text-gray-900">Five Cs Analysis</h3>
        </div>

        <div className="space-y-4">
          {Object.entries(displayResult.five_cs).map(([key, value]) => (
            <div key={key} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-900 capitalize">{key}</h4>
                <span className={`text-2xl font-bold ${getScoreColor(value.score)}`}>
                  {value.score}/10
                </span>
              </div>
              <p className="text-gray-600 text-sm">{value.rationale}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Data Visualization Charts */}
      <div className="space-y-6">
        {/* 1. Radar Chart - Five Cs Distribution */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <BarChart3 className="w-6 h-6 text-purple-600 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">Five Cs Profile</h3>
            <span className="ml-auto text-sm text-gray-500">Radar Chart</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={[
              {
                name: 'Character',
                value: displayResult.five_cs.character.score,
                fullMark: 10
              },
              {
                name: 'Capacity',
                value: displayResult.five_cs.capacity.score,
                fullMark: 10
              },
              {
                name: 'Capital',
                value: displayResult.five_cs.capital.score,
                fullMark: 10
              },
              {
                name: 'Collateral',
                value: displayResult.five_cs.collateral.score,
                fullMark: 10
              },
              {
                name: 'Conditions',
                value: displayResult.five_cs.conditions.score,
                fullMark: 10
              }
            ]}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="name" stroke="#6b7280" />
              <PolarRadiusAxis angle={90} domain={[0, 10]} stroke="#9ca3af" />
              <Radar name="Score" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
              <Tooltip contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* 2. Bar Chart - Five Cs vs Credit Score Contribution */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <BarChart3 className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">Five Cs Impact Analysis</h3>
            <span className="ml-auto text-sm text-gray-500">Comparative Impact on Final Score</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              {
                name: 'Character',
                score: displayResult.five_cs.character.score,
                weighted: (displayResult.five_cs.character.score * 0.20).toFixed(2)
              },
              {
                name: 'Capacity',
                score: displayResult.five_cs.capacity.score,
                weighted: (displayResult.five_cs.capacity.score * 0.30).toFixed(2)
              },
              {
                name: 'Capital',
                score: displayResult.five_cs.capital.score,
                weighted: (displayResult.five_cs.capital.score * 0.20).toFixed(2)
              },
              {
                name: 'Collateral',
                score: displayResult.five_cs.collateral.score,
                weighted: (displayResult.five_cs.collateral.score * 0.15).toFixed(2)
              },
              {
                name: 'Conditions',
                score: displayResult.five_cs.conditions.score,
                weighted: (displayResult.five_cs.conditions.score * 0.15).toFixed(2)
              }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
              <Legend />
              <Bar dataKey="score" fill="#3b82f6" name="Raw Score (/10)" />
              <Bar dataKey="weighted" fill="#10b981" name="Weighted Contribution" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 3. Five Cs vs Credit Score Correlation */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-xl font-bold text-gray-900">C's Scores vs Credit Score</h3>
            <span className="ml-auto text-sm text-gray-500">Individual Component Analysis</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" dataKey="score" name="Individual C Score" stroke="#6b7280" />
              <YAxis type="number" dataKey="credit_impact" name="Credit Score Impact" stroke="#6b7280" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
              <Scatter name="Character" data={[{ score: displayResult.five_cs.character.score, credit_impact: displayResult.credit_score * 0.20, c_name: 'Character' }]} fill="#ff7c7c" />
              <Scatter name="Capacity" data={[{ score: displayResult.five_cs.capacity.score, credit_impact: displayResult.credit_score * 0.30, c_name: 'Capacity' }]} fill="#8884d8" />
              <Scatter name="Capital" data={[{ score: displayResult.five_cs.capital.score, credit_impact: displayResult.credit_score * 0.20, c_name: 'Capital' }]} fill="#82ca9d" />
              <Scatter name="Collateral" data={[{ score: displayResult.five_cs.collateral.score, credit_impact: displayResult.credit_score * 0.15, c_name: 'Collateral' }]} fill="#ffc658" />
              <Scatter name="Conditions" data={[{ score: displayResult.five_cs.conditions.score, credit_impact: displayResult.credit_score * 0.15, c_name: 'Conditions' }]} fill="#8dd1e1" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* 4. Five Cs vs Risk Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Five Cs vs Fraud Score */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <Shield className="w-6 h-6 text-red-600 mr-2" />
              <h3 className="text-lg font-bold text-gray-900">C's vs Fraud Risk</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { name: 'Character', five_c: displayResult.five_cs.character.score, fraud_inverse: 10 - (displayResult.fraud_analysis?.fraud_score || 0) / 10 },
                { name: 'Capacity', five_c: displayResult.five_cs.capacity.score, fraud_inverse: 10 - (displayResult.fraud_analysis?.fraud_score || 0) / 10 },
                { name: 'Capital', five_c: displayResult.five_cs.capital.score, fraud_inverse: 10 - (displayResult.fraud_analysis?.fraud_score || 0) / 10 },
                { name: 'Collateral', five_c: displayResult.five_cs.collateral.score, fraud_inverse: 10 - (displayResult.fraud_analysis?.fraud_score || 0) / 10 },
                { name: 'Conditions', five_c: displayResult.five_cs.conditions.score, fraud_inverse: 10 - (displayResult.fraud_analysis?.fraud_score || 0) / 10 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
                <Legend />
                <Bar dataKey="five_c" fill="#8b5cf6" name="C Score" />
                <Bar dataKey="fraud_inverse" fill="#ef4444" name="Fraud Safety" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Five Cs vs Risk Premium */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <TrendingUp className="w-6 h-6 text-orange-600 mr-2" />
              <h3 className="text-lg font-bold text-gray-900">C's vs Risk Premium</h3>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { 
                  name: 'Character', 
                  five_c: displayResult.five_cs.character.score, 
                  risk_premium: displayResult.risk_premium_pct 
                },
                { 
                  name: 'Capacity', 
                  five_c: displayResult.five_cs.capacity.score, 
                  risk_premium: displayResult.risk_premium_pct 
                },
                { 
                  name: 'Capital', 
                  five_c: displayResult.five_cs.capital.score, 
                  risk_premium: displayResult.risk_premium_pct 
                },
                { 
                  name: 'Collateral', 
                  five_c: displayResult.five_cs.collateral.score, 
                  risk_premium: displayResult.risk_premium_pct 
                },
                { 
                  name: 'Conditions', 
                  five_c: displayResult.five_cs.conditions.score, 
                  risk_premium: displayResult.risk_premium_pct 
                }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
                <Legend />
                <Bar dataKey="five_c" fill="#8b5cf6" name="C Score" />
                <Bar dataKey="risk_premium" fill="#f97316" name="Risk Premium %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 5. Five Cs vs Bank Metrics */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <Database className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">C's vs Financial Health</h3>
            <span className="ml-auto text-sm text-gray-500">Bank Balance Relationships</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { 
                name: 'Character', 
                five_c: displayResult.five_cs.character.score,
                avg_balance: (displayResult.bank_analysis?.avg_balance || 0) / 100000
              },
              { 
                name: 'Capacity', 
                five_c: displayResult.five_cs.capacity.score,
                avg_balance: (displayResult.bank_analysis?.avg_balance || 0) / 100000
              },
              { 
                name: 'Capital', 
                five_c: displayResult.five_cs.capital.score,
                avg_balance: (displayResult.bank_analysis?.avg_balance || 0) / 100000
              },
              { 
                name: 'Collateral', 
                five_c: displayResult.five_cs.collateral.score,
                avg_balance: (displayResult.bank_analysis?.avg_balance || 0) / 100000
              },
              { 
                name: 'Conditions', 
                five_c: displayResult.five_cs.conditions.score,
                avg_balance: (displayResult.bank_analysis?.avg_balance || 0) / 100000
              }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis yAxisId="left" stroke="#8b5cf6" />
              <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
              <Tooltip contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }} />
              <Legend />
              <Bar yAxisId="left" dataKey="five_c" fill="#8b5cf6" name="C Score" />
              <Bar yAxisId="right" dataKey="avg_balance" fill="#10b981" name="Avg Balance (₹100K)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 6. Overall Metrics Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white rounded-lg shadow-lg p-6">
          <div className="text-center">
            <div className="text-sm text-gray-600">Average C Score</div>
            <div className="text-2xl font-bold text-blue-600">
              {((displayResult.five_cs.character.score + 
                displayResult.five_cs.capacity.score + 
                displayResult.five_cs.capital.score + 
                displayResult.five_cs.collateral.score + 
                displayResult.five_cs.conditions.score) / 5).toFixed(1)}/10
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Highest C</div>
            <div className="text-2xl font-bold text-green-600">
              {Math.max(
                displayResult.five_cs.character.score,
                displayResult.five_cs.capacity.score,
                displayResult.five_cs.capital.score,
                displayResult.five_cs.collateral.score,
                displayResult.five_cs.conditions.score
              ).toFixed(1)}/10
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Lowest C</div>
            <div className="text-2xl font-bold text-red-600">
              {Math.min(
                displayResult.five_cs.character.score,
                displayResult.five_cs.capacity.score,
                displayResult.five_cs.capital.score,
                displayResult.five_cs.collateral.score,
                displayResult.five_cs.conditions.score
              ).toFixed(1)}/10
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600">Variance</div>
            <div className="text-2xl font-bold text-orange-600">
              {(Math.max(
                displayResult.five_cs.character.score,
                displayResult.five_cs.capacity.score,
                displayResult.five_cs.capital.score,
                displayResult.five_cs.collateral.score,
                displayResult.five_cs.conditions.score
              ) - Math.min(
                displayResult.five_cs.character.score,
                displayResult.five_cs.capacity.score,
                displayResult.five_cs.capital.score,
                displayResult.five_cs.collateral.score,
                displayResult.five_cs.conditions.score
              )).toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Fraud Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <Shield className="w-6 h-6 text-red-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Fraud Analysis</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Fraud Score:</span>
              <span className="font-semibold">{displayResult.fraud_analysis?.fraud_score}/100</span>
            </div>
            <div className="flex justify-between">
              <span>Total Flags:</span>
              <span className="font-semibold">{displayResult.fraud_analysis?.total_flags}</span>
            </div>
            <div className="flex justify-between">
              <span>High Severity:</span>
              <span className="font-semibold">{displayResult.fraud_analysis?.high_severity_count}</span>
            </div>
          </div>
        </div>

        {/* Bank Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <Database className="w-6 h-6 text-green-600 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Bank Analysis</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>Avg Balance:</span>
              <span className="font-semibold">₹{displayResult.bank_analysis?.avg_balance.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Inflow:</span>
              <span className="font-semibold">₹{displayResult.bank_analysis?.total_inflow.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Outflow:</span>
              <span className="font-semibold">₹{displayResult.bank_analysis?.total_outflow.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      {/* CAM PDF Download */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-blue-900">Credit Analysis Narrative & CAM PDF</h3>
          </div>
          {displayResult.cam_path && (
            <button
              onClick={() => {
                const filename = displayResult.cam_path?.split("\\").pop() || 'CAM_Report.pdf';
                window.location.href = `/api/download-cam/${encodeURIComponent(filename)}`;
              }}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download CAM PDF
            </button>
          )}
        </div>
        <p className="text-gray-700 leading-relaxed mt-4">{displayResult.narrative}</p>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium text-blue-900 mb-2">For Approval:</h4>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Set up automated monitoring</li>
              <li>• Schedule quarterly reviews</li>
              <li>• Consider graduated loan disbursement</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-900 mb-2">Risk Mitigation:</h4>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Maintain fraud monitoring</li>
              <li>• Regular financial statement reviews</li>
              <li>• Collateral valuation updates</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;