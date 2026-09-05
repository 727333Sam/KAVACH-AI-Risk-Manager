import React from 'react';
import { formatPercentage } from '../utils/formatters';

interface FalsePositiveTrackerProps {}

const FalsePositiveTracker: React.FC<FalsePositiveTrackerProps> = () => {
  // Mock data - in production, this would come from useRiskData hook
  const fpr = 0.0042; // 0.42%
  const threshold1 = 0.01; // 1% warning threshold
  const threshold2 = 0.02; // 2% critical threshold

  const getFPRStatus = (rate: number) => {
    if (rate > threshold2) return { label: 'Critical', color: 'red', bgColor: 'bg-red-50', borderColor: 'border-red-500' };
    if (rate > threshold1) return { label: 'Warning', color: 'amber', bgColor: 'bg-amber-50', borderColor: 'border-amber-500' };
    return { label: 'Optimal', color: 'green', bgColor: 'bg-green-50', borderColor: 'border-green-500' };
  };

  const status = getFPRStatus(fpr);
  const percentage = Math.min((fpr / threshold2) * 100, 100);

  return (
    <div className={`${status.bgColor} rounded-xl shadow-sm p-6 border-2 ${status.borderColor}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">False-Positive Monitor</h3>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${status.color}-100 text-${status.color}-800`}>
          {status.label}
        </span>
      </div>

      {/* Large FPR Display */}
      <div className="text-center mb-4">
        <div className={`text-4xl font-bold text-${status.color}-600`}>
          {formatPercentage(fpr)}
        </div>
        <p className="text-xs text-gray-500 mt-1">Current FPR</p>
      </div>

      {/* Visual Progress Bar */}
      <div className="space-y-2 mb-4">
        <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`absolute top-0 left-0 h-full bg-${status.color}-500 transition-all duration-500 ease-out`}
            style={{ width: `${percentage}%` }}
          ></div>
          {/* Warning threshold marker at 50% (1% FPR) */}
          <div className="absolute top-0 h-full border-l-2 border-amber-400" style={{ left: '50%' }}></div>
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>0%</span>
          <span className="text-amber-600">1% ⚠</span>
          <span className="text-red-600">2% 🚨</span>
        </div>
      </div>

      {/* Status Messages */}
      <div className="space-y-2">
        {fpr > threshold2 && (
          <div className="flex items-start text-xs text-red-800 bg-red-100 rounded p-2">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>Auto-downgrade activated. Review model thresholds immediately.</span>
          </div>
        )}
        {fpr > threshold1 && fpr <= threshold2 && (
          <div className="flex items-start text-xs text-amber-800 bg-amber-100 rounded p-2">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>FPR elevated. Monitor legitimate transactions closely.</span>
          </div>
        )}
        {fpr <= threshold1 && (
          <div className="flex items-start text-xs text-green-800 bg-green-100 rounded p-2">
            <svg className="w-4 h-4 mr-1 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>System performing within optimal parameters.</span>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-3 text-center">
          <div>
            <p className="text-xs text-gray-500">Last Hour</p>
            <p className={`text-lg font-semibold text-${status.color}-600`}>0.38%</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">24h Avg</p>
            <p className={`text-lg font-semibold text-${status.color}-600`}>0.45%</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FalsePositiveTracker;