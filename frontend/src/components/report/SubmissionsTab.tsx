import {
  SubmissionsResponse,
  SubmissionDetailResponse,
  ApprovalFilter,
  SortBy
} from './types';
import { formatDate, getStatusBadge } from './utils';
import SubmissionDetail from './SubmissionDetail';

interface SubmissionsTabProps {
  submissions: SubmissionsResponse | null;
  selectedSubmission: SubmissionDetailResponse | null;
  approvalFilter: ApprovalFilter;
  sortBy: SortBy;
  sortOrder: 'asc' | 'desc';
  onApprovalFilterChange: (filter: ApprovalFilter) => void;
  onSortByChange: (sortBy: SortBy) => void;
  onSortOrderChange: (order: 'asc' | 'desc') => void;
  onSubmissionClick: (id: number) => void;
  onCloseDetail: () => void;
  onApprove: (id: number) => Promise<void>;
  onReject: (id: number) => Promise<void>;
}

/**
 * Submissions Tab Component
 *
 * Displays a table of submissions with filtering, sorting, and detail view
 */
export function SubmissionsTab({
  submissions,
  selectedSubmission,
  approvalFilter,
  sortBy,
  sortOrder,
  onApprovalFilterChange,
  onSortByChange,
  onSortOrderChange,
  onSubmissionClick,
  onCloseDetail,
  onApprove,
  onReject
}: SubmissionsTabProps) {
  return (
    <div className="flex space-x-6">
      {/* Submissions Table */}
      <div className={selectedSubmission ? 'w-1/2' : 'w-full'}>
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Submissions</h2>

            {/* Filters */}
            <div className="mt-4 flex space-x-4">
              <select
                value={approvalFilter}
                onChange={(e) => onApprovalFilterChange(e.target.value as ApprovalFilter)}
                className="px-3 py-2 border rounded-md text-gray-900 bg-white"
              >
                <option value="all">All Submissions</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>

              <select
                value={sortBy}
                onChange={(e) => onSortByChange(e.target.value as SortBy)}
                className="px-3 py-2 border rounded-md text-gray-900 bg-white"
              >
                <option value="submitted_at">Date Submitted</option>
                <option value="email">Email</option>
                <option value="age">Age</option>
                <option value="region">Region</option>
              </select>

              <select
                value={sortOrder}
                onChange={(e) => onSortOrderChange(e.target.value as 'asc' | 'desc')}
                className="px-3 py-2 border rounded-md text-gray-900 bg-white"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Respondent
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Demographics
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Submitted
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {submissions?.submissions.map((submission) => (
                  <tr
                    key={submission.id}
                    onClick={() => onSubmissionClick(submission.id)}
                    className="hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {submission.email}
                        </div>
                        <div className="text-sm text-gray-500">
                          {submission.phone_number}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {submission.gender}, {submission.age}
                      </div>
                      <div className="text-sm text-gray-500">
                        {submission.region}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(submission.submitted_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(submission)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Submission Detail */}
      {selectedSubmission && (
        <div className="w-1/2">
          <SubmissionDetail
            submission={selectedSubmission.submission}
            responses={selectedSubmission.responses}
            onClose={onCloseDetail}
            onApprove={() => onApprove(selectedSubmission.submission.id)}
            onReject={() => onReject(selectedSubmission.submission.id)}
          />
        </div>
      )}
    </div>
  );
}

export default SubmissionsTab;
