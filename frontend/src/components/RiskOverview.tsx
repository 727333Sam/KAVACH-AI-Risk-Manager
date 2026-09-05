import React from 'react';
import { formatNumber, formatPercentage } from '../utils/formatters';
import { getRiskColor, getRiskBgColor, getRiskTextColor } from '../utils/riskColors';

interface RiskOverviewProps {}

interface RiskMetrics {
  fraud_alerts_today: number;
  fraud_alerts_trend: number;
  chargebacks_prevented: number;
  chargebacks_prevented_percentage: number;
  false_positive_rate: number;
  transactions_today: number;
}

const RiskOverview: React.FC<RiskOverviewProps> = () => {
  // Mock data for development
  const metrics: RiskMetrics = {
    fraud_alerts_today: 42,
    fraud_alerts_trend: 12.5,
    chargebacks_prevented: 15,
    chargebacks_prevented_percentage: 89.3,
    false_positive_rate: 0.0042,
    transactions_today: 10500,
  };

  const FraudAlertsCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500">Fraud Alerts Today</p>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">{formatNumber(metrics.fraud_alerts_today)}</h3>
          <div className={`flex items-center mt-2 ${metrics.fraud_alerts_trend >= 0 ? 'text-red-600' : 'text-green-600'}`}>
            <span className="text-sm font-medium">
              {metrics.fraud_alerts_trend >= 0 ? '+' : ''}{metrics.fraud_alerts_trend}%
            </span>
            <span className="text-sm text-gray-500 ml-1">vs yesterday</span>
          </div>
        </div>
        <div className={`p-3 rounded-lg ${metrics.fraud_alerts_trend >= 0 ? 'bg-red-100' : 'bg-green-100'}`}>
          {metrics.fraud_alerts_trend >= 0 ? (
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
          )}
        </div>
      </div>
    </div>
  );

  const ChargebacksPreventedCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500">Chargebacks Prevented</p>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">{formatNumber(metrics.chargebacks_prevented)}</h3>
          <p className="text-sm text-green-600 font-medium mt-2">
            {formatPercentage(metrics.chargebacks_prevented_percentage)} of potential losses avoided
          </p>
        </div>
        <div className="p-3 rounded-lg bg-blue-100">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    </div>
  );

  const FalsePositiveRateCard = () => {
    const fpr = metrics.false_positive_rate;
    const riskLevel = fpr > 0.01 ? 'high' : fpr > 0.005 ? 'medium' : 'low';
    const riskColors = getRiskColor(fpr);
    const riskBg = getRiskBgColor(fpr);
    const riskText = getRiskTextColor(fpr);

    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-sm font-medium text-gray-500">False-Positive Rate</p>
            <h3 className={`text-3xl font-bold mt-2 ${riskText.replace('text-', '')}`}>
              {formatPercentage(fpr)}
            </h3>
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-2 ${riskBg} ${riskText}`}>
              {fpr > 0.01 ? 'Warning' : fpr > 0.005 ? 'Monitoring' : 'Optimal'}
            </div>
          </div>
          <div className={`p-3 rounded-lg ${riskBg}`}>
            <svg className={`w-6 h-6 ${riskText.replace('text-', 'text-')}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
            </svg>
          </div>
        </div>
      </div>
    );
  };

  const TransactionsProcessedCard = () => (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-gray-500">Transactions Processed Today</p>
          <h3 className="text-3xl font-bold text-brand-600 mt-2">{formatNumber(metrics.transactions_today)}</h3>
          <div className="flex items-center mt-2">
            <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-brand-600 rounded-full" style={{ width: '75%' }}></div>
            </div>
            <span className="text-sm text-gray-500 ml-3">75%</span>
          </div>
        </div>
        <div className="p-3 rounded-lg bg-purple-100">
          <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      </div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <FraudAlertsCard />
      <ChargebacksPreventedCard />
      <FalsePositiveRateCard />
      <TransactionsProcessedCard />
    </div>
  );
};

export default RiskOverview;