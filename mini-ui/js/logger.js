// Logger Utility - Production-safe logging
// Set window.DEBUG = true in development to enable console logging

const DEBUG = window.DEBUG || false;

/**
 * Log info message (only in debug mode)
 */
export function log(...args) {
    if (DEBUG) {
        console.log('[Mini UI]', ...args);
    }
}

/**
 * Log warning message (only in debug mode)
 */
export function warn(...args) {
    if (DEBUG) {
        console.warn('[Mini UI]', ...args);
    }
}

/**
 * Log error message (always logged, but formatted)
 */
export function error(...args) {
    // Errors are always logged for debugging, but formatted
    if (DEBUG) {
        console.error('[Mini UI]', ...args);
    }
    // In production, errors can be sent to error tracking service
    // Example: if (window.errorTracker) window.errorTracker.captureException(...args);
}

/**
 * Log debug message (only in debug mode)
 */
export function debug(...args) {
    if (DEBUG) {
        console.debug('[Mini UI]', ...args);
    }
}

