import { useState, useEffect } from 'react';
import { deviceAPI } from '../api';
import DeviceCard from '../components/DeviceCard';
import { PageHeader } from '../components/PageHeader';
import { DeviceGridSkeleton, ErrorMessage, EmptyState } from '../components/LoadingStates';

export default function Home() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await deviceAPI.getDevices();
      setDevices(response.data);
    } catch (err) {
      console.error('Failed to fetch devices:', err);
      setError(err.message || 'Failed to connect to the hub. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const handleDeviceUpdate = (updatedDevice) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === updatedDevice.id ? updatedDevice : device
      )
    );
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
        {/* Page Title & Stats */}
        <div className="mb-8">
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

        {/* Content Area */}
        {loading ? (
          <DeviceGridSkeleton count={6} />
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
                onClick={fetchDevices}
                className="px-6 py-2 bg-primary text-white rounded-md hover:opacity-80 transition-opacity"
              >
                Scan for Devices
              </button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {devices.map(device => (
              <DeviceCard 
                key={device.id} 
                device={device} 
                onDeviceUpdate={handleDeviceUpdate}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
