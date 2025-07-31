import { useState, useEffect } from 'react';
import api from '../api';

/**
 * AddDeviceModal Component
 * 
 * A comprehensive modal for adding devices to the smart home hub.
 * Features two tabs: Discovery (auto-scan) and Manual Add.
 * Integrates with the backend API for device discovery and registration.
 */
export function AddDeviceModal({ isOpen, onClose, onDeviceAdded }) {
  // Modal state management
  const [activeTab, setActiveTab] = useState('discovery'); // 'discovery' or 'manual'
  
  // Discovery tab state
  const [discoveredDevices, setDiscoveredDevices] = useState([]);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [discoveryError, setDiscoveryError] = useState(null);
  
  // Manual add tab state
  const [manualForm, setManualForm] = useState({
    id: '',
    name: '',
    type: 'wifi',
    ip: '',
    node_id: ''
  });
  const [isAdding, setIsAdding] = useState(false);
  const [addError, setAddError] = useState(null);
  const [addSuccess, setAddSuccess] = useState(null);

  // Reset modal state when opened
  useEffect(() => {
    if (isOpen) {
      setActiveTab('discovery');
      setDiscoveredDevices([]);
      setDiscoveryError(null);
      setManualForm({
        id: '',
        name: '',
        type: 'wifi',
        ip: '',
        node_id: ''
      });
      setAddError(null);
      setAddSuccess(null);
      
      // Auto-discover when modal opens
      discoverDevices();
    }
  }, [isOpen]);

  /**
   * Discover available devices using the backend API
   */
  const discoverDevices = async () => {
    setIsDiscovering(true);
    setDiscoveryError(null);
    
    try {
      console.log('🔍 Starting device discovery...');
      const response = await api.get('/devices/discover');
      const data = response.data;
      
      console.log('📡 Discovery response:', data);
      
      if (data.discovered_devices) {
        setDiscoveredDevices(data.discovered_devices);
        console.log(`✅ Found ${data.discovered_devices.length} devices`);
      } else {
        setDiscoveredDevices([]);
      }
    } catch (error) {
      console.error('❌ Discovery failed:', error);
      setDiscoveryError(
        error.response?.data?.detail || 
        'Failed to discover devices. Please check your network connection.'
      );
      setDiscoveredDevices([]);
    } finally {
      setIsDiscovering(false);
    }
  };

  /**
   * Add a discovered device to the hub
   */
  const addDiscoveredDevice = async (device) => {
    setIsAdding(true);
    setAddError(null);
    
    try {
      console.log('➕ Adding discovered device:', device);
      
      // Prepare device data for API
      const deviceData = {
        id: device.id,
        name: device.name,
        type: device.type
      };
      
      // Add type-specific fields
      if (device.type === 'wifi' && device.ip) {
        deviceData.ip = device.ip;
      }
      if (device.type === 'zwave' && device.node_id) {
        deviceData.node_id = device.node_id;
      }
      
      const response = await api.post('/devices/add', deviceData);
      console.log('✅ Device added successfully:', response.data);
      
      // Notify parent component
      onDeviceAdded();
      
      // Close modal after successful add
      setTimeout(() => {
        onClose();
      }, 1000);
      
    } catch (error) {
      console.error('❌ Failed to add device:', error);
      setAddError(
        error.response?.data?.detail || 
        'Failed to add device. Please try again.'
      );
    } finally {
      setIsAdding(false);
    }
  };

  /**
   * Handle manual form input changes
   */
  const handleManualFormChange = (field, value) => {
    setManualForm(prev => {
      const updated = { ...prev, [field]: value };
      
      // Auto-generate ID from name if name is provided
      if (field === 'name' && value) {
        updated.id = value.toLowerCase()
          .replace(/[^a-z0-9\s]/g, '')
          .replace(/\s+/g, '_')
          .substring(0, 20);
      }
      
      return updated;
    });
    
    // Clear errors when user starts typing
    setAddError(null);
    setAddSuccess(null);
  };

  /**
   * Submit manual device addition
   */
  const submitManualAdd = async (e) => {
    e.preventDefault();
    setIsAdding(true);
    setAddError(null);
    setAddSuccess(null);
    
    try {
      // Validate required fields
      if (!manualForm.name.trim()) {
        throw new Error('Device name is required');
      }
      
      if (manualForm.type === 'wifi' && !manualForm.ip.trim()) {
        throw new Error('IP address is required for Wi-Fi devices');
      }
      
      if (manualForm.type === 'zwave' && !manualForm.node_id.trim()) {
        throw new Error('Node ID is required for Z-Wave devices');
      }
      
      // Prepare device data
      const deviceData = {
        id: manualForm.id || manualForm.name.toLowerCase().replace(/\s+/g, '_'),
        name: manualForm.name.trim(),
        type: manualForm.type
      };
      
      if (manualForm.type === 'wifi') {
        deviceData.ip = manualForm.ip.trim();
      } else if (manualForm.type === 'zwave') {
        deviceData.node_id = parseInt(manualForm.node_id);
      }
      
      console.log('➕ Adding manual device:', deviceData);
      
      const response = await api.post('/devices/add', deviceData);
      console.log('✅ Manual device added successfully:', response.data);
      
      setAddSuccess('Device added successfully!');
      
      // Reset form
      setManualForm({
        id: '',
        name: '',
        type: 'wifi',
        ip: '',
        node_id: ''
      });
      
      // Notify parent component
      onDeviceAdded();
      
      // Close modal after successful add
      setTimeout(() => {
        onClose();
      }, 1500);
      
    } catch (error) {
      console.error('❌ Failed to add manual device:', error);
      setAddError(
        error.response?.data?.detail || 
        error.message ||
        'Failed to add device. Please check your input and try again.'
      );
    } finally {
      setIsAdding(false);
    }
  };

  // Don't render if modal is closed
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal Container */}
      <div className="flex min-h-full items-center justify-center p-4 sm:p-6">
        <div className="relative w-full max-w-3xl max-h-[90vh] bg-card rounded-xl shadow-2xl overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-b border-border-secondary bg-background">
            <div>
              <h2 className="text-xl font-semibold text-text">Add New Device</h2>
              <p className="text-sm text-text-secondary mt-1">Connect a new smart device to your hub</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-text-secondary hover:text-text hover:bg-surface-hover rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex border-b border-border-secondary bg-background">
            <button
              onClick={() => setActiveTab('discovery')}
              className={`flex-1 px-4 sm:px-6 py-3 text-sm font-medium transition-all duration-200 relative ${
                activeTab === 'discovery'
                  ? 'text-primary bg-card'
                  : 'text-text-secondary hover:text-text hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Discovered</span>
              </div>
              {activeTab === 'discovery' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('manual')}
              className={`flex-1 px-4 sm:px-6 py-3 text-sm font-medium transition-all duration-200 relative ${
                activeTab === 'manual'
                  ? 'text-primary bg-card'
                  : 'text-text-secondary hover:text-text hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Manual Add</span>
              </div>
              {activeTab === 'manual' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
              )}
            </button>
          </div>
          
          {/* Tab Content */}
          <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
            {activeTab === 'discovery' && (
              <div className="p-4 sm:p-6">
                {/* Discovery Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 space-y-3 sm:space-y-0">
                  <div>
                    <h3 className="text-lg font-medium text-text mb-1">Network Discovery</h3>
                    <p className="text-text-secondary text-sm">
                      Automatically scan for devices on your network
                    </p>
                  </div>
                  <button
                    onClick={discoverDevices}
                    disabled={isDiscovering}
                    className="px-4 py-2 bg-accent text-white rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isDiscovering ? (
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
                </div>
                
                {/* Discovery Error */}
                {discoveryError && (
                  <div className="mb-6 p-4 bg-danger bg-opacity-10 border border-danger rounded-lg">
                    <div className="flex items-start space-x-3">
                      <svg className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h4 className="text-danger font-medium mb-1">Discovery Failed</h4>
                        <p className="text-danger text-sm">{discoveryError}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Discovered Devices List */}
                {isDiscovering ? (
                  <div className="text-center py-12">
                    <div className="w-12 h-12 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <h3 className="text-text font-medium mb-2">Scanning Network</h3>
                    <p className="text-text-secondary text-sm">Looking for smart devices...</p>
                  </div>
                ) : discoveredDevices.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-20 h-20 bg-surface-hover rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-10 h-10 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <h3 className="text-text font-medium mb-2">No Devices Found</h3>
                    <p className="text-text-secondary text-sm mb-4">
                      No smart devices were discovered on your network
                    </p>
                    <p className="text-text-muted text-xs">
                      Try manual add or check if your devices are connected to the same network
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="text-text font-medium">Found {discoveredDevices.length} device{discoveredDevices.length !== 1 ? 's' : ''}</h4>
                    </div>
                    {discoveredDevices.map((device, index) => (
                      <div
                        key={device.id || index}
                        className="flex items-center justify-between p-4 bg-background rounded-lg border border-border-secondary hover:border-border-primary transition-colors"
                      >
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-3 mb-2">
                            <div className="w-10 h-10 bg-primary bg-opacity-10 rounded-lg flex items-center justify-center flex-shrink-0">
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
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-text truncate">{device.name}</h3>
                              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                                <span className="text-sm text-primary font-medium">
                                  {device.type === 'wifi' ? 'Wi-Fi' : 'Z-Wave'}
                                </span>
                                {device.ip && (
                                  <span className="text-sm text-text-muted">IP: {device.ip}</span>
                                )}
                                {device.node_id && (
                                  <span className="text-sm text-text-muted">Node: {device.node_id}</span>
                                )}
                                {device.manufacturer && (
                                  <span className="text-sm text-text-muted">{device.manufacturer}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                        <button
                          onClick={() => addDiscoveredDevice(device)}
                          disabled={isAdding}
                          className="ml-4 px-4 py-2 bg-primary text-white rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                        >
                          {isAdding ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                              <span>Adding...</span>
                            </>
                          ) : (
                            <>
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                              </svg>
                              <span>Add</span>
                            </>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
            
            {activeTab === 'manual' && (
              <div className="p-4 sm:p-6">
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-text mb-1">Manual Device Setup</h3>
                  <p className="text-text-secondary text-sm">
                    Add a device by entering its connection details manually
                  </p>
                </div>
                
                {/* Success Message */}
                {addSuccess && (
                  <div className="mb-6 p-4 bg-success bg-opacity-10 border border-success rounded-lg">
                    <div className="flex items-start space-x-3">
                      <svg className="w-5 h-5 text-success flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h4 className="text-success font-medium mb-1">Success!</h4>
                        <p className="text-success text-sm">{addSuccess}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Error Message */}
                {addError && (
                  <div className="mb-6 p-4 bg-danger bg-opacity-10 border border-danger rounded-lg">
                    <div className="flex items-start space-x-3">
                      <svg className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h4 className="text-danger font-medium mb-1">Error</h4>
                        <p className="text-danger text-sm">{addError}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Manual Add Form */}
                <form onSubmit={submitManualAdd} className="space-y-6">
                  {/* Device Name */}
                  <div>
                    <label className="block text-sm font-medium text-text mb-2">
                      Device Name <span className="text-danger">*</span>
                    </label>
                    <input
                      type="text"
                      value={manualForm.name}
                      onChange={(e) => handleManualFormChange('name', e.target.value)}
                      placeholder="e.g., Living Room Light"
                      className="w-full px-4 py-3 bg-background border border-border-secondary rounded-lg text-text placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors"
                      required
                    />
                  </div>
                  
                  {/* Device ID (auto-generated) */}
                  <div>
                    <label className="block text-sm font-medium text-text mb-2">
                      Device ID
                    </label>
                    <input
                      type="text"
                      value={manualForm.id}
                      onChange={(e) => handleManualFormChange('id', e.target.value)}
                      placeholder="Auto-generated from name"
                      className="w-full px-4 py-3 bg-surface-hover border border-border-secondary rounded-lg text-text-secondary text-sm focus:outline-none focus:ring-1 focus:ring-border-primary"
                    />
                    <p className="text-xs text-text-muted mt-2">
                      Unique identifier (auto-generated if left empty)
                    </p>
                  </div>
                  
                  {/* Device Type */}
                  <div>
                    <label className="block text-sm font-medium text-text mb-2">
                      Device Type <span className="text-danger">*</span>
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <label className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        manualForm.type === 'wifi' 
                          ? 'border-primary bg-primary bg-opacity-5' 
                          : 'border-border-secondary hover:border-border-primary'
                      }`}>
                        <input
                          type="radio"
                          name="deviceType"
                          value="wifi"
                          checked={manualForm.type === 'wifi'}
                          onChange={(e) => handleManualFormChange('type', e.target.value)}
                          className="sr-only"
                        />
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            manualForm.type === 'wifi' ? 'bg-primary text-white' : 'bg-surface-hover text-text-secondary'
                          }`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                            </svg>
                          </div>
                          <div>
                            <div className="font-medium text-text">Wi-Fi Device</div>
                            <div className="text-sm text-text-secondary">Smart plugs, lights, etc.</div>
                          </div>
                        </div>
                      </label>
                      
                      <label className={`relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        manualForm.type === 'zwave' 
                          ? 'border-primary bg-primary bg-opacity-5' 
                          : 'border-border-secondary hover:border-border-primary'
                      }`}>
                        <input
                          type="radio"
                          name="deviceType"
                          value="zwave"
                          checked={manualForm.type === 'zwave'}
                          onChange={(e) => handleManualFormChange('type', e.target.value)}
                          className="sr-only"
                        />
                        <div className="flex items-center space-x-3">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            manualForm.type === 'zwave' ? 'bg-primary text-white' : 'bg-surface-hover text-text-secondary'
                          }`}>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>
                          <div>
                            <div className="font-medium text-text">Z-Wave Device</div>
                            <div className="text-sm text-text-secondary">Sensors, switches, etc.</div>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>
                  
                  {/* Conditional Fields Based on Type */}
                  {manualForm.type === 'wifi' && (
                    <div>
                      <label className="block text-sm font-medium text-text mb-2">
                        IP Address <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        value={manualForm.ip}
                        onChange={(e) => handleManualFormChange('ip', e.target.value)}
                        placeholder="e.g., 192.168.1.100"
                        pattern="^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
                        className="w-full px-4 py-3 bg-background border border-border-secondary rounded-lg text-text placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors"
                        required
                      />
                      <p className="text-xs text-text-muted mt-2">
                        IP address of the device on your network
                      </p>
                    </div>
                  )}
                  
                  {manualForm.type === 'zwave' && (
                    <div>
                      <label className="block text-sm font-medium text-text mb-2">
                        Z-Wave Node ID <span className="text-danger">*</span>
                      </label>
                      <input
                        type="number"
                        value={manualForm.node_id}
                        onChange={(e) => handleManualFormChange('node_id', e.target.value)}
                        placeholder="e.g., 5"
                        min="1"
                        max="232"
                        className="w-full px-4 py-3 bg-background border border-border-secondary rounded-lg text-text placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors"
                        required
                      />
                      <p className="text-xs text-text-muted mt-2">
                        Node ID from your Z-Wave controller (1-232)
                      </p>
                    </div>
                  )}
                  
                  {/* Submit Button */}
                  <div className="flex justify-end space-x-3 pt-4 border-t border-border-secondary">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-6 py-3 text-text-secondary hover:text-text transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isAdding || !manualForm.name.trim()}
                      className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-80 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {isAdding ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Adding Device...</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          <span>Add Device</span>
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
