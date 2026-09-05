/**
 * Get color based on risk score
 * 0-50: low risk (green)
 * 50-70: medium risk (yellow)
 * 70-100: high risk (red)
 */
export const getRiskColor = (score: number): string => {
  if (score < 50) return 'risk-low';
  if (score < 70) return 'risk-medium';
  return 'risk-high';
};

/**
 * Get background color class based on risk score
 */
export const getRiskBgColor = (score: number): string => {
  if (score < 50) return 'bg-green-100';
  if (score < 70) return 'bg-amber-100';
  return 'bg-red-100';
};

/**
 * Get text color class based on risk score
 */
export const getRiskTextColor = (score: number): string => {
  if (score < 50) return 'text-green-800';
  if (score < 70) return 'text-amber-800';
  return 'text-red-800';
};

/**
 * Get action color based on action type
 */
export const getActionColor = (action: string): string => {
  const actions: Record<string, string> = {
    ALERT: 'bg-blue-100 text-blue-800',
    FLAG: 'bg-amber-100 text-amber-800',
    HOLD: 'bg-orange-100 text-orange-800',
    BLOCK: 'bg-red-100 text-red-800',
    APPROVE: 'bg-green-100 text-green-800',
    DECLINE: 'bg-red-100 text-red-800',
    REVIEW: 'bg-gray-100 text-gray-800',
  };
  return actions[action] || 'bg-gray-100 text-gray-800';
};

/**
 * Get status color based on status
 */
export const getStatusColor = (status: string): string => {
  const statusMap: Record<string, string> = {
    COMPLETED: 'bg-green-100 text-green-800',
    PENDING: 'bg-amber-100 text-amber-800',
    BLOCKED: 'bg-red-100 text-red-800',
    FLAGGED: 'bg-orange-100 text-orange-800',
    PROCESSING: 'bg-blue-100 text-blue-800',
  };
  return statusMap[status] || 'bg-gray-100 text-gray-800';
};