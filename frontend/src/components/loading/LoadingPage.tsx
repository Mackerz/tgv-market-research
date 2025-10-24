import LoadingSpinner from './LoadingSpinner';

interface LoadingPageProps {
  message?: string;
}

/**
 * Loading Page Component
 *
 * Full-page loading state for route transitions or initial page loads.
 *
 * @example
 * ```tsx
 * <LoadingPage message="Loading report..." />
 * ```
 */
export function LoadingPage({ message = 'Loading...' }: LoadingPageProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <LoadingSpinner size="xl" color="primary" className="mx-auto" />
        <p className="mt-6 text-lg text-gray-600">{message}</p>
      </div>
    </div>
  );
}

export default LoadingPage;
