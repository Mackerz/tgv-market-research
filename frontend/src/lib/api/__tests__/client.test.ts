/**
 * Tests for API Client
 */

import { apiClient, ApiError } from '../client';

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe('GET requests', () => {
    it('should make a successful GET request', async () => {
      const mockData = { id: 1, name: 'Test' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await apiClient.get('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should handle GET request with query parameters', async () => {
      const mockData = { results: [] };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      await apiClient.get('/test', {
        params: { page: 1, limit: 10 },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=1'),
        expect.any(Object)
      );
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=10'),
        expect.any(Object)
      );
    });

    it('should throw ApiError on failed GET request', async () => {
      const errorData = { detail: 'Not found' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => errorData,
      });

      await expect(apiClient.get('/test')).rejects.toThrow(ApiError);
      await expect(apiClient.get('/test')).rejects.toThrow('Not found');
    });
  });

  describe('POST requests', () => {
    it('should make a successful POST request with JSON body', async () => {
      const mockData = { id: 1, created: true };
      const postData = { name: 'Test', value: 123 };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await apiClient.post('/test', postData);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should handle POST request without body', async () => {
      const mockData = { success: true };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      await apiClient.post('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test'),
        expect.objectContaining({
          method: 'POST',
          body: undefined,
        })
      );
    });
  });

  describe('PUT requests', () => {
    it('should make a successful PUT request', async () => {
      const mockData = { id: 1, updated: true };
      const putData = { name: 'Updated' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await apiClient.put('/test/1', putData);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(putData),
        })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('DELETE requests', () => {
    it('should make a successful DELETE request', async () => {
      const mockData = { deleted: true };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await apiClient.delete('/test/1');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/test/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('File upload', () => {
    it('should upload a file with FormData', async () => {
      const mockData = { file_url: 'https://example.com/file.jpg' };
      const formData = new FormData();
      formData.append('file', new Blob(['test']), 'test.jpg');

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await apiClient.upload('/upload', formData);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/upload'),
        expect.objectContaining({
          method: 'POST',
          body: formData,
        })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('Error handling', () => {
    it('should create ApiError with correct properties', () => {
      const error = new ApiError(404, 'Not Found', { detail: 'Resource not found' });

      expect(error).toBeInstanceOf(Error);
      expect(error.status).toBe(404);
      expect(error.statusText).toBe('Not Found');
      expect(error.data).toEqual({ detail: 'Resource not found' });
      expect(error.message).toContain('Resource not found');
      expect(error.name).toBe('ApiError');
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new TypeError('Network error'));

      await expect(apiClient.get('/test')).rejects.toThrow('Network error');
    });

    it('should retry on network errors', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new TypeError('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ success: true }),
        });

      const result = await apiClient.get('/test', { retry: 1 });

      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(result).toEqual({ success: true });
    });

    it('should timeout after specified duration', async () => {
      jest.useFakeTimers();

      (global.fetch as jest.Mock).mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 5000);
          })
      );

      const promise = apiClient.get('/test', { timeout: 1000 });

      jest.advanceTimersByTime(1000);

      await expect(promise).rejects.toThrow();

      jest.useRealTimers();
    });
  });

  describe('Type safety', () => {
    it('should return typed responses', async () => {
      interface User {
        id: number;
        name: string;
        email: string;
      }

      const mockUser: User = {
        id: 1,
        name: 'John Doe',
        email: 'john@example.com',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser,
      });

      const result = await apiClient.get<User>('/users/1');

      // TypeScript should infer the correct type
      expect(result.id).toBe(1);
      expect(result.name).toBe('John Doe');
      expect(result.email).toBe('john@example.com');
    });
  });
});
