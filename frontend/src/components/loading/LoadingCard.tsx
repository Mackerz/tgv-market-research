import LoadingSpinner from './LoadingSpinner';

interface LoadingCardProps {
  message?: string;
  className?: string;
}

/**
 * Loading Card Component
 *
 * Displays a card-style loading state with spinner and optional message.
 * Useful for loading states within card layouts.
 *
 * @example
 * ```tsx
 * <LoadingCard message="Loading survey data..." />
 * ```
 */
export function LoadingCard({ message = 'Loading...', className = '' }: LoadingCardProps) {
  return (
    <div className={`bg-white rounded-lg shadow p-8 ${className}`}>
      <div className="flex flex-col items-center justify-center">
        <LoadingSpinner size="lg" color="primary" />
        <p className="mt-4 text-gray-600 text-center">{message}</p>
      </div>
    </div>
  );
}

export default LoadingCard;
