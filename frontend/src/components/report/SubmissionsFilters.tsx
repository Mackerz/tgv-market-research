/**
 * SubmissionsFilters Component
 * Filters and sorting controls for submissions list
 */

import type { ApprovalFilter, SortBy } from '@/types';

interface SubmissionsFiltersProps {
  approvalFilter: ApprovalFilter;
  sortBy: SortBy;
  sortOrder: 'asc' | 'desc';
  onApprovalFilterChange: (filter: ApprovalFilter) => void;
  onSortByChange: (sortBy: SortBy) => void;
  onSortOrderChange: (order: 'asc' | 'desc') => void;
}

export default function SubmissionsFilters({
  approvalFilter,
  sortBy,
  sortOrder,
  onApprovalFilterChange,
  onSortByChange,
  onSortOrderChange,
}: SubmissionsFiltersProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
      {/* Approval Filter */}
      <div className="flex items-center space-x-2">
        <label className="text-sm font-medium text-gray-700">Filter:</label>
        <select
          value={approvalFilter}
          onChange={(e) => onApprovalFilterChange(e.target.value as ApprovalFilter)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#D01A8A]"
        >
          <option value="all">All</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      {/* Sort By */}
      <div className="flex items-center space-x-2">
        <label className="text-sm font-medium text-gray-700">Sort by:</label>
        <select
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value as SortBy)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-[#D01A8A]"
        >
          <option value="submitted_at">Date Submitted</option>
          <option value="email">Email</option>
          <option value="age">Age</option>
          <option value="region">Region</option>
        </select>
      </div>

      {/* Sort Order */}
      <button
        onClick={() => onSortOrderChange(sortOrder === 'asc' ? 'desc' : 'asc')}
        className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
        title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
      >
        {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
      </button>
    </div>
  );
}
