/**
 * Tests for useApi Hook
 */

import { renderHook, waitFor } from '@testing-library/react';
import { useApi } from '../useApi';
import { ApiError } from '@/lib/api/client';

describe('useApi Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch data immediately on mount by default', async () => {
    const fetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() => useApi(fetcher));

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();

    // Wait for data to load
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ data: 'test' });
    expect(result.current.error).toBeNull();
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('should not fetch immediately when immediate is false', async () => {
    const fetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() => useApi(fetcher, [], { immediate: false }));

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('should handle errors correctly', async () => {
    const error = new ApiError(404, 'Not Found', {}, 'Resource not found');
    const fetcher = jest.fn().mockRejectedValue(error);

    const { result } = renderHook(() => useApi(fetcher));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBe('Resource not found');
  });

  it('should handle generic Error objects', async () => {
    const error = new Error('Generic error');
    const fetcher = jest.fn().mockRejectedValue(error);

    const { result } = renderHook(() => useApi(fetcher));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Generic error');
  });

  it('should handle unknown errors', async () => {
    const fetcher = jest.fn().mockRejectedValue('string error');

    const { result } = renderHook(() => useApi(fetcher));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('An unknown error occurred');
  });

  it('should allow manual execution', async () => {
    const fetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() => useApi(fetcher, [], { immediate: false }));

    expect(fetcher).not.toHaveBeenCalled();

    // Manually execute
    await result.current.execute();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual({ data: 'test' });
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('should allow refetching', async () => {
    const fetcher = jest.fn()
      .mockResolvedValueOnce({ data: 'first' })
      .mockResolvedValueOnce({ data: 'second' });

    const { result } = renderHook(() => useApi(fetcher));

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'first' });
    });

    // Refetch
    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'second' });
    });

    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it('should reset state', async () => {
    const fetcher = jest.fn().mockResolvedValue({ data: 'test' });

    const { result } = renderHook(() => useApi(fetcher));

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'test' });
    });

    // Reset
    result.current.reset();

    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it('should call onSuccess callback', async () => {
    const fetcher = jest.fn().mockResolvedValue({ data: 'test' });
    const onSuccess = jest.fn();

    renderHook(() => useApi(fetcher, [], { onSuccess }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith({ data: 'test' });
    });
  });

  it('should call onError callback', async () => {
    const error = new Error('Test error');
    const fetcher = jest.fn().mockRejectedValue(error);
    const onError = jest.fn();

    renderHook(() => useApi(fetcher, [], { onError }));

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(error);
    });
  });

  it('should refetch when dependencies change', async () => {
    const fetcher = jest.fn()
      .mockResolvedValueOnce({ data: 'first' })
      .mockResolvedValueOnce({ data: 'second' });

    const { result, rerender } = renderHook(
      ({ id }) => useApi(() => fetcher(id), [id]),
      { initialProps: { id: 1 } }
    );

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'first' });
    });

    expect(fetcher).toHaveBeenCalledWith(1);

    // Change dependency
    rerender({ id: 2 });

    await waitFor(() => {
      expect(result.current.data).toEqual({ data: 'second' });
    });

    expect(fetcher).toHaveBeenCalledWith(2);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it('should handle concurrent requests correctly', async () => {
    const fetcher = jest.fn()
      .mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: 'test' }), 100)));

    const { result } = renderHook(() => useApi(fetcher, [], { immediate: false }));

    // Trigger multiple concurrent requests
    const promise1 = result.current.execute();
    const promise2 = result.current.execute();

    await Promise.all([promise1, promise2]);

    // Should have called fetcher for each execute
    expect(fetcher).toHaveBeenCalledTimes(2);
  });

  it('should maintain type safety', async () => {
    interface User {
      id: number;
      name: string;
    }

    const fetcher = jest.fn().mockResolvedValue({ id: 1, name: 'John' });

    const { result } = renderHook(() => useApi<User>(fetcher));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // TypeScript should enforce type checking
    expect(result.current.data?.id).toBe(1);
    expect(result.current.data?.name).toBe('John');
  });
});
