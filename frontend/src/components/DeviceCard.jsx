import { useState } from 'react';
import { deviceAPI } from '../api';

export default function DeviceCard({ device, onDeviceUpdate, onRemoveDevice }) {
  const [loading, setLoading] = useState(false);
  const [removing, setRemoving] = useState(false);

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

  const removeDevice = async (e) => {
    e.stopPropagation(); // Prevent triggering card hover effects
    
    if (!confirm(`Are you sure you want to remove "${device.name}"?`)) {
      return;
    }

    setRemoving(true);
    try {
      await deviceAPI.removeDevice(device.id);
      
      // Notify parent component
      if (onRemoveDevice) {
        onRemoveDevice(device.id);
      }
    } catch (err) {
      console.error('Failed to remove device:', err);
      alert('Failed to remove device. Please try again.');
    } finally {
      setRemoving(false);
    }
  };

  const isOn = device.status === 'on';

  return (
    <div className="group relative rounded-xl shadow-md hover:shadow-lg p-6 transition-all duration-300 hover:scale-[1.02] bg-card border border-border-secondary hover:border-primary cursor-pointer">
      {/* Remove Button */}
      <button
        onClick={removeDevice}
        disabled={removing || loading}
        className={`absolute top-3 right-3 w-7 h-7 rounded-full flex items-center justify-center transition-all duration-200 z-10 ${
          removing 
            ? 'bg-text-muted text-text-secondary cursor-not-allowed'
            : 'bg-danger bg-opacity-10 text-danger hover:bg-danger hover:text-white opacity-0 group-hover:opacity-100 hover:scale-110'
        }`}
        title="Remove device"
      >
        {removing ? (
          <div className="w-3 h-3 border border-text-secondary border-t-transparent rounded-full animate-spin"></div>
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
      </button>

      <div className="flex flex-col items-center space-y-5">
        {/* Device Icon & Name */}
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary bg-opacity-10 rounded-2xl flex items-center justify-center shadow-sm">
            <span className="text-3xl">
              {device.type === 'light' ? '💡' : 
               device.type === 'switch' ? '🔌' : 
               device.type === 'sensor' ? '📡' : 
               device.type === 'thermostat' ? '🌡️' : 
               device.type === 'lock' ? '🔒' : 
               '📱'}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-text group-hover:text-primary transition-colors tracking-wide">
            {device.name}
          </h3>
        </div>
        
        {/* Device Type & Status Badge */}
        <div className="flex items-center space-x-3">
          <span className="text-xs px-3 py-1.5 rounded-full uppercase tracking-wider font-medium bg-text-muted bg-opacity-20 text-text-muted">
            {device.type || 'unknown'}
          </span>
          <span className={`text-xs px-3 py-1.5 rounded-full font-semibold tracking-wide ${
            isOn 
              ? 'bg-success text-white shadow-sm'
              : 'bg-danger text-white shadow-sm'
          }`}>
            {isOn ? 'ON' : 'OFF'}
          </span>
        </div>

        {/* Status Indicator with Label */}
        <div className="flex items-center space-x-3">
          <div 
            className={`h-3 w-3 rounded-full transition-all duration-300 ${
              isOn 
                ? 'bg-success animate-pulse shadow-lg shadow-success/50'
                : 'bg-text-muted'
            }`}
          />
          <span className={`text-sm font-medium transition-colors tracking-wide ${
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
          className={`w-full px-6 py-3 rounded-lg font-semibold transition-all duration-200 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 tracking-wide ${
            loading 
              ? 'bg-text-muted text-text-secondary cursor-not-allowed'
              : isOn 
                ? 'bg-danger hover:brightness-110 focus:ring-danger hover:shadow-lg transform hover:scale-[1.02] active:scale-95' 
                : 'bg-success hover:brightness-110 focus:ring-success hover:shadow-lg transform hover:scale-[1.02] active:scale-95'
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
        <div className="text-xs text-text-muted font-mono bg-background bg-opacity-50 px-3 py-1.5 rounded-lg border border-border-secondary">
          ID: {device.id}
        </div>
      </div>
    </div>
  );
}
