/**
 * Taxonomy API Service
 * All taxonomy and reporting label-related API calls
 */

import { apiClient } from '../client';
import type {
  TaxonomyOverview,
  ReportingLabel,
  ReportingLabelCreate,
  ReportingLabelUpdate,
  AddSystemLabelRequest,
  RemoveSystemLabelRequest,
  GenerateTaxonomyRequest,
  MediaPreview,
} from '@/types/taxonomy';

export const taxonomyService = {
  /**
   * Get taxonomy overview for a survey, optionally filtered by question
   */
  getTaxonomy: (surveyId: number, questionId?: string) => {
    return apiClient.get<TaxonomyOverview>(`/api/surveys/${surveyId}/taxonomy`, {
      params: { question_id: questionId }
    });
  },

  /**
   * Generate AI taxonomy for a survey
   */
  generateTaxonomy: (surveyId: number, maxCategories?: number) => {
    const data: GenerateTaxonomyRequest = {
      survey_id: surveyId,
      max_categories: maxCategories,
    };
    return apiClient.post<TaxonomyOverview>(
      `/api/surveys/${surveyId}/taxonomy/generate`,
      data
    );
  },

  /**
   * Get media previews for a system label, optionally filtered by question
   */
  getMediaPreviews: (surveyId: number, systemLabel: string, limit?: number, questionId?: string) => {
    return apiClient.get<MediaPreview[]>(
      `/api/surveys/${surveyId}/system-labels/${encodeURIComponent(systemLabel)}/media`,
      { params: { limit, question_id: questionId } }
    );
  },

  /**
   * Create a new reporting label
   */
  createReportingLabel: (data: ReportingLabelCreate) => {
    return apiClient.post<ReportingLabel>('/api/reporting-labels', data);
  },

  /**
   * Update a reporting label
   */
  updateReportingLabel: (labelId: number, data: ReportingLabelUpdate) => {
    return apiClient.put<ReportingLabel>(`/api/reporting-labels/${labelId}`, data);
  },

  /**
   * Delete a reporting label
   */
  deleteReportingLabel: (labelId: number) => {
    return apiClient.delete(`/api/reporting-labels/${labelId}`);
  },

  /**
   * Add a system label to a reporting label
   */
  addSystemLabel: (reportingLabelId: number, systemLabel: string) => {
    const data: AddSystemLabelRequest = { system_label: systemLabel };
    return apiClient.post<ReportingLabel>(
      `/api/reporting-labels/${reportingLabelId}/system-labels`,
      data
    );
  },

  /**
   * Remove a system label from a reporting label
   */
  removeSystemLabel: (reportingLabelId: number, systemLabel: string) => {
    const data: RemoveSystemLabelRequest = { system_label: systemLabel };
    return apiClient.delete(
      `/api/reporting-labels/${reportingLabelId}/system-labels`,
      data
    );
  },
};
