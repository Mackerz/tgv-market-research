/**
 * ErrorState Component
 * Reusable error state UI with optional retry
 */

import { useRouter } from 'next/navigation';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  showHomeButton?: boolean;
  fullScreen?: boolean;
}

export default function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
  showHomeButton = true,
  fullScreen = true
}: ErrorStateProps) {
  const router = useRouter();

  const containerClass = fullScreen
    ? "min-h-screen bg-gray-50 flex items-center justify-center"
    : "flex items-center justify-center py-12";

  return (
    <div className={containerClass}>
      <div className="text-center max-w-md px-4">
        <div className="text-6xl mb-4">❌</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-600 mb-6">{message}</p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-6 py-2 bg-[#D01A8A] text-white rounded hover:bg-[#D01A8A] transition-colors"
            >
              Try Again
            </button>
          )}

          {showHomeButton && (
            <button
              onClick={() => router.push('/')}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
            >
              Go Home
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
