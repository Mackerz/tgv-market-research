interface LoadingSkeletonProps {
  type?: 'text' | 'title' | 'card' | 'table' | 'chart';
  rows?: number;
  className?: string;
}

/**
 * Loading Skeleton Component
 *
 * Displays placeholder content shapes while data is loading.
 * Provides better UX than spinners for content-heavy areas.
 *
 * @example
 * ```tsx
 * <LoadingSkeleton type="table" rows={5} />
 * <LoadingSkeleton type="card" />
 * ```
 */
export function LoadingSkeleton({ type = 'text', rows = 3, className = '' }: LoadingSkeletonProps) {
  const baseClass = 'animate-pulse bg-gray-200 rounded';

  if (type === 'text') {
    return (
      <div className={`space-y-3 ${className}`}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={`h-4 ${baseClass}`} style={{ width: `${80 + Math.random() * 20}%` }} />
        ))}
      </div>
    );
  }

  if (type === 'title') {
    return <div className={`h-8 w-1/2 ${baseClass} ${className}`} />;
  }

  if (type === 'card') {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className={`h-6 w-1/3 ${baseClass} mb-4`} />
        <div className="space-y-3">
          <div className={`h-4 w-full ${baseClass}`} />
          <div className={`h-4 w-5/6 ${baseClass}`} />
          <div className={`h-4 w-4/6 ${baseClass}`} />
        </div>
      </div>
    );
  }

  if (type === 'table') {
    return (
      <div className={`space-y-3 ${className}`}>
        {/* Header */}
        <div className={`h-10 w-full ${baseClass}`} />
        {/* Rows */}
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={`h-16 w-full ${baseClass}`} />
        ))}
      </div>
    );
  }

  if (type === 'chart') {
    return (
      <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
        <div className={`h-6 w-1/4 ${baseClass} mb-6`} />
        <div className="flex items-end justify-around h-64 space-x-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className={baseClass}
              style={{ height: `${40 + Math.random() * 60}%`, width: '15%' }}
            />
          ))}
        </div>
      </div>
    );
  }

  return null;
}

export default LoadingSkeleton;
