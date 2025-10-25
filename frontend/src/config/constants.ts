/**
 * Application-wide constants and configuration values
 *
 * Centralizes magic numbers, limits, and other constants
 * for easier maintenance and configuration.
 */

// =============================================================================
// PAGINATION CONSTANTS
// =============================================================================

export const DEFAULT_PAGE_SIZE = 100;
export const MAX_PAGE_SIZE = 1000;

// =============================================================================
// MEDIA & PREVIEW CONSTANTS
// =============================================================================

export const DEFAULT_MEDIA_PREVIEW_LIMIT = 5;
export const MAX_MEDIA_PREVIEW_LIMIT = 20;

// =============================================================================
// FILE UPLOAD CONSTANTS
// =============================================================================

export const MAX_UPLOAD_SIZE_MB = 50;
export const MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024;

export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
export const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo'];

// =============================================================================
// API TIMEOUT CONSTANTS
// =============================================================================

export const DEFAULT_API_TIMEOUT_MS = 30000;  // 30 seconds
export const UPLOAD_API_TIMEOUT_MS = 120000;  // 2 minutes for uploads
export const REPORTING_API_TIMEOUT_MS = 60000; // 1 minute for reports

// =============================================================================
// TAXONOMY CONSTANTS
// =============================================================================

export const DEFAULT_TAXONOMY_CATEGORIES = 6;
export const MAX_TAXONOMY_CATEGORIES = 20;

// =============================================================================
// UI/UX CONSTANTS
// =============================================================================

export const DEBOUNCE_DELAY_MS = 300;
export const TOAST_DURATION_MS = 3000;
export const MODAL_ANIMATION_DURATION_MS = 200;

// =============================================================================
// VALIDATION CONSTANTS
// =============================================================================

export const MIN_PASSWORD_LENGTH = 8;
export const MAX_PASSWORD_LENGTH = 128;

export const MIN_SURVEY_NAME_LENGTH = 3;
export const MAX_SURVEY_NAME_LENGTH = 200;

export const MAX_QUESTION_TEXT_LENGTH = 500;
export const MAX_FREE_TEXT_RESPONSE_LENGTH = 2000;

// =============================================================================
// CACHE CONSTANTS
// =============================================================================

export const SURVEY_DATA_CACHE_MS = 300000;  // 5 minutes
export const REPORTING_DATA_CACHE_MS = 60000; // 1 minute

// =============================================================================
// RETRY CONSTANTS
// =============================================================================

export const MAX_RETRY_ATTEMPTS = 3;
export const RETRY_DELAY_MS = 1000;

// =============================================================================
// ENVIRONMENT CONSTANTS
// =============================================================================

export const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';
export const IS_PRODUCTION = process.env.NODE_ENV === 'production';
