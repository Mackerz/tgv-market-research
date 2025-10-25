import { useState, useCallback } from 'react';
import { ApiError } from '@/lib/api/client';

/**
 * Reusable hook for handling errors consistently across the application
 *
 * Provides standardized error message extraction and state management
 * to eliminate duplicate error handling logic.
 *
 * @returns Object containing error state, handler function, and clear function
 *
 * @example
 * ```typescript
 * const { error, handleError, clearError } = useErrorHandler();
 *
 * try {
 *   await someApiCall();
 * } catch (err) {
 *   handleError(err); // Automatically extracts message from ApiError or Error
 * }
 *
 * // Later:
 * clearError(); // Reset error state
 * ```
 */
export function useErrorHandler() {
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles errors and extracts appropriate message
   * Supports ApiError, Error, and unknown error types
   */
  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError) {
      setError(err.message);
    } else if (err instanceof Error) {
      setError(err.message);
    } else {
      setError('An unknown error occurred');
    }
  }, []);

  /**
   * Clears the current error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError,
    setError, // Expose for custom error messages
  };
}
