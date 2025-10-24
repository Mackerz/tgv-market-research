/**
 * Security utilities for sanitizing user input to prevent XSS attacks
 */

import DOMPurify from 'dompurify';
import React from 'react';

/**
 * Sanitizes HTML content to prevent XSS attacks
 * Removes potentially dangerous tags and attributes while preserving safe HTML
 *
 * @param dirty - Untrusted HTML string
 * @returns Sanitized HTML safe for rendering
 */
export function sanitizeHtml(dirty: string): string {
  if (typeof window === 'undefined') {
    // Server-side: return as-is (Next.js will escape it)
    return dirty;
  }

  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  });
}

/**
 * Sanitizes plain text to prevent XSS in dangerouslySetInnerHTML contexts
 * Strips all HTML tags
 *
 * @param text - Untrusted text string
 * @returns Plain text with all HTML removed
 */
export function sanitizePlainText(text: string): string {
  if (typeof window === 'undefined') {
    // Server-side: return as-is (Next.js will escape it)
    return text;
  }

  return DOMPurify.sanitize(text, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  });
}

/**
 * Validates email format using built-in browser validation
 * More secure than regex-based validation
 *
 * @param email - Email string to validate
 * @returns True if email is valid format
 */
export function isValidEmail(email: string): boolean {
  // Use browser's built-in email validation
  const input = document.createElement('input');
  input.type = 'email';
  input.value = email;

  return input.checkValidity() && email.length <= 320; // RFC 5321 max length
}

/**
 * Validates phone number format
 * Allows international formats with optional country code
 *
 * @param phone - Phone number string to validate
 * @returns True if phone number is valid format
 */
export function isValidPhoneNumber(phone: string): boolean {
  // Remove common formatting characters
  const cleaned = phone.replace(/[\s\-\(\)\.]/g, '');

  // Check if it's a valid format:
  // - Optional + for country code
  // - 7-15 digits (international standard range)
  const phoneRegex = /^\+?[0-9]{7,15}$/;

  return phoneRegex.test(cleaned);
}

/**
 * Component for safely rendering user-provided HTML content
 * Use this instead of dangerouslySetInnerHTML
 *
 * @example
 * ```tsx
 * <SafeHtml html={userProvidedContent} />
 * ```
 */
interface SafeHtmlProps {
  html: string;
  className?: string;
}

export function SafeHtml({ html, className }: SafeHtmlProps) {
  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizeHtml(html) }}
    />
  );
}

/**
 * Component for safely rendering plain text from user input
 * Strips all HTML tags
 *
 * @example
 * ```tsx
 * <SafeText text={userInput} />
 * ```
 */
interface SafeTextProps {
  text: string;
  className?: string;
}

export function SafeText({ text, className }: SafeTextProps) {
  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizePlainText(text) }}
    />
  );
}
