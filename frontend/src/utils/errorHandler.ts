/**
 * Global Error Handler Utilities
 * Filters out browser extension errors and provides clean error logging
 */

/**
 * Check if error is from a browser extension
 */
export const isExtensionError = (error: Error | ErrorEvent): boolean => {
  const errorString = error.toString();
  const stack = error instanceof Error ? error.stack : '';

  // Check for extension URLs in error message or stack
  const extensionPatterns = [
    /chrome-extension:\/\//,
    /moz-extension:\/\//,
    /safari-extension:\/\//,
    /webkit-masked-url:\/\//,
  ];

  return extensionPatterns.some(pattern =>
    pattern.test(errorString) || (stack && pattern.test(stack))
  );
};

/**
 * Check if error is from external script (ads, analytics, etc.)
 */
export const isExternalScriptError = (error: ErrorEvent): boolean => {
  if (!error.filename) return false;

  const externalPatterns = [
    /googletagmanager\.com/,
    /google-analytics\.com/,
    /doubleclick\.net/,
    /facebook\.net/,
    /adnxs\.com/,
  ];

  return externalPatterns.some(pattern => pattern.test(error.filename || ''));
};

/**
 * Filter errors that should not be logged
 */
export const shouldIgnoreError = (error: Error | ErrorEvent): boolean => {
  // Ignore extension errors
  if (isExtensionError(error)) {
    return true;
  }

  // Ignore external script errors in production
  if (import.meta.env.PROD && error instanceof ErrorEvent && isExternalScriptError(error)) {
    return true;
  }

  // Ignore ResizeObserver errors (harmless browser quirks)
  const message = error instanceof Error ? error.message : error.message || '';
  if (/ResizeObserver loop/.test(message)) {
    return true;
  }

  return false;
};

/**
 * Setup global error handlers
 */
export const setupGlobalErrorHandlers = () => {
  // Handle uncaught errors
  window.addEventListener('error', (event: ErrorEvent) => {
    if (shouldIgnoreError(event)) {
      event.preventDefault(); // Prevent default browser error handling
      return;
    }

    // Log actual application errors
    if (import.meta.env.DEV) {
      console.error('🚨 Uncaught Error:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
      });
    } else {
      // In production, send to error tracking service (e.g., Sentry)
      console.error('Application Error:', event.message);
    }
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event: PromiseRejectionEvent) => {
    const error = event.reason;

    if (error instanceof Error && shouldIgnoreError(error)) {
      event.preventDefault();
      return;
    }

    if (import.meta.env.DEV) {
      console.error('🚨 Unhandled Promise Rejection:', {
        reason: event.reason,
        promise: event.promise,
      });
    } else {
      console.error('Promise Rejection:', event.reason);
    }
  });

  if (import.meta.env.DEV) {
    console.log('✅ Global error handlers initialized');
  }
};

/**
 * Safe console.error wrapper that filters extension errors
 */
export const safeConsoleError = (...args: unknown[]) => {
  const firstArg = args[0];

  // Check if first argument looks like an extension error
  if (typeof firstArg === 'string' && /chrome-extension|moz-extension/.test(firstArg)) {
    if (import.meta.env.DEV) {
      console.log('🔇 Suppressed extension error:', firstArg);
    }
    return;
  }

  if (firstArg instanceof Error && isExtensionError(firstArg)) {
    if (import.meta.env.DEV) {
      console.log('🔇 Suppressed extension error:', firstArg.message);
    }
    return;
  }

  // Log actual application errors
  console.error(...args);
};
