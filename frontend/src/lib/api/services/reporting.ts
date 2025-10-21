/**
 * Reporting API Service
 * All reporting-related API calls
 */

import { apiClient } from '../client';
import type {
  SubmissionsResponse,
  SubmissionDetailResponse,
  ReportingData,
  ReportSettings,
  AgeRange,
  MediaGalleryResponse,
  ApprovalFilter,
  SortBy,
  SortOrder,
} from '@/types';

export const reportingService = {
  /**
   * Get submissions for a survey
   */
  getSubmissions: (
    surveySlug: string,
    params?: {
      approved?: ApprovalFilter;
      sort_by?: SortBy;
      sort_order?: SortOrder;
      skip?: number;
      limit?: number;
    }
  ) => {
    // Convert approval filter to API format
    const apiParams: Record<string, string | number | undefined> = {};

    // Copy all params except approved
    if (params) {
      Object.keys(params).forEach(key => {
        if (key !== 'approved') {
          apiParams[key] = params[key as keyof typeof params];
        }
      });

      // Handle approved filter conversion
      if (params.approved && params.approved !== 'all') {
        if (params.approved === 'pending') {
          apiParams.approved = 'null';
        } else if (params.approved === 'approved') {
          apiParams.approved = 'true';
        } else if (params.approved === 'rejected') {
          apiParams.approved = 'false';
        }
      }
    }

    return apiClient.get<SubmissionsResponse>(
      `/api/reports/${surveySlug}/submissions`,
      { params: apiParams }
    );
  },

  /**
   * Get submission detail
   */
  getSubmissionDetail: (surveySlug: string, submissionId: number) => {
    return apiClient.get<SubmissionDetailResponse>(
      `/api/reports/${surveySlug}/submissions/${submissionId}`
    );
  },

  /**
   * Approve a submission
   */
  approveSubmission: (surveySlug: string, submissionId: number) => {
    return apiClient.put(
      `/api/reports/${surveySlug}/submissions/${submissionId}/approve`
    );
  },

  /**
   * Reject a submission
   */
  rejectSubmission: (surveySlug: string, submissionId: number) => {
    return apiClient.put(
      `/api/reports/${surveySlug}/submissions/${submissionId}/reject`
    );
  },

  /**
   * Get reporting data (charts and analytics)
   */
  getReportingData: (surveySlug: string) => {
    return apiClient.get<ReportingData>(`/api/reports/${surveySlug}/data`);
  },

  /**
   * Get media gallery
   */
  getMediaGallery: (
    surveySlug: string,
    params?: {
      labels?: string;
      regions?: string;
      genders?: string;
      age_min?: number;
      age_max?: number;
    }
  ) => {
    return apiClient.get<MediaGalleryResponse>(
      `/api/reports/${surveySlug}/media-gallery`,
      { params }
    );
  },

  /**
   * Get report settings
   */
  getSettings: (surveySlug: string) => {
    return apiClient.get<ReportSettings>(`/api/reports/${surveySlug}/settings`);
  },

  /**
   * Update age ranges
   */
  updateAgeRanges: (surveySlug: string, ageRanges: AgeRange[]) => {
    return apiClient.put(`/api/reports/${surveySlug}/settings/age-ranges`, {
      age_ranges: ageRanges,
    });
  },

  /**
   * Update question display names (bulk)
   */
  updateQuestionDisplayNames: (
    surveySlug: string,
    updates: Array<{ question_id: string; display_name: string }>
  ) => {
    return apiClient.put(`/api/reports/${surveySlug}/settings/question-display-names`, {
      question_updates: updates,
    });
  },

  /**
   * Update single question display name
   */
  updateQuestionDisplayName: (
    surveySlug: string,
    questionId: string,
    displayName: string
  ) => {
    return apiClient.put(
      `/api/reports/${surveySlug}/settings/question-display-names/${questionId}`,
      { display_name: displayName }
    );
  },
};
