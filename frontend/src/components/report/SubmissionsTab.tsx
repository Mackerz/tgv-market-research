import { useState } from 'react';
import {
  SubmissionsResponse,
  SubmissionDetailResponse,
  ApprovalFilter,
  SortBy
} from './types';
import { formatDate, getStatusBadge } from './utils';
import SubmissionDetail from './SubmissionDetail';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { reportingService } from '@/lib/api/services/reporting';
import { surveyService } from '@/lib/api';
import { logger } from '@/lib/logger';

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
  const [exporting, setExporting] = useState(false);

  /**
   * Export submissions to CSV with all questions and responses
   */
  const handleExportCSV = async () => {
    if (!submissions || submissions.submissions.length === 0) {
      alert('No submissions to export');
      return;
    }

    try {
      setExporting(true);

      // 1. Fetch full survey details to get all questions
      const surveyData = await surveyService.getSurveyBySlug(submissions.survey.survey_slug);
      const questions = surveyData.survey_flow || [];

      // 2. Fetch all submission details with responses
      const submissionDetails = await Promise.all(
        submissions.submissions.map(submission =>
          reportingService.getSubmissionDetail(submissions.survey.survey_slug, submission.id)
        )
      );

      // 3. Define CSV headers - basic info + all questions
      const basicHeaders = [
        'ID',
        'Email',
        'Phone Number',
        'Region',
        'Gender',
        'Age',
        'Submitted At',
        'Status',
        'Completed'
      ];

      const questionHeaders = questions.map(q => q.question);
      const headers = [...basicHeaders, ...questionHeaders];

      // 4. Create CSV rows
      const rows = submissionDetails.map(detail => {
        const submission = detail.submission;
        const responses = detail.responses;

        // Basic info
        const status = submission.is_approved === null
          ? 'Pending'
          : submission.is_approved
            ? 'Approved'
            : 'Rejected';

        const basicInfo = [
          submission.id,
          submission.email,
          submission.phone_number,
          submission.region,
          submission.gender,
          submission.age,
          new Date(submission.submitted_at).toLocaleString(),
          status,
          submission.is_completed ? 'Yes' : 'No'
        ];

        // Map responses to questions
        const responseMap = new Map(
          responses.map(r => [r.question, r])
        );

        const questionResponses = questions.map(q => {
          const response = responseMap.get(q.question);
          if (!response) return '';

          // Format response based on type
          switch (response.question_type) {
            case 'single':
              return response.single_answer || '';
            case 'multi':
              return response.multiple_choice_answer?.join('; ') || '';
            case 'free_text':
              return response.free_text_answer || '';
            case 'photo':
              return response.photo_url || '';
            case 'video':
              return response.video_url || '';
            default:
              return '';
          }
        });

        return [...basicInfo, ...questionResponses];
      });

      // 5. Create CSV content with proper escaping
      const escapeCsvCell = (cell: any): string => {
        const cellStr = String(cell);
        // Escape cells containing commas, quotes, or newlines
        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
          return `"${cellStr.replace(/"/g, '""')}"`;
        }
        return cellStr;
      };

      const csvContent = [
        headers.map(escapeCsvCell).join(','),
        ...rows.map(row => row.map(escapeCsvCell).join(','))
      ].join('\n');

      // 6. Create blob and download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${submissions.survey.survey_slug}-submissions-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      logger.error('Error exporting CSV:', error);
      alert('Failed to export CSV. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex space-x-6">
      {/* Submissions Table */}
      <div className={selectedSubmission ? 'w-1/2' : 'w-full'}>
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Submissions</h2>

              {/* Export CSV Button */}
              <button
                onClick={handleExportCSV}
                disabled={!submissions || submissions.submissions.length === 0 || exporting}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                title="Export submissions with all questions to CSV"
              >
                {exporting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Exporting...</span>
                  </>
                ) : (
                  <>
                    <ArrowDownTrayIcon className="h-5 w-5" />
                    <span>Export CSV</span>
                  </>
                )}
              </button>
            </div>

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
