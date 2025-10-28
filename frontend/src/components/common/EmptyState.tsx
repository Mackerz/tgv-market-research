/**
 * EmptyState Component
 * Reusable empty state UI
 */

interface EmptyStateProps {
  icon?: string;
  title: string;
  message?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  fullScreen?: boolean;
}

export default function EmptyState({
  icon = '📭',
  title,
  message,
  action,
  fullScreen = false
}: EmptyStateProps) {
  const containerClass = fullScreen
    ? "min-h-screen bg-gray-50 flex items-center justify-center"
    : "flex items-center justify-center py-12";

  return (
    <div className={containerClass}>
      <div className="text-center max-w-md px-4">
        <div className="text-6xl mb-4">{icon}</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        {message && <p className="text-gray-600 mb-6">{message}</p>}

        {action && (
          <button
            onClick={action.onClick}
            className="px-6 py-2 bg-[#D01A8A] text-white rounded hover:bg-[#D01A8A] transition-colors"
          >
            {action.label}
          </button>
        )}
      </div>
    </div>
  );
}
