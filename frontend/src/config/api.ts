/**
 * API Configuration
 * Centralized configuration for all API endpoints
 * Supports environment variables for different deployment environments
 */

// Get API base URL from environment variable or use default
const getApiBaseUrl = (): string => {
  // Production: Use environment variable or same-origin
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  // In production, fail if no API URL is configured
  if (import.meta.env.PROD) {
    console.error('VITE_API_BASE_URL environment variable is required in production');
    // Fallback to same-origin (assumes frontend and backend on same domain)
    return window.location.origin;
  }

  // Development: Auto-detect if accessed remotely
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If not localhost, use same hostname with port 7860
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:7860`;
    }
  }

  // Development: Default to localhost
  return 'http://localhost:7860';
};

// Get Browser Service URL from environment variable or use default
const getBrowserServiceUrl = (): string => {
  if (import.meta.env.VITE_BROWSER_SERVICE_URL) {
    return import.meta.env.VITE_BROWSER_SERVICE_URL;
  }

  // In production, disable Browser Agent endpoint (not needed for voice chat)
  if (import.meta.env.PROD) {
    // Browser Agent not used in production voice chat
    // Only needed for admin monitoring
    return '';
  }

  // Development: Auto-detect if accessed remotely
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // If not localhost, use same hostname with port 7863
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:7863`;
    }
  }

  // Development: Browser Agent runs on separate port
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

