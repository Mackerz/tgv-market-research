/**
 * SubmissionsList Component
 * Displays list of submissions with approve/reject actions
 */

import type { Submission } from '@/types';

interface SubmissionsListProps {
  submissions: Submission[];
  onViewDetail: (submissionId: number) => void;
  onApprove: (submissionId: number) => Promise<void>;
  onReject: (submissionId: number) => Promise<void>;
}

export default function SubmissionsList({
  submissions,
  onViewDetail,
  onApprove,
  onReject,
}: SubmissionsListProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getApprovalBadge = (isApproved: boolean | null) => {
    if (isApproved === null) {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
          Pending
        </span>
      );
    }
    if (isApproved) {
      return (
        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
          Approved
        </span>
      );
    }
    return (
      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
        Rejected
      </span>
    );
  };

  if (submissions.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No submissions found</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {submissions.map((submission) => (
        <div
          key={submission.id}
          className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            {/* Submission Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="font-semibold text-gray-900">
                  {submission.email}
                </h3>
                {getApprovalBadge(submission.is_approved)}
                {!submission.is_completed && (
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                    Incomplete
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Region:</span> {submission.region}
                </div>
                <div>
                  <span className="font-medium">Age:</span> {submission.age || 'N/A'}
                </div>
                <div>
                  <span className="font-medium">Submitted:</span>{' '}
                  {formatDate(submission.submitted_at)}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => onViewDetail(submission.id)}
                className="px-4 py-2 bg-[#D01A8A] text-white rounded-lg hover:bg-[#D01A8A] transition-colors text-sm font-medium"
              >
                View Details
              </button>

              {submission.is_approved === null && submission.is_completed && (
                <>
                  <button
                    onClick={() => onApprove(submission.id)}
                    className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => onReject(submission.id)}
                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
                  >
                    Reject
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
