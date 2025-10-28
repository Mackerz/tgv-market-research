'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { logger } from '@/lib/logger';

interface Props {
  children: ReactNode;
  routeName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Route-level Error Boundary
 *
 * Catches errors specific to a route/page without crashing the entire app.
 * Allows navigation to other routes even when one route has an error.
 *
 * @example
 * ```tsx
 * <RouteErrorBoundary routeName="Survey">
 *   <SurveyPage />
 * </RouteErrorBoundary>
 * ```
 */
class RouteErrorBoundaryClass extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error(`RouteErrorBoundary${this.props.routeName ? ` (${this.props.routeName})` : ''} caught an error`, error, {
      componentStack: errorInfo.componentStack,
      routeName: this.props.routeName
    });
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center mb-4">
              <svg
                className="h-8 w-8 text-orange-500 mr-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h1 className="text-2xl font-semibold text-gray-900">
                {this.props.routeName ? `${this.props.routeName} Error` : 'Page Error'}
              </h1>
            </div>

            <p className="text-gray-600 mb-6">
              This page encountered an error and cannot be displayed.
              {this.props.routeName && ` The ${this.props.routeName} feature is temporarily unavailable.`}
            </p>

            {process.env.NODE_ENV === 'development' && (
              <div className="mb-6 p-4 bg-orange-50 border border-orange-200 rounded-lg">
                <p className="text-sm font-semibold text-orange-900 mb-2">Development Error Details:</p>
                <p className="text-sm text-orange-800 font-mono whitespace-pre-wrap">
                  {this.state.error.message}
                </p>
                {this.state.error.stack && (
                  <details className="mt-2">
                    <summary className="text-xs text-orange-700 cursor-pointer hover:text-orange-900">
                      Show stack trace
                    </summary>
                    <pre className="text-xs text-orange-700 mt-2 overflow-x-auto">
                      {this.state.error.stack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            <div className="flex space-x-3">
              <button
                onClick={this.reset}
                className="flex-1 px-4 py-2 bg-[#D01A8A] text-white rounded-md hover:bg-[#B0156E] font-medium transition"
              >
                Try Again
              </button>
              <button
                onClick={() => window.history.back()}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 font-medium transition"
              >
                Go Back
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium transition"
              >
                Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export function RouteErrorBoundary(props: Props) {
  return <RouteErrorBoundaryClass {...props} />;
}

export default RouteErrorBoundary;
