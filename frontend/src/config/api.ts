// API Configuration - hardcoded for production deployment
export const API_BASE_URL = 'https://tmg-market-research-backend-953615400721.us-central1.run.app';

// Helper function to build API URLs
export const apiUrl = (path: string) => `${API_BASE_URL}${path}`;