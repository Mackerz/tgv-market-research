/**
 * Authentication API Service
 * All authentication-related API calls
 */

import { apiClient } from '../client';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface GoogleAuthRequest {
  credential: string;
}

export interface AuthCheckResponse {
  google_sso_enabled: boolean;
  environment: 'development' | 'production';
}

export const authService = {
  /**
   * Get current authenticated user
   */
  getMe: () => {
    return apiClient.get<User>('/api/auth/me');
  },

  /**
   * Login with username and password
   */
  login: (username: string, password: string) => {
    const data: LoginRequest = { username, password };
    return apiClient.post<User>('/api/auth/login', data);
  },

  /**
   * Login with Google OAuth
   */
  googleLogin: (credential: string) => {
    const data: GoogleAuthRequest = { credential };
    return apiClient.post<User>('/api/auth/google', data);
  },

  /**
   * Logout current user
   */
  logout: () => {
    return apiClient.post('/api/auth/logout', {});
  },

  /**
   * Check authentication configuration
   */
  checkAuthConfig: () => {
    return apiClient.get<AuthCheckResponse>('/api/auth/check');
  },
};
