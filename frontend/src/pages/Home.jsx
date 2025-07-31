import { useState, useEffect } from 'react';
import { deviceAPI, telemetryAPI } from '../api';
import DeviceCard from '../components/DeviceCard';
import { PageHeader } from '../components/PageHeader';
import { DeviceGridSkeleton, ErrorMessage, EmptyState } from '../components/LoadingStates';
import { AddDeviceModal } from '../components/AddDeviceModal';
import { DiscoveredDevicesModal } from '../components/DiscoveredDevicesModal';

export default function Home() {
  // Device state management
  const [devices, setDevices] = useState([]);
  const [discoveredDevices, setDiscoveredDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDiscovery, setLoadingDiscovery] = useState(false);
  const [addingDevices, setAddingDevices] = useState(new Set()); // Track which devices are being added
  const [error, setError] = useState(null);
  const [discoveryError, setDiscoveryError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [isDiscoveredDevicesModalOpen, setIsDiscoveredDevicesModalOpen] = useState(false);
  
  // Telemetry state
  const [lastScanSummary, setLastScanSummary] = useState(null);

  /**
   * Fetch registered devices from the backend
   */
  const fetchDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await deviceAPI.getDevices();
      setDevices(response.data);
      console.log('📱 Loaded registered devices:', response.data);
    } catch (err) {
      console.error('Failed to fetch devices:', err);
      setError(err.message || 'Failed to connect to the hub. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch telemetry data including last scan summary
   */
  const fetchTelemetryData = async () => {
    try {
      // Fetch last scan summary
      const summaryResponse = await telemetryAPI.getLastScanSummary();
      setLastScanSummary(summaryResponse.data.summary);
      
      console.log('📊 Loaded telemetry data:', {
        summary: summaryResponse.data.summary
      });
      
    } catch (err) {
      console.error('Failed to fetch telemetry data:', err);
      // Don't show error to user for telemetry - it's not critical
    }
  };

  /**
   * Discover available devices on the network
   */
  const discoverDevices = async () => {
    try {
      setLoadingDiscovery(true);
      setDiscoveryError(null);
      console.log('🔍 Starting device discovery...');
      
      const response = await deviceAPI.discoverDevices();
      const discoveredList = response.data.discovered_devices || [];
      
      // Enhanced duplicate filtering - check ID, IP, and node_id
      const filteredDiscovered = discoveredList.filter(discoveredDevice => {
        return !devices.some(registeredDevice => {
          // Check by ID first
          if (discoveredDevice.id === registeredDevice.id) return true;
          
          // For Wi-Fi devices, also check by IP
          if (discoveredDevice.type === 'wifi' && registeredDevice.type === 'wifi' &&
              discoveredDevice.ip && registeredDevice.ip &&
              discoveredDevice.ip === registeredDevice.ip) return true;
              
          // For Z-Wave devices, also check by node_id
          if (discoveredDevice.type === 'zwave' && registeredDevice.type === 'zwave' &&
              discoveredDevice.node_id && registeredDevice.node_id &&
              discoveredDevice.node_id === registeredDevice.node_id) return true;
              
          return false;
        });
      });
      
      setDiscoveredDevices(filteredDiscovered);
      
      console.log('🔍 Discovery completed:', {
        total_found: discoveredList.length,
        new_devices: filteredDiscovered.length,
        filtered_out: discoveredList.length - filteredDiscovered.length,
        summary: response.data.discovery_summary
      });
      
    } catch (err) {
      console.error('Device discovery failed:', err);
      setDiscoveryError(err.response?.data?.detail || err.message || 'Failed to discover devices on the network.');
    } finally {
      setLoadingDiscovery(false);
    }
  };

  /**
   * Add a discovered device to the hub
   */
  const addDiscoveredDevice = async (device) => {
    // Set loading state for this specific device
    setAddingDevices(prev => new Set(prev).add(device.id));
    
    try {
      console.log('➕ Adding discovered device:', device);
      
      // Prepare device data for addition - ensure all required fields
      const deviceData = {
        id: device.id,
        name: device.name,
        type: device.type,
        // Add type-specific fields
        ...(device.ip && { ip: device.ip }),
        ...(device.node_id && { node_id: device.node_id })
      };
      
      // Validate required fields before sending
      if (device.type === 'wifi' && !device.ip) {
        throw new Error('Wi-Fi device must have an IP address');
      }
      if (device.type === 'zwave' && !device.node_id) {
        throw new Error('Z-Wave device must have a node ID');
      }
      
      const response = await deviceAPI.addDevice(deviceData);
      
      if (response.data.success) {
        console.log('✅ Device added successfully:', response.data.device);
        
        // Remove from discovered devices list immediately for better UX
        setDiscoveredDevices(prev => 
          prev.filter(d => d.id !== device.id)
        );
        
        // Refresh registered devices list
        await fetchDevices();
        
        // Optional: Show success toast/notification here
        console.log(`✅ ${device.name} successfully added to your hub!`);
      }
      
    } catch (err) {
      console.error('Failed to add discovered device:', err);
      
      // Better error messaging
      let errorMessage = 'Failed to add device';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      // For better UX, you could implement a toast notification system here
      // For now, using alert but consider implementing a proper notification component
      alert(`❌ ${errorMessage}`);
    } finally {
      // Remove loading state for this device
      setAddingDevices(prev => {
        const newSet = new Set(prev);
        newSet.delete(device.id);
        return newSet;
      });
    }
  };

  // Auto-discovery on component mount
  useEffect(() => {
    const initializeDevices = async () => {
      // Load registered devices first
      await fetchDevices();
      
      // Load telemetry data
      await fetchTelemetryData();
      
      // Then start discovery
      await discoverDevices();
    };
    
    initializeDevices();
  }, []);

  const handleDeviceUpdate = (updatedDevice) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === updatedDevice.id ? updatedDevice : device
      )
    );
  };

  /**
   * Handle successful device addition from the modal
   * Refreshes both device lists and telemetry data, then closes the modal
   */
  const handleDeviceAdded = async () => {
    console.log('✅ Device added successfully, refreshing lists...');
    await fetchDevices(); // Refresh registered devices
    await fetchTelemetryData(); // Refresh telemetry data
    await discoverDevices(); // Refresh discovery to remove any newly registered devices
  };

  /**
   * Manual rescan trigger for the rescan button
   */
  const handleRescan = async () => {
    console.log('🔄 Manual rescan triggered');
    await discoverDevices();
    await fetchTelemetryData(); // Refresh telemetry after scan
  };

  /**
   * Open the Add Device modal
   */
  const openAddModal = () => {
    setShowAddModal(true);
  };

  /**
   * Close the Add Device modal
   */
  const closeAddModal = () => {
    setShowAddModal(false);
  };

  /**
   * Handle dynamic button click - either opens modal or triggers rescan
   */
  const handleDynamicButtonClick = () => {
    const discoveredCount = discoveredDevices.length;
    
    if (discoveredCount > 0) {
      // Open modal to show discovered devices
      setIsDiscoveredDevicesModalOpen(true);
    } else {
      // Trigger rescan
      handleRescan();
    }
  };

  /**
   * Close the discovered devices modal
   */
  const closeDiscoveredDevicesModal = () => {
    setIsDiscoveredDevicesModalOpen(false);
  };

  /**
   * Handle rescan from modal
   */
  const handleModalRescan = async () => {
    await discoverDevices();
    await fetchTelemetryData(); // Refresh telemetry after scan
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Page Header */}
      <PageHeader 
        title="MyHub Local"
        onRefresh={fetchDevices}
        showThemeToggle={true}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title & Stats with Rescan Button */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-text mb-2">
              Smart Home Dashboard
            </h1>
            <p className="text-text-secondary">
              {loading ? 'Loading devices...' : 
               error ? 'Unable to load devices' :
               devices.length === 0 ? 'No devices found' :
               `Managing ${devices.length} connected device${devices.length !== 1 ? 's' : ''}`}
            </p>
          </div>
          
          {/* Dynamic Discovery Button */}
          <div className="mt-4 sm:mt-0">
            <button
              onClick={handleDynamicButtonClick}
              disabled={loadingDiscovery}
              className={`px-4 py-2 text-white rounded-lg hover:opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 ${
                discoveredDevices.length > 0 
                  ? 'bg-primary pulse-glow' 
                  : 'bg-accent'
              }`}
            >
              {loadingDiscovery ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Scanning...</span>
                </>
              ) : discoveredDevices.length > 0 ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <span>{discoveredDevices.length} Device{discoveredDevices.length !== 1 ? 's' : ''} Found!</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Rescan Devices</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Discovery Error Alert */}
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

        {/* Content Area - Registered Devices */}
        {/* Content Area - Registered Devices */}
        {loading ? (
          <div>
            {/* Show discovery loading skeleton */}
            {loadingDiscovery && (
              <div className="mb-8">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-8 h-8 bg-surface-hover rounded-full animate-pulse" />
                  <div>
                    <div className="h-5 w-32 bg-surface-hover rounded animate-pulse mb-1" />
                    <div className="h-3 w-48 bg-surface-hover rounded animate-pulse" />
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="bg-card border border-border-secondary rounded-lg p-4 animate-pulse">
                      <div className="flex items-center space-x-3 mb-3">
                        <div className="w-10 h-10 bg-surface-hover rounded-lg" />
                        <div>
                          <div className="h-4 w-24 bg-surface-hover rounded mb-1" />
                          <div className="h-3 w-16 bg-surface-hover rounded" />
                        </div>
                      </div>
                      <div className="h-8 w-full bg-surface-hover rounded" />
                    </div>
                  ))}
                </div>
              </div>
            )}
            <DeviceGridSkeleton count={6} />
          </div>
        ) : error ? (
          <ErrorMessage 
            message={error}
            onRetry={fetchDevices}
          />
        ) : devices.length === 0 ? (
          <EmptyState 
            title="No Devices Connected"
            description="Connect your smart devices to start controlling them from this dashboard."
            action={
              <button
                onClick={openAddModal}
                className="px-6 py-2 bg-primary text-white rounded-md hover:opacity-80 transition-opacity"
              >
                Add Your First Device
              </button>
            }
          />
        ) : (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-text">
                Connected Devices
              </h2>
              <span className="text-sm text-text-secondary">
                {devices.length} device{devices.length !== 1 ? 's' : ''}
              </span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {devices.map(device => (
                <DeviceCard 
                  key={device.id} 
                  device={device} 
                  onDeviceUpdate={handleDeviceUpdate}
                />
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Floating Add Device Button */}
      {devices.length > 0 && (
        <button
          onClick={openAddModal}
          className="fixed bottom-6 right-6 w-14 h-14 bg-primary text-white rounded-full shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center justify-center z-40"
          title="Add New Device"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      )}

      {/* Add Device Modal */}
      <AddDeviceModal
        isOpen={showAddModal}
        onClose={closeAddModal}
        onDeviceAdded={handleDeviceAdded}
      />

      {/* Discovered Devices Modal */}
      <DiscoveredDevicesModal
        isOpen={isDiscoveredDevicesModalOpen}
        onClose={closeDiscoveredDevicesModal}
        discoveredDevices={discoveredDevices}
        onAddDevice={addDiscoveredDevice}
        onRescan={handleModalRescan}
        addingDevices={addingDevices}
        scanSummary={lastScanSummary}
        isRescanning={loadingDiscovery}
      />
    </div>
  );
}
