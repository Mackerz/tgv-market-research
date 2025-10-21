// API Configuration - environment-based
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'production'
    ? 'https://tmg-market-research-backend-953615400721.us-central1.run.app'
    : 'http://localhost:8000');

// Helper function to build API URLs
export const apiUrl = (path: string) => `${API_BASE_URL}${path}`;