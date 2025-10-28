interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'white';
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
  xl: 'h-16 w-16 border-4',
};

const colorClasses = {
  primary: 'border-[#D01A8A] border-t-transparent',
  secondary: 'border-gray-600 border-t-transparent',
  white: 'border-white border-t-transparent',
};

/**
 * Loading Spinner Component
 *
 * Displays an animated spinning circle to indicate loading state.
 *
 * @example
 * ```tsx
 * <LoadingSpinner size="md" color="primary" />
 * ```
 */
export function LoadingSpinner({
  size = 'md',
  color = 'primary',
  className = '',
}: LoadingSpinnerProps) {
  return (
    <div
      className={`
        animate-spin rounded-full
        ${sizeClasses[size]}
        ${colorClasses[color]}
        ${className}
      `}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
}

export default LoadingSpinner;
