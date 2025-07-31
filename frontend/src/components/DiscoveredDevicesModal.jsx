import { useState, useEffect } from 'react';

/**
 * Modal component that displays discovered devices with options to add them to the hub
 * @param {boolean} isOpen - Controls modal visibility
 * @param {function} onClose - Function to close the modal
 * @param {array} discoveredDevices - Array of discovered devices
 * @param {function} onAddDevice - Function to add a device to the hub
 * @param {function} onRescan - Function to trigger a new device scan
 * @param {Set} addingDevices - Set of device IDs currently being added
 * @param {object} scanSummary - Summary information about the last scan
 * @param {boolean} isRescanning - Whether a rescan is currently in progress
 */
export function DiscoveredDevicesModal({
  isOpen,
  onClose,
  discoveredDevices = [],
  onAddDevice,
  onRescan,
  addingDevices = new Set(),
  scanSummary = null,
  isRescanning = false
}) {
  const [isClosing, setIsClosing] = useState(false);
  const [deviceStates, setDeviceStates] = useState({}); // Track individual device animation states
  
  // Handle modal opening/closing animations
  useEffect(() => {
    if (isOpen) {
      setIsClosing(false);
      // Reset device states when modal opens
      setDeviceStates({});
    }
  }, [isOpen]);

  if (!isOpen && !isClosing) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const handleClose = () => {
    setIsClosing(true);
    // Wait for exit animation to complete before actually closing
    setTimeout(() => {
      onClose();
      setIsClosing(false);
    }, 300);
  };

  // Enhanced device addition with visual feedback
  const handleAddDevice = async (device) => {
    try {
      // Set loading state
      setDeviceStates(prev => ({
        ...prev,
        [device.id]: { state: 'loading' }
      }));

      await onAddDevice(device);
      
      // Show success animation
      setDeviceStates(prev => ({
        ...prev,
        [device.id]: { state: 'success' }
      }));

      // Clear state after animation
      setTimeout(() => {
        setDeviceStates(prev => {
          const newStates = { ...prev };
          delete newStates[device.id];
          return newStates;
        });
      }, 1500);

    } catch (error) {
      // Show error animation
      setDeviceStates(prev => ({
        ...prev,
        [device.id]: { state: 'error' }
      }));

      // Clear error state after animation
      setTimeout(() => {
        setDeviceStates(prev => ({
          ...prev,
          [device.id]: { state: 'idle' }
        }));
      }, 1000);
    }
  };

  const formatDuration = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div 
      className={`fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 ${
        isClosing ? 'backdrop-exit' : 'backdrop-enter'
      }`}
      onClick={handleBackdropClick}
    >
      <div className={`bg-card border border-border-secondary rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden ${
        isClosing ? 'modal-exit' : 'modal-enter'
      }`}>
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-border-secondary">
          <div>
            <h2 className="text-xl font-semibold text-text">
              Discovered Devices
            </h2>
            <p className="text-text-secondary text-sm mt-1">
              {discoveredDevices.length === 0 
                ? 'No new devices found on your network'
                : `${discoveredDevices.length} device${discoveredDevices.length !== 1 ? 's' : ''} found on your network`
              }
            </p>
          </div>
          <button
            onClick={handleClose}
            className="w-8 h-8 rounded-full hover:bg-surface-hover flex items-center justify-center transition-colors duration-200"
            title="Close"
          >
            <svg className="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {discoveredDevices.length === 0 ? (
            // Empty State
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-surface-hover rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-text mb-2">No New Devices Found</h3>
              <p className="text-text-secondary mb-6">
                All devices on your network are already registered with your hub.
              </p>
            </div>
          ) : (
            // Device Grid
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {discoveredDevices.map((device, index) => {
                const deviceState = deviceStates[device.id]?.state || 'idle';
                const staggerClass = `card-stagger-${Math.min(index + 1, 6)}`;
                
                return (
                  <div 
                    key={device.id} 
                    className={`
                      bg-background border border-border-secondary rounded-lg p-4 
                      hover:border-border-primary transition-all duration-300
                      ${staggerClass}
                      ${deviceState === 'success' ? 'success-flash' : ''}
                      ${deviceState === 'error' ? 'error-shake' : ''}
                    `}
                  >
                    {/* Device Header */}
                    <div className="flex items-start space-x-3 mb-3">
                      <div className="w-10 h-10 bg-surface-hover rounded-lg flex items-center justify-center flex-shrink-0">
                        {device.type === 'wifi' ? (
                          <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <h3 className="font-medium text-text truncate">
                          {device.name || 'Unknown Device'}
                        </h3>
                        <p className="text-sm text-text-secondary capitalize">
                          {device.type} {device.subtype || 'Device'}
                        </p>
                        {device.manufacturer && (
                          <p className="text-xs text-text-muted truncate">
                            {device.manufacturer} {device.product && `- ${device.product}`}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    {/* Device Details */}
                    <div className="text-xs text-text-muted mb-3 space-y-1">
                      {device.ip && (
                        <div className="flex justify-between">
                          <span>IP Address:</span>
                          <span className="font-mono">{device.ip}</span>
                        </div>
                      )}
                      {device.node_id && (
                        <div className="flex justify-between">
                          <span>Node ID:</span>
                          <span className="font-mono">{device.node_id}</span>
                        </div>
                      )}
                      {device.discovered_via && (
                        <div className="flex justify-between">
                          <span>Found via:</span>
                          <span className="capitalize">{device.discovered_via}</span>
                        </div>
                      )}
                    </div>
                    
                    {/* Add Button */}
                    <button
                      onClick={() => handleAddDevice(device)}
                      disabled={addingDevices.has(device.id) || deviceState === 'loading'}
                      className={`
                        w-full px-3 py-2 text-white text-sm rounded-md 
                        transition-all duration-200 
                        flex items-center justify-center space-x-2
                        hover:scale-105 hover:shadow-md
                        active:scale-95
                        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                        ${deviceState === 'success' ? 'bg-success' : 
                          deviceState === 'error' ? 'bg-danger' : 'bg-primary hover:bg-primary/90'}
                      `}
                    >
                      {deviceState === 'loading' || addingDevices.has(device.id) ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Adding...</span>
                        </>
                      ) : deviceState === 'success' ? (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span>Added!</span>
                        </>
                      ) : deviceState === 'error' ? (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                          <span>Failed</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          <span>Add to Hub</span>
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {/* Scan Summary */}
          {scanSummary && (
            <div className="bg-background border border-border-secondary rounded-lg p-4">
              <h3 className="text-sm font-medium text-text mb-3">Last Scan Summary</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-lg font-semibold text-primary">
                    {scanSummary.total_found || 0}
                  </div>
                  <div className="text-xs text-text-secondary">Total Found</div>
                </div>
                <div>
                  <div className="text-sm text-text">
                    <span className="font-medium text-accent">{scanSummary.wifi_found || 0}</span> Wi-Fi
                  </div>
                  <div className="text-xs text-text-secondary">Wi-Fi Devices</div>
                </div>
                <div>
                  <div className="text-sm text-text">
                    <span className="font-medium text-accent">{scanSummary.zwave_found || 0}</span> Z-Wave
                  </div>
                  <div className="text-xs text-text-secondary">Z-Wave Devices</div>
                </div>
                <div>
                  <div className="text-lg font-semibold text-success">
                    {scanSummary.duration_ms ? formatDuration(scanSummary.duration_ms) : 'N/A'}
                  </div>
                  <div className="text-xs text-text-secondary">Scan Duration</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between p-6 border-t border-border-secondary bg-surface-hover">
          <div className="text-sm text-text-secondary">
            {discoveredDevices.length > 0 
              ? `${discoveredDevices.length} device${discoveredDevices.length !== 1 ? 's' : ''} waiting to be added`
              : 'Try rescanning to find new devices'
            }
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onRescan}
              disabled={isRescanning}
              className={`
                px-4 py-2 text-white rounded-md font-medium
                transition-all duration-200
                flex items-center space-x-2
                hover:scale-105 hover:shadow-md
                active:scale-95
                disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                ${isRescanning ? 'bg-accent/70' : 'bg-accent hover:bg-accent/90'}
              `}
            >
              {isRescanning ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Rescan</span>
                </>
              )}
            </button>
            <button
              onClick={handleClose}
              className="px-4 py-2 bg-background border border-border-secondary text-text rounded-md hover:bg-surface-hover transition-all duration-200 hover:scale-105 active:scale-95"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
