import { useState, useEffect } from 'react';
import { apiClient, ApiError } from '@/lib/api';
import { apiUrl } from '@/config/api';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import {
  SubmissionsResponse,
  SubmissionDetailResponse,
  ReportingData,
  ApprovalFilter,
  SortBy
} from '@/components/report/types';

/**
 * Custom hook for managing report data fetching
 * Handles submissions, submission details, and reporting data
 */
export function useReportData(reportSlug: string) {
  // Error handling using new reusable hook
  const { error, handleError, setError } = useErrorHandler();

  // Submissions state
  const [submissions, setSubmissions] = useState<SubmissionsResponse | null>(null);
  const [selectedSubmission, setSelectedSubmission] = useState<SubmissionDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // Filtering and sorting
  const [approvalFilter, setApprovalFilter] = useState<ApprovalFilter>('all');
  const [sortBy, setSortBy] = useState<SortBy>('submitted_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Reporting state
  const [reportingData, setReportingData] = useState<ReportingData | null>(null);
  const [reportingLoading, setReportingLoading] = useState(false);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      let approved: string | undefined = undefined;

      if (approvalFilter === 'approved') {
        approved = 'true';
      } else if (approvalFilter === 'rejected') {
        approved = 'false';
      } else if (approvalFilter === 'pending') {
        approved = 'null';
      }

      const params: Record<string, string> = {
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      if (approved !== undefined) {
        params.approved = approved;
      }

      const data = await apiClient.get<SubmissionsResponse>(
        `/api/reports/${reportSlug}/submissions`,
        { params }
      );
      setSubmissions(data);
      setError(null);
    } catch (err) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubmissionDetail = async (submissionId: number) => {
    try {
      const data = await apiClient.get<SubmissionDetailResponse>(
        `/api/reports/${reportSlug}/submissions/${submissionId}`
      );
      setSelectedSubmission(data);
      setError(null);
    } catch (err) {
      handleError(err);
    }
  };

  const handleApproveSubmission = async (submissionId: number) => {
    try {
      await apiClient.put(`/api/reports/${reportSlug}/submissions/${submissionId}/approve`);

      // Refresh submissions list and selected submission
      await fetchSubmissions();
      if (selectedSubmission?.submission.id === submissionId) {
        await fetchSubmissionDetail(submissionId);
      }
      setError(null);
    } catch (err) {
      handleError(err);
    }
  };

  const handleRejectSubmission = async (submissionId: number) => {
    try {
      await apiClient.put(`/api/reports/${reportSlug}/submissions/${submissionId}/reject`);

      // Refresh submissions list and selected submission
      await fetchSubmissions();
      if (selectedSubmission?.submission.id === submissionId) {
        await fetchSubmissionDetail(submissionId);
      }
      setError(null);
    } catch (err) {
      handleError(err);
    }
  };

  const fetchReportingData = async () => {
    try {
      setReportingLoading(true);
      const data = await apiClient.get<ReportingData>(
        `/api/reports/${reportSlug}/data`
      );
      setReportingData(data);
      setError(null);
    } catch (err) {
      handleError(err);
    } finally {
      setReportingLoading(false);
    }
  };

  // Fetch submissions when filters change
  useEffect(() => {
    fetchSubmissions();
  }, [reportSlug, approvalFilter, sortBy, sortOrder]);

  return {
    // Submissions data
    submissions,
    selectedSubmission,
    loading,
    error,

    // Filters
    approvalFilter,
    setApprovalFilter,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,

    // Actions
    fetchSubmissions,
    fetchSubmissionDetail,
    handleApproveSubmission,
    handleRejectSubmission,
    setSelectedSubmission,
    setError,

    // Reporting data
    reportingData,
    reportingLoading,
    fetchReportingData,
  };
}
