/**
 * useApi Hook
 * Generic hook for API calls with loading, error, and data state
 */

import { useState, useEffect, useCallback } from 'react';
import { ApiError } from '@/lib/api';

interface UseApiOptions {
  immediate?: boolean; // Whether to fetch immediately on mount
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError | Error) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: () => Promise<void>;
  refetch: () => Promise<void>;
  reset: () => void;
}

/**
 * Custom hook for API calls with automatic state management
 * @param fetcher - Async function that returns the data
 * @param deps - Dependencies array for useEffect
 * @param options - Additional options
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: any[] = [],
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const { immediate = true, onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetcher();
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      const errorMessage = err instanceof ApiError
        ? err.message
        : err instanceof Error
        ? err.message
        : 'An unknown error occurred';

      setError(errorMessage);
      onError?.(err as ApiError | Error);
    } finally {
      setLoading(false);
    }
  }, [fetcher, onSuccess, onError]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return {
    data,
    loading,
    error,
    execute,
    refetch: execute,
    reset,
  };
}
