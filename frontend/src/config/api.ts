/**
 * API Configuration
 * Centralized configuration for all API endpoints
 * Supports environment variables for different deployment environments
 */

// Get API base URL from environment variable or use default
const getApiBaseUrl = (): string => {
  // Production: Use environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  // Development: Default to localhost
  return 'http://localhost:7860';
};

// Get Browser Service URL from environment variable or use default
const getBrowserServiceUrl = (): string => {
  if (import.meta.env.VITE_BROWSER_SERVICE_URL) {
    return import.meta.env.VITE_BROWSER_SERVICE_URL;
  }
  return 'http://localhost:7863';
};

// Get WebSocket URL (convert http/https to ws/wss)
const getWebSocketUrl = (): string => {
  const apiUrl = getApiBaseUrl();
  if (apiUrl.startsWith('https://')) {
    return apiUrl.replace('https://', 'wss://') + '/ws';
  }
  return apiUrl.replace('http://', 'ws://') + '/ws';
};

// Export configuration
export const API_BASE_URL = getApiBaseUrl();
export const BROWSER_SERVICE_URL = getBrowserServiceUrl();
export const WS_URL = getWebSocketUrl();

// API Endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login`,
    REGISTER: `${API_BASE_URL}/api/auth/register`,
    VERIFY: `${API_BASE_URL}/api/auth/verify`,
    FORGOT_PASSWORD: `${API_BASE_URL}/api/auth/forgot-password`,
    RESET_PASSWORD: `${API_BASE_URL}/api/auth/reset-password`,
  },
  // Session endpoints
  SESSIONS: {
    LIST: `${API_BASE_URL}/api/sessions`,
    GET: (sessionId: string) => `${API_BASE_URL}/api/sessions/${sessionId}`,
  },
  // WebRTC endpoint
  WEBRTC_OFFER: `${API_BASE_URL}/offer`,
  // Browser Service endpoints
  BROWSER: {
    LIVE: `${BROWSER_SERVICE_URL}/api/live`,
  },
} as const;

// Log configuration in development
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:', {
    API_BASE_URL,
    BROWSER_SERVICE_URL,
    WS_URL,
  });
}

