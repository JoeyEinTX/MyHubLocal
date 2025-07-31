import { useState } from 'react';
import { deviceAPI } from '../api';

export default function DeviceCard({ device, onDeviceUpdate }) {
  const [loading, setLoading] = useState(false);

  const toggleDevice = async () => {
    setLoading(true);
    try {
      const newAction = device.status === 'on' ? 'off' : 'on';
      await deviceAPI.controlDevice(device.id, newAction);
      
      // Update parent component with new status
      if (onDeviceUpdate) {
        onDeviceUpdate({ ...device, status: newAction });
      }
    } catch (err) {
      console.error('Failed to toggle device:', err);
      // Could add toast notification here in the future
    } finally {
      setLoading(false);
    }
  };

  const isOn = device.status === 'on';

  return (
    <div className="group rounded-lg shadow-md p-6 transition-all duration-300 hover:shadow-lg hover:scale-105 bg-card border border-border-secondary hover:border-primary cursor-pointer">
      <div className="flex flex-col items-center space-y-4">
        {/* Device Icon & Name */}
        <div className="text-center">
          <div className="w-12 h-12 mx-auto mb-3 bg-primary bg-opacity-10 rounded-full flex items-center justify-center">
            <span className="text-2xl">
              {device.type === 'light' ? '💡' : 
               device.type === 'switch' ? '🔌' : 
               device.type === 'sensor' ? '📡' : 
               device.type === 'thermostat' ? '🌡️' : 
               device.type === 'lock' ? '🔒' : 
               '📱'}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-text group-hover:text-primary transition-colors">
            {device.name}
          </h3>
        </div>
        
        {/* Device Type & Status Badge */}
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2 py-1 rounded-full uppercase tracking-wide bg-text-muted bg-opacity-20 text-text-secondary">
            {device.type || 'unknown'}
          </span>
          <span className={`text-xs px-3 py-1 rounded-full font-medium ${
            isOn 
              ? 'bg-success text-white'
              : 'bg-danger text-white'
          }`}>
            {isOn ? 'ON' : 'OFF'}
          </span>
        </div>

        {/* Status Indicator with Label */}
        <div className="flex items-center space-x-2">
          <div 
            className={`h-3 w-3 rounded-full transition-all duration-300 ${
              isOn 
                ? 'bg-success animate-pulse shadow-lg shadow-success/50'
                : 'bg-text-muted'
            }`}
          />
          <span className={`text-sm font-medium transition-colors ${
            isOn 
              ? 'text-success'
              : 'text-text-secondary'
          }`}>
            {isOn ? 'ACTIVE' : 'INACTIVE'}
          </span>
        </div>

        {/* Toggle Button */}
        <button
          onClick={toggleDevice}
          disabled={loading}
          className={`w-full px-4 py-3 rounded-md font-medium transition-all duration-200 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            loading 
              ? 'bg-text-muted text-text-secondary cursor-not-allowed'
              : isOn 
                ? 'bg-danger hover:opacity-90 focus:ring-danger hover:shadow-lg transform hover:scale-105 active:scale-95' 
                : 'bg-success hover:opacity-90 focus:ring-success hover:shadow-lg transform hover:scale-105 active:scale-95'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <span>{isOn ? 'Turn Off' : 'Turn On'}</span>
              <span>{isOn ? '⏹️' : '▶️'}</span>
            </div>
          )}
        </button>
        
        {/* Device ID - Subtle */}
        <div className="text-xs text-text-muted font-mono bg-background bg-opacity-50 px-2 py-1 rounded border">
          ID: {device.id}
        </div>
      </div>
    </div>
  );
}
