import React from 'react';
import { Submission } from './types';

/**
 * Format date string to localized format
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

/**
 * Get status badge element for submission
 */
export function getStatusBadge(submission: Submission): React.ReactElement {
  if (submission.is_approved === null) {
    return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Pending</span>;
  } else if (submission.is_approved === true) {
    return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Approved</span>;
  } else {
    return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Rejected</span>;
  }
}

/**
 * Get status label for filter button
 */
export function getStatusLabel(status: boolean | null): string {
  if (status === null) return 'Pending';
  return status ? 'Approved' : 'Rejected';
}

/**
 * Get status color classes
 */
export function getStatusClasses(status: boolean | null): string {
  if (status === null) return 'bg-yellow-100 text-yellow-800';
  return status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
}
