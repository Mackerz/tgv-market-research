/**
 * LoadingState Component
 * Reusable loading state UI
 */

interface LoadingStateProps {
  message?: string;
  fullScreen?: boolean;
}

export default function LoadingState({
  message = 'Loading...',
  fullScreen = true
}: LoadingStateProps) {
  const containerClass = fullScreen
    ? "min-h-screen bg-gray-50 flex items-center justify-center"
    : "flex items-center justify-center py-12";

  return (
    <div className={containerClass}>
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#D01A8A] mx-auto mb-4"></div>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
}
