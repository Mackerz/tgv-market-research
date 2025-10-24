'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '@/lib/logger';

interface Props {
  children: ReactNode;
  componentName?: string;
  fallbackUI?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Component-level Error Boundary
 *
 * Catches errors in specific components without affecting the rest of the page.
 * Useful for wrapping complex components like charts, media galleries, etc.
 *
 * @example
 * ```tsx
 * <ComponentErrorBoundary componentName="Media Gallery">
 *   <MediaGallery />
 * </ComponentErrorBoundary>
 * ```
 */
export class ComponentErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error(`ComponentErrorBoundary${this.props.componentName ? ` (${this.props.componentName})` : ''} caught an error`, error, {
      componentStack: errorInfo.componentStack,
      componentName: this.props.componentName
    });
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback UI if provided
      if (this.props.fallbackUI) {
        return this.props.fallbackUI;
      }

      // Default inline error UI
      return (
        <div className="border border-red-200 bg-red-50 rounded-lg p-4 my-4">
          <div className="flex items-start">
            <svg
              className="h-5 w-5 text-red-600 mt-0.5 mr-3 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-red-900 mb-1">
                {this.props.componentName ? `${this.props.componentName} Error` : 'Component Error'}
              </h3>
              <p className="text-sm text-red-800 mb-3">
                This component encountered an error and cannot be displayed.
              </p>

              {process.env.NODE_ENV === 'development' && (
                <div className="mb-3 p-2 bg-red-100 border border-red-300 rounded text-xs">
                  <p className="text-red-900 font-mono">{this.state.error.message}</p>
                </div>
              )}

              <button
                onClick={this.reset}
                className="text-sm text-red-700 hover:text-red-900 font-medium underline"
              >
                Try reloading this component
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ComponentErrorBoundary;
