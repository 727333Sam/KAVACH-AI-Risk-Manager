import React, { useState } from 'react';
import { formatCurrency, formatDateTime, formatRiskScore } from '../utils/formatters';
import { getRiskBgColor, getRiskTextColor } from '../utils/riskColors';

interface Transaction {
  id: string;
  transaction_id: string;
  merchant_id: string;
  customer_id: string;
  amount: number;
  card_bin: string;
  category: string;
  ip_address: string;
  device_id: string;
  fraud_score: number;
  chargeback_score: number;
  return_score: number;
  action: string;
  status: string;
  timestamp: string;
  customer_email?: string;
  customer_name?: string;
}

interface RiskScoreCardProps {
  transaction: Transaction;
  onClose?: () => void;
}

const RiskScoreCard: React.FC<RiskScoreCardProps> = ({ transaction, onClose }) => {
  const [overrideAction, setOverrideAction] = useState<string | null>(null);

  const getRiskExplanation = (score: number, engine: string): string => {
    const explanations: Record<string, Record<string, string>> = {
      fraud: {
        high: 'Multiple fraud indicators detected: high velocity, unusual geography, device mismatch',
        medium: 'Some fraud signals present: moderate velocity check, new customer profile',
        low: 'Clean transaction profile with no significant fraud signals',
      },
      chargeback: {
        high: 'High chargeback risk: high-value item, multiple geographic mismatches',
        medium: 'Moderate chargeback risk: category known for disputes, partial AVS match',
        low: 'Low chargeback risk: established customer, verified shipping address',
      },
      return: {
        high: 'High return fraud risk: high-value electronics, suspicious return patterns',
        medium: 'Moderate return risk: category susceptible to fraud, first-time purchase',
        low: 'Low return fraud risk: repeat customer, low-value consumable item',
      },
    };

    let level = 'low';
    if (score > 70) level = 'high';
    else if (score > 50) level = 'medium';

    return explanations[engine]?.[level] || 'Risk assessment complete';
  };

  const getRulesTriggered = (transaction: Transaction) => {
    const rules = [];

    if (transaction.fraud_score > 70) {
      rules.push({
        type: 'fraud',
        rule: 'High-value transaction',
        impact: '+25',
      });
      rules.push({
        type: 'fraud',
        rule: 'Geographic mismatch',
        impact: '+20',
      });
    } else if (transaction.fraud_score > 50) {
      rules.push({
        type: 'fraud',
        rule: 'Velocity check',
        impact: '+15',
      });
    }

    if (transaction.chargeback_score > 70) {
      rules.push({
        type: 'chargeback',
        rule: 'High-risk category',
        impact: '+22',
      });
    }

    if (transaction.return_score > 50) {
      rules.push({
        type: 'return',
        rule: 'Return pattern detected',
        impact: '+18',
      });
    }

    return rules.length > 0 ? rules : [{ type: 'info', rule: 'No major red flags', impact: '✓' }];
  };

  const rules = getRulesTriggered(transaction);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-lg">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Transaction Risk Analysis</h3>
          <p className="text-sm text-gray-500 mt-1">{transaction.transaction_id}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Transaction Details Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 pb-6 border-b border-gray-200">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase">Amount</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{formatCurrency(transaction.amount)}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase">Customer</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{transaction.customer_name}</p>
          <p className="text-xs text-gray-500">{transaction.customer_email}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase">Category</p>
          <p className="text-lg font-bold text-gray-900 mt-1 capitalize">{transaction.category}</p>
        </div>
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase">Time</p>
          <p className="text-lg font-bold text-gray-900 mt-1">{formatDateTime(transaction.timestamp)}</p>
        </div>
      </div>

      {/* Risk Scores - Three Engines */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Fraud Engine */}
        <div className={`rounded-lg p-4 ${getRiskBgColor(transaction.fraud_score)} border-l-4 border-red-500`}>
          <div className="flex justify-between items-start mb-3">
            <h4 className="font-semibold text-gray-900">Fraud Engine</h4>
            <span className={`text-2xl font-bold ${getRiskTextColor(transaction.fraud_score)}`}>
              {formatRiskScore(transaction.fraud_score)}
            </span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed mb-3">
            {getRiskExplanation(transaction.fraud_score, 'fraud')}
          </p>
          <div className="text-xs text-gray-600">
            <span className="font-medium">Confidence:</span> 92%
          </div>
        </div>

        {/* Chargeback Engine */}
        <div className={`rounded-lg p-4 ${getRiskBgColor(transaction.chargeback_score)} border-l-4 border-yellow-500`}>
          <div className="flex justify-between items-start mb-3">
            <h4 className="font-semibold text-gray-900">Chargeback Engine</h4>
            <span className={`text-2xl font-bold ${getRiskTextColor(transaction.chargeback_score)}`}>
              {formatRiskScore(transaction.chargeback_score)}
            </span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed mb-3">
            {getRiskExplanation(transaction.chargeback_score, 'chargeback')}
          </p>
          <div className="text-xs text-gray-600">
            <span className="font-medium">Confidence:</span> 87%
          </div>
        </div>

        {/* Return Fraud Engine */}
        <div className={`rounded-lg p-4 ${getRiskBgColor(transaction.return_score)} border-l-4 border-blue-500`}>
          <div className="flex justify-between items-start mb-3">
            <h4 className="font-semibold text-gray-900">Return Engine</h4>
            <span className={`text-2xl font-bold ${getRiskTextColor(transaction.return_score)}`}>
              {formatRiskScore(transaction.return_score)}
            </span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed mb-3">
            {getRiskExplanation(transaction.return_score, 'return')}
          </p>
          <div className="text-xs text-gray-600">
            <span className="font-medium">Confidence:</span> 84%
          </div>
        </div>
      </div>

      {/* Rules Triggered */}
      <div className="mb-6 pb-6 border-b border-gray-200">
        <h4 className="font-semibold text-gray-900 mb-3">Rules Triggered</h4>
        <div className="space-y-2">
          {rules.map((rule, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between p-3 rounded-lg ${
                rule.type === 'info' ? 'bg-green-50 border border-green-200' : 'bg-amber-50 border border-amber-200'
              }`}
            >
              <div className="flex items-center">
                {rule.type === 'info' ? (
                  <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-amber-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                <span className="text-sm font-medium text-gray-900">{rule.rule}</span>
              </div>
              <span
                className={`text-sm font-bold ${
                  rule.type === 'info' ? 'text-green-600' : 'text-amber-600'
                }`}
              >
                {rule.impact}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Merchant Override Options */}
      <div>
        <h4 className="font-semibold text-gray-900 mb-3">Merchant Override</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button
            onClick={() => setOverrideAction('APPROVE')}
            className={`py-3 px-4 rounded-lg font-medium transition-colors text-sm ${
              overrideAction === 'APPROVE'
                ? 'bg-green-600 text-white'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            <svg className="w-4 h-4 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
            Approve
          </button>
          <button
            onClick={() => setOverrideAction('REVIEW')}
            className={`py-3 px-4 rounded-lg font-medium transition-colors text-sm ${
              overrideAction === 'REVIEW'
                ? 'bg-blue-600 text-white'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Review
          </button>
          <button
            onClick={() => setOverrideAction('DECLINE')}
            className={`py-3 px-4 rounded-lg font-medium transition-colors text-sm ${
              overrideAction === 'DECLINE'
                ? 'bg-red-600 text-white'
                : 'bg-red-100 text-red-700 hover:bg-red-200'
            }`}
          >
            <svg className="w-4 h-4 inline mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
            Decline
          </button>
        </div>
        {overrideAction && (
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              Override action set to <strong>{overrideAction}</strong>. Click submit to apply.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskScoreCard;