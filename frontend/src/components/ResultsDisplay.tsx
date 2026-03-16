import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, TrendingUp, FileText, Shield, Database, BarChart3, Download } from 'lucide-react';

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