import React, { useState } from 'react';

interface EngineConfig {
  enabled: boolean;
  threshold: number;
  action_mode: 'ALERT' | 'FLAG' | 'HOLD' | 'BLOCK';
}

interface MerchantConfigData {
  merchant_id: string;
  fraud_engine: EngineConfig;
  chargeback_engine: EngineConfig;
  return_engine: EngineConfig;
}

const MerchantConfig: React.FC = () => {
  const [config, setConfig] = useState<MerchantConfigData>({
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
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleToggle = (engine: keyof Omit<MerchantConfigData, 'merchant_id'>) => {
    setConfig((prev) => ({
      ...prev,
      [engine]: {
        ...prev[engine],
        enabled: !prev[engine].enabled,
      },
    }));
    setSaveSuccess(false);
  };

  const handleThresholdChange = (engine: keyof Omit<MerchantConfigData, 'merchant_id'>, value: number) => {
    setConfig((prev) => ({
      ...prev,
      [engine]: {
        ...prev[engine],
        threshold: value,
      },
    }));
    setSaveSuccess(false);
  };

  const handleActionModeChange = (engine: keyof Omit<MerchantConfigData, 'merchant_id'>, mode: EngineConfig['action_mode']) => {
    setConfig((prev) => ({
      ...prev,
      [engine]: {
        ...prev[engine],
        action_mode: mode,
      },
    }));
    setSaveSuccess(false);
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setSaveSuccess(true);
    // In production: await axios.post(`${API_BASE_URL}/config`, config);
  };

  const engines: Array<{
    key: keyof Omit<MerchantConfigData, 'merchant_id'>;
    label: string;
    description: string;
    color: string;
    icon: JSX.Element;
  }> = [
    {
      key: 'fraud_engine',
      label: 'Fraud Engine',
      description: 'Detects fraudulent transactions',
      color: 'red',
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      ),
    },
    {
      key: 'chargeback_engine',
      label: 'Chargeback Engine',
      description: 'Prevents chargeback fraud',
      color: 'amber',
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm0 14a6 6 0 110-12 6 6 0 010 12z" />
        </svg>
      ),
    },
    {
      key: 'return_engine',
      label: 'Return Engine',
      description: 'Prevents return fraud',
      color: 'blue',
      icon: (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
        </svg>
      ),
    },
  ];

  const actionModes: EngineConfig['action_mode'][] = ['ALERT', 'FLAG', 'HOLD', 'BLOCK'];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Merchant Configuration</h2>
        <p className="text-sm text-gray-500 mt-1">Configure risk engine thresholds and actions</p>
      </div>

      <div className="p-6 space-y-6">
        {engines.map((engine) => (
          <div key={engine.key} className="border border-gray-200 rounded-lg p-4">
            {/* Header - Toggle */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg bg-${engine.color}-100 text-${engine.color}-600 mr-3`}>
                  {engine.icon}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{engine.label}</h3>
                  <p className="text-xs text-gray-500">{engine.description}</p>
                </div>
              </div>
              <button
                onClick={() => handleToggle(engine.key)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  config[engine.key].enabled ? `bg-${engine.color}-600` : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    config[engine.key].enabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Threshold Slider */}
            <div className={`mb-4 ${!config[engine.key].enabled && 'opacity-50 pointer-events-none'}`}>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium text-gray-700">Threshold</label>
                <span className="text-sm font-mono text-gray-900 bg-gray-100 px-2 py-0.5 rounded">
                  {(config[engine.key].threshold * 100).toFixed(0)}%
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="90"
                value={config[engine.key].threshold * 100}
                onChange={(e) => handleThresholdChange(engine.key, parseInt(e.target.value) / 100)}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>50% (Sensitive)</span>
                <span>90% (Strict)</span>
              </div>
            </div>

            {/* Action Mode Dropdown */}
            <div className={!config[engine.key].enabled ? 'opacity-50 pointer-events-none' : ''}>
              <label className="text-sm font-medium text-gray-700 block mb-2">Action Mode</label>
              <div className="grid grid-cols-4 gap-2">
                {actionModes.map((mode) => (
                  <button
                    key={mode}
                    onClick={() => handleActionModeChange(engine.key, mode)}
                    className={`py-2 px-3 text-xs font-medium rounded-lg border transition-colors ${
                      config[engine.key].action_mode === mode
                        ? `bg-${engine.color}-600 text-white border-${engine.color}-600`
                        : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            isSaving
              ? 'bg-gray-400 cursor-not-allowed'
              : saveSuccess
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-brand-600 hover:bg-brand-700'
          } text-white`}
        >
          {isSaving ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </span>
          ) : saveSuccess ? (
            <span className="flex items-center justify-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Configuration Saved
            </span>
          ) : (
            'Save Configuration'
          )}
        </button>
      </div>
    </div>
  );
};

export default MerchantConfig;