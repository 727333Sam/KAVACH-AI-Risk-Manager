import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Transaction interfaces
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

export interface RiskMetrics {
  fraud_alerts_today: number;
  fraud_alerts_trend: number; // percentage change
  chargebacks_prevented: number;
  chargebacks_prevented_percentage: number;
  false_positive_rate: number;
  transactions_today: number;
}

export interface EngineConfig {
  enabled: boolean;
  threshold: number;
  action_mode: 'ALERT' | 'FLAG' | 'HOLD' | 'BLOCK';
}

export interface MerchantConfig {
  merchant_id: string;
  fraud_engine: EngineConfig;
  chargeback_engine: EngineConfig;
  return_engine: EngineConfig;
}

interface MetricsHistory {
  timestamp: string;
  fraud_catch_rate: number;
  false_positive_rate: number;
  transactions: number;
}

// Mock data for development
const mockTransactions: Transaction[] = [
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

const mockMetrics: RiskMetrics = {
  fraud_alerts_today: 42,
  fraud_alerts_trend: 12.5,
  chargebacks_prevented: 15,
  chargebacks_prevented_percentage: 89.3,
  false_positive_rate: 0.0042,
  transactions_today: 10500,
};

const mockMetricsHistory: MetricsHistory[] = Array.from({ length: 24 }, (_, i) => ({
  timestamp: new Date(Date.now() - 1000 * 60 * 60 * (23 - i)).toISOString(),
  fraud_catch_rate: 75 + Math.random() * 20,
  false_positive_rate: 0.002 + Math.random() * 0.004,
  transactions: 400 + Math.floor(Math.random() * 200),
}));

const mockMerchantConfig: MerchantConfig = {
  merchant_id: 'merchant_456',
  fraud_engine: {
    enabled: true,
    threshold: 0.7,
    action_mode: 'ALERT',
  },
  chargeback_engine: {
    enabled: true,
    threshold: 0.65,
    action_mode: 'HOLD',
  },
  return_engine: {
    enabled: true,
    threshold: 0.6,
    action_mode: 'FLAG',
  },
};

export const useRiskData = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [metrics, setMetrics] = useState<RiskMetrics | null>(null);
  const [config, setConfig] = useState<MerchantConfig | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<MetricsHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTransactions = useCallback(async () => {
    try {
      // Using mock data for development
      // In production: const response = await axios.get(`${API_BASE_URL}/dashboard/transactions`);
      setTransactions(mockTransactions);
    } catch (e) {
      console.error('Failed to fetch transactions:', e);
      setTransactions(mockTransactions);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      // Using mock data for development
      // In production: const response = await axios.get(`${API_BASE_URL}/dashboard/metrics`);
      setMetrics(mockMetrics);
    } catch (e) {
      console.error('Failed to fetch metrics:', e);
      setMetrics(mockMetrics);
    }
  }, []);

  const fetchConfig = useCallback(async () => {
    try {
      // Using mock data for development
      setConfig(mockMerchantConfig);
    } catch (e) {
      console.error('Failed to fetch config:', e);
      setConfig(mockMerchantConfig);
    }
  }, []);

  const fetchMetricsHistory = useCallback(async () => {
    try {
      // Using mock data for development
      setMetricsHistory(mockMetricsHistory);
    } catch (e) {
      console.error('Failed to fetch metrics history:', e);
      setMetricsHistory(mockMetricsHistory);
    }
  }, []);

  const updateConfig = useCallback(async (newConfig: MerchantConfig) => {
    try {
      // In production: await axios.post(`${API_BASE_URL}/config`, newConfig);
      setConfig(newConfig);
      return true;
    } catch (e) {
      console.error('Failed to update config:', e);
      return false;
    }
  }, []);

  const scoreTransaction = useCallback(async (transactionData: Partial<Transaction>) => {
    try {
      // In production: const response = await axios.post(`${API_BASE_URL}/risk/score`, transactionData);
      const mockScore = {
        fraud_score: Math.random() * 100,
        chargeback_score: Math.random() * 100,
        return_score: Math.random() * 100,
        action: 'ALERT',
        confidence: 0.85,
      };
      return mockScore;
    } catch (e) {
      console.error('Failed to score transaction:', e);
      return null;
    }
  }, []);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchTransactions(),
        fetchMetrics(),
        fetchConfig(),
        fetchMetricsHistory(),
      ]);
      setLoading(false);
    };

    fetchAll();
  }, [fetchTransactions, fetchMetrics, fetchConfig, fetchMetricsHistory]);

  return {
    transactions,
    metrics,
    config,
    metricsHistory,
    loading,
    error,
    fetchTransactions,
    fetchMetrics,
    updateConfig,
    scoreTransaction,
  };
};

export default useRiskData;