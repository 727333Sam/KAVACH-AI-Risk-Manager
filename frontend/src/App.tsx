import React, { useState } from 'react';
import { Transaction } from './components/TransactionFeed';
import RiskOverview from './components/RiskOverview';
import TransactionFeed from './components/TransactionFeed';
import MerchantConfig from './components/MerchantConfig';
import MetricsDashboard from './components/MetricsDashboard';
import FalsePositiveTracker from './components/FalsePositiveTracker';

function App() {
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Risk Manager</h1>
              <p className="text-sm text-gray-600">Real-time transaction monitoring & fraud detection</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <span className="font-medium">Merchant ID:</span>
                <span className="ml-2 text-brand-600 font-mono">merchant_456</span>
              </div>
              <button className="px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors">
                Config Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Top section - Overview and FPR Tracker */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          <div className="lg:col-span-3">
            <RiskOverview />
          </div>
          <div>
            <FalsePositiveTracker />
          </div>
        </div>

        {/* Metrics Dashboard */}
        <div className="mb-6">
          <MetricsDashboard />
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left - Transactions Feed */}
          <div className="lg:col-span-2">
            <TransactionFeed onSelectTransaction={setSelectedTransaction} />
          </div>

          {/* Right - Merchant Config */}
          <div>
            <MerchantConfig />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 border-t bg-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-sm text-gray-500">
          <p>AI Risk Manager v1.0 • Razorpay Hackathon Project • Real-time monitoring powered by ML engines</p>
        </div>
      </footer>
    </div>
  );
}

export default App;