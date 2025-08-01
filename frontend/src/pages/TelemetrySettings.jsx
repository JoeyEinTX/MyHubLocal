import { useState, useEffect } from 'react';
import { telemetryAPI } from '../api';

export default function TelemetrySettings({ onRefreshReady }) {
  const [discoveryHistory, setDiscoveryHistory] = useState([]);
  const [onboardingHistory, setOnboardingHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch all telemetry data for the settings page
   */
  const fetchTelemetryData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch discovery and onboarding history
      const [discoveryResponse, onboardingResponse] = await Promise.all([
        telemetryAPI.getDiscoveryHistory(10),
        telemetryAPI.getOnboardingHistory(10)
      ]);

      setDiscoveryHistory(discoveryResponse.data.history || []);
      setOnboardingHistory(onboardingResponse.data.history || []);

      console.log('📊 Loaded telemetry settings data:', {
        discovery: discoveryResponse.data.history,
        onboarding: onboardingResponse.data.history
      });

    } catch (err) {
      console.error('Failed to fetch telemetry data:', err);
      setError(err.message || 'Failed to load telemetry data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetryData();
    
    // Provide refresh function to parent
    if (onRefreshReady) {
      onRefreshReady(fetchTelemetryData);
    }
  }, [onRefreshReady]);

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  /**
   * Get status badge styling
   */
  const getStatusBadge = (status) => {
    if (status === 'added') {
      return 'bg-success bg-opacity-20 text-success px-2 py-1 rounded-full text-xs font-medium';
    } else {
      return 'bg-danger bg-opacity-20 text-danger px-2 py-1 rounded-full text-xs font-medium';
    }
  };

  return (
    <div>
      {/* Main Content */}
      <main className="py-8">
        {error && (
          <div className="mb-6 p-4 bg-danger bg-opacity-10 border border-danger rounded-lg">
            <div className="flex items-start space-x-3">
              <svg className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h4 className="text-danger font-medium mb-1">Error</h4>
                <p className="text-danger text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="space-y-8">
            {/* Discovery History Skeleton */}
            <div className="bg-card border border-border-secondary rounded-lg p-6">
              <div className="h-6 w-48 bg-surface-hover rounded animate-pulse mb-4" />
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex justify-between items-center">
                    <div className="h-4 w-32 bg-surface-hover rounded animate-pulse" />
                    <div className="h-4 w-24 bg-surface-hover rounded animate-pulse" />
                    <div className="h-4 w-16 bg-surface-hover rounded animate-pulse" />
                  </div>
                ))}
              </div>
            </div>

            {/* Onboarding History Skeleton */}
            <div className="bg-card border border-border-secondary rounded-lg p-6">
              <div className="h-6 w-48 bg-surface-hover rounded animate-pulse mb-4" />
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex justify-between items-center">
                    <div className="h-4 w-32 bg-surface-hover rounded animate-pulse" />
                    <div className="h-4 w-24 bg-surface-hover rounded animate-pulse" />
                    <div className="h-4 w-16 bg-surface-hover rounded animate-pulse" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Discovery History */}
            <div className="bg-card border border-border-secondary rounded-lg p-6">
              <h2 className="text-xl font-semibold text-text mb-6">Discovery Scan History</h2>
              
              {discoveryHistory.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-text-muted mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <p className="text-text-secondary">No discovery scans found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-secondary">
                        <th className="text-left py-3 px-4 font-medium text-text">Timestamp</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Wi-Fi Devices</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Z-Wave Devices</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Total Found</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Duration</th>
                      </tr>
                    </thead>
                    <tbody>
                      {discoveryHistory.map((scan, index) => (
                        <tr key={index} className="border-b border-border-secondary hover:bg-surface-hover">
                          <td className="py-3 px-4 text-text-secondary">
                            {formatTimestamp(scan.timestamp)}
                          </td>
                          <td className="py-3 px-4 text-text">
                            {scan.wifi_found}
                          </td>
                          <td className="py-3 px-4 text-text">
                            {scan.zwave_found}
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-medium text-text">{scan.total_found}</span>
                          </td>
                          <td className="py-3 px-4 text-text-muted">
                            {scan.duration_ms}ms
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Onboarding History */}
            <div className="bg-card border border-border-secondary rounded-lg p-6">
              <h2 className="text-xl font-semibold text-text mb-6">Device Onboarding History</h2>
              
              {onboardingHistory.length === 0 ? (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-text-muted mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <p className="text-text-secondary">No device onboarding events found</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border-secondary">
                        <th className="text-left py-3 px-4 font-medium text-text">Timestamp</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Device Name</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Device ID</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Type</th>
                        <th className="text-left py-3 px-4 font-medium text-text">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {onboardingHistory.map((event, index) => (
                        <tr key={index} className="border-b border-border-secondary hover:bg-surface-hover">
                          <td className="py-3 px-4 text-text-secondary">
                            {formatTimestamp(event.timestamp)}
                          </td>
                          <td className="py-3 px-4 text-text font-medium">
                            {event.device_name}
                          </td>
                          <td className="py-3 px-4 text-text-muted font-mono text-sm">
                            {event.device_id}
                          </td>
                          <td className="py-3 px-4 text-text capitalize">
                            {event.type}
                          </td>
                          <td className="py-3 px-4">
                            <span className={getStatusBadge(event.status)}>
                              {event.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
