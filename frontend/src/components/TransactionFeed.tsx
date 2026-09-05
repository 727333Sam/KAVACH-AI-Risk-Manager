import React, { useState } from 'react';
import { formatCurrency, formatRelativeTime } from '../utils/formatters';
import { getRiskBgColor, getRiskTextColor, getActionColor, getStatusColor } from '../utils/riskColors';
import RiskScoreCard from './RiskScoreCard';

export interface Transaction {
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

interface TransactionFeedProps {
  onSelectTransaction?: (transaction: Transaction | null) => void;
}

const TransactionFeed: React.FC<TransactionFeedProps> = ({ onSelectTransaction }) => {
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  // Mock data
  const transactions: Transaction[] = [
    {
      id: '1',
      transaction_id: 'txn_001',
      merchant_id: 'merchant_456',
      customer_id: 'cust_001',
      amount: 2500,
      card_bin: '512345',
      category: 'electronics',
      ip_address: '203.0.113.45',
      device_id: 'device_001',
      fraud_score: 23,
      chargeback_score: 15,
      return_score: 8,
      action: 'APPROVE',
      status: 'COMPLETED',
      timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
      customer_email: 'john@example.com',
      customer_name: 'John Doe',
    },
    {
      id: '2',
      transaction_id: 'txn_002',
      merchant_id: 'merchant_456',
      customer_id: 'cust_002',
      amount: 15000,
      card_bin: '411111',
      category: 'jewelry',
      ip_address: '198.51.100.12',
      device_id: 'device_002',
      fraud_score: 78,
      chargeback_score: 65,
      return_score: 45,
      action: 'HOLD',
      status: 'PENDING',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      customer_email: 'suspicious@email.com',
      customer_name: 'Unknown User',
    },
    {
      id: '3',
      transaction_id: 'txn_003',
      merchant_id: 'merchant_456',
      customer_id: 'cust_003',
      amount: 890,
      card_bin: '378282',
      category: 'clothing',
      ip_address: '192.0.2.100',
      device_id: 'device_003',
      fraud_score: 12,
      chargeback_score: 8,
      return_score: 25,
      action: 'APPROVE',
      status: 'COMPLETED',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      customer_email: 'regular@customer.com',
      customer_name: 'Jane Smith',
    },
    {
      id: '4',
      transaction_id: 'txn_004',
      merchant_id: 'merchant_456',
      customer_id: 'cust_004',
      amount: 45000,
      card_bin: '601100',
      category: 'electronics',
      ip_address: '203.0.113.100',
      device_id: 'device_004',
      fraud_score: 92,
      chargeback_score: 88,
      return_score: 72,
      action: 'BLOCK',
      status: 'BLOCKED',
      timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
      customer_email: 'fraudster@fake.com',
      customer_name: 'Suspicious Customer',
    },
    {
      id: '5',
      transaction_id: 'txn_005',
      merchant_id: 'merchant_456',
      customer_id: 'cust_005',
      amount: 1200,
      card_bin: '550000',
      category: 'groceries',
      ip_address: '10.0.0.55',
      device_id: 'device_005',
      fraud_score: 35,
      chargeback_score: 42,
      return_score: 18,
      action: 'FLAG',
      status: 'FLAGGED',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      customer_email: 'mary@email.com',
      customer_name: 'Mary Wilson',
    },
  ];

  const handleRowClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setExpandedRow(expandedRow === transaction.id ? null : transaction.id);
    onSelectTransaction?.(transaction);
  };

  const getRiskLevel = (score: number): 'low' | 'medium' | 'high' => {
    if (score < 50) return 'low';
    if (score < 70) return 'medium';
    return 'high';
  };

  const getMaxScore = (transaction: Transaction): number => {
    return Math.max(transaction.fraud_score, transaction.chargeback_score, transaction.return_score);
  };

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Real-Time Transaction Feed</h2>
            <div className="flex items-center space-x-2">
              <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                <span className="w-2 h-2 bg-green-600 rounded-full mr-1.5 animate-pulse"></span>
                Live
              </div>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Txn ID</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Amount</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Customer</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Time</th>
                <th className="px-6 py-3 text-center font-semibold text-gray-700">Fraud Score</th>
                <th className="px-6 py-3 text-center font-semibold text-gray-700">Chargeback</th>
                <th className="px-6 py-3 text-center font-semibold text-gray-700">Return</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Action</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {transactions.map((txn) => {
                const maxScore = getMaxScore(txn);

                return (
                  <React.Fragment key={txn.id}>
                    <tr
                      onClick={() => handleRowClick(txn)}
                      className={`hover:bg-gray-50 cursor-pointer transition-colors ${
                        selectedTransaction?.id === txn.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <td className="px-6 py-3 text-gray-900 font-mono text-xs">{txn.transaction_id}</td>
                      <td className="px-6 py-3 text-gray-900 font-semibold">{formatCurrency(txn.amount)}</td>
                      <td className="px-6 py-3 text-gray-700">
                        <div>
                          <p className="font-medium">{txn.customer_name}</p>
                          <p className="text-xs text-gray-500">{txn.customer_email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-3 text-gray-600 text-xs whitespace-nowrap">
                        {formatRelativeTime(txn.timestamp)}
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex justify-center">
                          <span
                            className={`inline-flex items-center justify-center w-12 h-8 rounded-md font-semibold text-xs ${getRiskBgColor(
                              txn.fraud_score
                            )} ${getRiskTextColor(txn.fraud_score)}`}
                          >
                            {txn.fraud_score.toFixed(0)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex justify-center">
                          <span
                            className={`inline-flex items-center justify-center w-12 h-8 rounded-md font-semibold text-xs ${getRiskBgColor(
                              txn.chargeback_score
                            )} ${getRiskTextColor(txn.chargeback_score)}`}
                          >
                            {txn.chargeback_score.toFixed(0)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <div className="flex justify-center">
                          <span
                            className={`inline-flex items-center justify-center w-12 h-8 rounded-md font-semibold text-xs ${getRiskBgColor(
                              txn.return_score
                            )} ${getRiskTextColor(txn.return_score)}`}
                          >
                            {txn.return_score.toFixed(0)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActionColor(txn.action)}`}>
                          {txn.action}
                        </span>
                      </td>
                      <td className="px-6 py-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(txn.status)}`}>
                          {txn.status}
                        </span>
                      </td>
                    </tr>
                    {expandedRow === txn.id && (
                      <tr className="bg-blue-50 border-b border-gray-200">
                        <td colSpan={9} className="px-6 py-4">
                          <RiskScoreCard transaction={txn} onClose={() => setExpandedRow(null)} />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-center text-xs text-gray-500">
          Showing 5 of 10500 transactions • Auto-refresh every 5 seconds
        </div>
      </div>

      {selectedTransaction && !expandedRow && (
        <div className="mt-4">
          <RiskScoreCard transaction={selectedTransaction} onClose={() => setSelectedTransaction(null)} />
        </div>
      )}
    </>
  );
};

export default TransactionFeed;