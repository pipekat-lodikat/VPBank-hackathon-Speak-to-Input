// Auto-detect API URL based on window location
export const getApiUrl = (): string => {
  // In production, use ALB directly (CloudFront only serves static files)
  if (import.meta.env.PROD) {
    return 'http://vpbank-voice-agent-alb-1745174960.us-east-1.elb.amazonaws.com';
  }

  // In development or when accessed via network, use the same hostname
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;

    // If accessing via IP or domain (not localhost), use that
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${protocol}//${hostname}:7860`;
    }
  }

  // Default to localhost for local development
  return 'http://localhost:7860';
};

export const getWsUrl = (): string => {
  const apiUrl = getApiUrl();
  return apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
};

export const API_URL = getApiUrl();
export const WS_URL = getWsUrl();
