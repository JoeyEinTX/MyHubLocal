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
  controlDevice: (id, action) => api.post('/devices/control', { id, action }),
};

export default api;
