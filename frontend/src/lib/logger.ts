/**
 * Logger Utility
 *
 * Centralized logging utility that respects environment settings.
 * Replaces direct console.log/error/warn calls throughout the application.
 *
 * Features:
 * - Environment-aware (suppresses debug logs in production)
 * - Structured log format with timestamps
 * - Integration-ready for external logging services (Sentry, Datadog, etc.)
 * - Type-safe error logging
 *
 * @example
 * ```typescript
 * import { logger } from '@/lib/logger';
 *
 * logger.debug('User clicked button', { buttonId: 'submit' });
 * logger.info('Survey submitted successfully');
 * logger.warn('Slow network detected');
 * logger.error('Failed to fetch data', error);
 * ```
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: unknown;
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development';
  private isTest = process.env.NODE_ENV === 'test';

  /**
   * Format log message with timestamp and context
   */
  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  /**
   * Debug-level logging
   * Only shown in development environment
   */
  debug(message: string, context?: LogContext): void {
    if (this.isDevelopment && !this.isTest) {
      console.log(this.formatMessage('debug', message, context));
    }
  }

  /**
   * Info-level logging
   * Shown in all environments
   */
  info(message: string, context?: LogContext): void {
    if (!this.isTest) {
      console.info(this.formatMessage('info', message, context));
    }
  }

  /**
   * Warning-level logging
   * Shown in all environments
   */
  warn(message: string, context?: LogContext): void {
    if (!this.isTest) {
      console.warn(this.formatMessage('warn', message, context));
    }
    // TODO: Send to monitoring service in production
    // if (!this.isDevelopment) {
    //   this.sendToMonitoringService('warn', message, context);
    // }
  }

  /**
   * Error-level logging
   * Always shown and sent to monitoring services
   */
  error(message: string, error?: Error | unknown, context?: LogContext): void {
    const errorDetails = error instanceof Error
      ? { message: error.message, stack: error.stack, ...context }
      : { error, ...context };

    if (!this.isTest) {
      console.error(this.formatMessage('error', message, errorDetails));
    }

    // TODO: Send to error tracking service (Sentry, etc.)
    // this.sendToErrorTracking(message, error, context);
  }

  /**
   * Performance timing helper
   */
  time(label: string): void {
    if (this.isDevelopment) {
      console.time(label);
    }
  }

  /**
   * End performance timing
   */
  timeEnd(label: string): void {
    if (this.isDevelopment) {
      console.timeEnd(label);
    }
  }

  /**
   * Group related logs together (development only)
   */
  group(label: string): void {
    if (this.isDevelopment && !this.isTest) {
      console.group(label);
    }
  }

  /**
   * End log group
   */
  groupEnd(): void {
    if (this.isDevelopment && !this.isTest) {
      console.groupEnd();
    }
  }

  /**
   * Log table data (development only)
   */
  table(data: unknown): void {
    if (this.isDevelopment && !this.isTest) {
      console.table(data);
    }
  }

  // TODO: Implement these methods when integrating monitoring services

  // private sendToMonitoringService(level: LogLevel, message: string, context?: LogContext): void {
  //   // Send to Datadog, CloudWatch, etc.
  // }

  // private sendToErrorTracking(message: string, error?: Error | unknown, context?: LogContext): void {
  //   // Send to Sentry, Rollbar, etc.
  //   // Example for Sentry:
  //   // Sentry.captureException(error, {
  //   //   tags: { ...context },
  //   //   extra: { message }
  //   // });
  // }
}

// Export singleton instance
export const logger = new Logger();

// For testing purposes
export type { LogLevel, LogContext };
export { Logger };
