import React, { useState } from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface MetricsDashboardProps {}

const MetricsDashboard: React.FC<MetricsDashboardProps> = () => {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');

  // Generate mock data based on time range
  const generateMockData = () => {
    if (timeRange === '24h') {
      return Array.from({ length: 24 }, (_, i) => ({
        time: `${i}:00`,
        fraud_catch_rate: 75 + Math.random() * 20,
        fpr: 0.2 + Math.random() * 0.4,
        transactions: 400 + Math.floor(Math.random() * 200),
      }));
    } else if (timeRange === '7d') {
      return Array.from({ length: 7 }, (_, i) => ({
        time: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        fraud_catch_rate: 75 + Math.random() * 20,
        fpr: 0.2 + Math.random() * 0.4,
        transactions: 2800 + Math.floor(Math.random() * 1400),
      }));
    } else {
      return Array.from({ length: 30 }, (_, i) => ({
        time: `${i + 1}`,
        fraud_catch_rate: 75 + Math.random() * 20,
        fpr: 0.2 + Math.random() * 0.4,
        transactions: 2800 + Math.floor(Math.random() * 1400),
      }));
    }
  };

  const chartData = generateMockData();

  // Mock action breakdown data
  const actionData = [
    { name: 'ALERT', count: 1240, color: '#3b82f6' },
    { name: 'FLAG', count: 380, color: '#f59e0b' },
    { name: 'HOLD', count: 156, color: '#f97316' },
    { name: 'BLOCK', count: 42, color: '#ef4444' },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900 mb-1">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {typeof entry.value === 'number' && entry.name.includes('rate')
                ? `${(entry.value * 100).toFixed(2)}%`
                : entry.name === 'transactions'
                ? entry.value.toLocaleString()
                : entry.value.toFixed(1)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">Risk Metrics Dashboard</h2>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                timeRange === range
                  ? 'bg-brand-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fraud Catch Rate Chart */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Fraud Catch Rate</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    tickLine={false}
                    domain={[60, 100]}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="fraud_catch_rate"
                    name="Catch Rate"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* False Positive Rate Chart */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">False Positive Rate Trend</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="fprGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    tickLine={false}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    tickLine={false}
                    tickFormatter={(value) => `${(value * 100).toFixed(1)}%`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="fpr"
                    name="FPR"
                    stroke="#f59e0b"
                    strokeWidth={2}
                    fill="url(#fprGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Action Breakdown Chart */}
          <div className="bg-gray-50 rounded-lg p-4 lg:col-span-2">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Action Breakdown</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={actionData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
                  <XAxis
                    type="number"
                    tick={{ fontSize: 11, fill: '#6b7280' }}
                    tickLine={false}
                    tickFormatter={(value) => value.toLocaleString()}
                  />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fontSize: 12, fill: '#374151' }}
                    tickLine={false}
                    axisLine={false}
                    width={60}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar
                    dataKey="count"
                    name="Actions"
                    radius={[0, 4, 4, 0]}
                    barSize={32}
                  >
                    {actionData.map((entry, index) => (
                      <rect key={`bar-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-500">Avg Catch Rate</p>
              <p className="text-2xl font-bold text-green-600 mt-1">82.4%</p>
              <p className="text-xs text-green-600">+3.2% vs last period</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Avg FPR</p>
              <p className="text-2xl font-bold text-amber-600 mt-1">0.42%</p>
              <p className="text-xs text-amber-600">-0.08% vs last period</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Total Actions</p>
              <p className="text-2xl font-bold text-brand-600 mt-1">1,818</p>
              <p className="text-xs text-gray-500">In selected period</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500">Block Rate</p>
              <p className="text-2xl font-bold text-red-600 mt-1">2.3%</p>
              <p className="text-xs text-gray-500">Of total transactions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;