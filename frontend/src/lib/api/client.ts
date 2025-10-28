/**
 * API Client
 * Centralized HTTP client with error handling, retry logic, and type safety
 */

import { apiUrl } from '@/config/api';
import { logger } from '@/lib/logger';
import { DEFAULT_API_TIMEOUT_MS } from '@/config/constants';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data: any,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean | null | undefined>;
  retry?: number;
  timeout?: number;
}

class ApiClient {
  private defaultTimeout = DEFAULT_API_TIMEOUT_MS;

  /**
   * Make a GET request
   */
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    logger.info(`[API Client] API Key present: ${!!apiKey}, length: ${apiKey?.length || 0}`);
    if (!apiKey) {
      logger.warn('[API Client] NEXT_PUBLIC_API_KEY is not set!');
    }
    return this.request<T>(endpoint, {
      ...config,
      method: 'GET',
      headers: {
        ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        ...config?.headers,
      },
    });
  }

  /**
   * Make a POST request
   */
  async post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        ...config?.headers,
      },
    });
  }

  /**
   * Make a PUT request
   */
  async put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        ...config?.headers,
      },
    });
  }

  /**
   * Make a PATCH request
   */
  async patch<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        ...config?.headers,
      },
    });
  }

  /**
   * Make a DELETE request
   */
  async delete<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    return this.request<T>(endpoint, {
      ...config,
      method: 'DELETE',
      body: data ? JSON.stringify(data) : undefined,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'X-API-Key': apiKey } : {}),
        ...config?.headers,
      },
    });
  }

  /**
   * Upload a file with FormData
   */
  async upload<T>(endpoint: string, formData: FormData, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: formData,
      // Don't set Content-Type for FormData - browser will set it with boundary
    });
  }

  /**
   * Core request method with error handling
   */
  private async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const {
      params,
      retry = 0,
      timeout = this.defaultTimeout,
      ...fetchConfig
    } = config;

    // Build URL with query params
    let url = apiUrl(endpoint);
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        signal: controller.signal,
        credentials: 'include', // Include cookies for authentication
      });

      clearTimeout(timeoutId);

      // Handle non-OK responses
      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: response.statusText };
        }

        throw new ApiError(
          response.status,
          response.statusText,
          errorData,
          typeof errorData.detail === 'string'
            ? errorData.detail
            : JSON.stringify(errorData.detail || errorData)
        );
      }

      // Parse response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      // Return empty object for no content responses
      return {} as T;
    } catch (error) {
      clearTimeout(timeoutId);

      // Retry logic for network errors
      if (retry > 0 && error instanceof TypeError) {
        logger.warn(`Request failed, retrying... (${retry} attempts left)`);
        await this.delay(1000);
        return this.request<T>(endpoint, { ...config, retry: retry - 1 });
      }

      // Handle abort (timeout)
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError(
          408,
          'Request Timeout',
          {},
          `Request timeout after ${timeout}ms`
        );
      }

      // Re-throw API errors
      if (error instanceof ApiError) {
        throw error;
      }

      // Wrap unknown errors
      throw new ApiError(
        0,
        'Network Error',
        {},
        error instanceof Error ? error.message : 'An unknown error occurred'
      );
    }
  }

  /**
   * Delay helper for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
