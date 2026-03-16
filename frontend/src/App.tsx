import { useState } from 'react';
import { CreditCard } from 'lucide-react';
import CreditForm from './components/CreditForm';
import ResultsDisplay, { ProcessingResult } from './components/ResultsDisplay';

function App() {
  const [hasResult, setHasResult] = useState(false);
  const [latestResult, setLatestResult] = useState<ProcessingResult | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <CreditCard className="w-12 h-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">Credit Engine</h1>
          </div>
          <p className="text-xl text-gray-600">AI-Powered Credit Scoring System</p>
        </div>

        {/* Content */}
        {!hasResult ? (
          <CreditForm
            onSuccess={(result) => {
              setLatestResult(result);
              setHasResult(true);
            }}
          />
        ) : (
          <ResultsDisplay result={latestResult} />
        )}
      </div>
    </div>
  );
}

export default App;