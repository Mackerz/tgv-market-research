import { useState, useCallback } from 'react';

/**
 * Generic hook for managing async action state (loading, error, data)
 *
 * Eliminates duplicate loading state management patterns across the application.
 * Automatically handles loading states, error catching, and data storage.
 *
 * @template T - The type of data returned by the async function
 * @template Args - The types of arguments passed to the async function
 * @param asyncFn - The async function to execute
 * @returns Object containing loading state, error, data, and execute function
 *
 * @example
 * ```typescript
 * const fetchUser = async (userId: number) => {
 *   const response = await apiClient.get<User>(`/api/users/${userId}`);
 *   return response;
 * };
 *
 * const { loading, error, data, execute } = useAsyncAction(fetchUser);
 *
 * // Later:
 * await execute(123); // Automatically manages loading/error states
 * ```
 *
 * @example With dependencies
 * ```typescript
 * const { loading, error, data, execute } = useAsyncAction(
 *   async (searchTerm: string) => {
 *     return await apiClient.get('/api/search', { params: { q: searchTerm } });
 *   }
 * );
 * ```
 */
export function useAsyncAction<T, Args extends any[]>(
  asyncFn: (...args: Args) => Promise<T>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<T | null>(null);

  /**
   * Executes the async function with automatic state management
   * @param args - Arguments to pass to the async function
   * @returns Promise resolving to the function result
   * @throws Re-throws any errors after storing them in state
   */
  const execute = useCallback(
    async (...args: Args): Promise<T> => {
      try {
        setLoading(true);
        setError(null);
        const result = await asyncFn(...args);
        setData(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [asyncFn]
  );

  /**
   * Resets all state to initial values
   */
  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    loading,
    error,
    data,
    execute,
    reset,
    // Expose setters for advanced use cases
    setLoading,
    setError,
    setData,
  };
}

/**
 * Variant of useAsyncAction that executes immediately on mount
 *
 * Useful for fetching data when a component mounts without needing
 * to manually call execute().
 *
 * @example
 * ```typescript
 * const { loading, error, data, refetch } = useAsyncEffect(
 *   () => apiClient.get<Survey[]>('/api/surveys')
 * );
 * ```
 */
export function useAsyncEffect<T>(
  asyncFn: () => Promise<T>,
  deps: React.DependencyList = []
) {
  const { loading, error, data, execute, reset } = useAsyncAction(asyncFn);

  // Execute on mount and when dependencies change
  React.useEffect(() => {
    execute();
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    loading,
    error,
    data,
    refetch: execute, // Alias for clarity
    reset,
  };
}

// Import React for useEffect in useAsyncEffect
import React from 'react';
