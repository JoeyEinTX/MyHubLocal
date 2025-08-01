import axios from 'axios';

// Use Vite proxy in Codespaces to avoid auth issues
const getBaseURL = () => {
  console.log('🔍 Debugging API URL:');
  console.log('Current location:', window.location);
  console.log('Hostname:', window.location.hostname);
  
  if (window.location.hostname.includes('app.github.dev') || 
      window.location.hostname.includes('github.dev') ||
      window.location.hostname.includes('githubpreview.dev')) {
    // In Codespaces, use Vite proxy to avoid port authentication
    console.log('🌐 Codespaces detected, using Vite proxy: /api');
    return '/api';
  }
  // Local development
  console.log('🏠 Local development, using localhost:8000');
  return 'http://localhost:8000';
};

const baseURL = getBaseURL();
console.log('📡 Final API baseURL:', baseURL);

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const deviceAPI = {
  // Get all devices
  getDevices: () => api.get('/devices/list'),
  
  // Control a device (turn on/off)
  controlDevice: (id, action) => api.put(`/devices/${id}/state`, { state: { on: action === 'on' } }),
  
  // Discover available devices
  discoverDevices: () => api.get('/devices/discover'),
  
  // Add a new device
  addDevice: (deviceData) => api.post('/devices/add', deviceData),
  
  // Remove a device
  removeDevice: (deviceId) => api.delete(`/devices/remove/${deviceId}`),
  
  // Get specific device details
  getDevice: (deviceId) => api.get(`/devices/${deviceId}`),
  
  // Get devices health status (NEW - for dashboard monitoring)
  getDevicesHealth: () => api.get('/devices/health'),
};

export const scenesAPI = {
  // Get all available scenes
  getScenes: () => api.get('/scenes/list'),
  
  // Activate a scene
  activateScene: (sceneId) => api.post('/scenes/activate', { scene_id: sceneId }),
};

export const telemetryAPI = {
  // Get discovery scan history
  getDiscoveryHistory: (limit = 10) => api.get(`/telemetry/discovery-history?limit=${limit}`),
  
  // Get device onboarding history
  getOnboardingHistory: (limit = 10) => api.get(`/telemetry/onboarding-history?limit=${limit}`),
  
  // Get last scan summary
  getLastScanSummary: () => api.get('/telemetry/scan-summary'),
  
  // Internal logging endpoints (used by backend)
  logDiscovery: (data) => api.post('/telemetry/log-discovery', data),
  logOnboarding: (data) => api.post('/telemetry/log-onboarding', data),
};

export default api;
