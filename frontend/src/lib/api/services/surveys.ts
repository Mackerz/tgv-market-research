/**
 * Survey API Service
 * All survey-related API calls
 */

import { apiClient } from '../client';
import type {
  Survey,
  Submission,
  SubmissionCreate,
  Response,
  ResponseCreate,
  SurveyProgress,
  FileUploadResponse,
  NextQuestionResponse,
} from '@/types';

export const surveyService = {
  /**
   * Get survey by slug
   */
  getSurveyBySlug: (slug: string) => {
    return apiClient.get<Survey>(`/api/surveys/slug/${slug}`);
  },

  /**
   * Get survey by ID
   */
  getSurvey: (id: number) => {
    return apiClient.get<Survey>(`/api/surveys/${id}`);
  },

  /**
   * List all surveys
   */
  listSurveys: (params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
    search?: string;
    client?: string;
    sort_by?: string;
    sort_order?: string;
  }) => {
    return apiClient.get<{ surveys: Survey[]; total_count: number }>(
      '/api/surveys/',
      { params }
    );
  },

  /**
   * Create a submission
   */
  createSubmission: (slug: string, data: Omit<SubmissionCreate, 'survey_id'>) => {
    return apiClient.post<Submission>(`/api/surveys/${slug}/submit`, data);
  },

  /**
   * Get submission
   */
  getSubmission: (submissionId: number) => {
    return apiClient.get<Submission>(`/api/submissions/${submissionId}`);
  },

  /**
   * Get submission progress
   */
  getProgress: (submissionId: number) => {
    return apiClient.get<SurveyProgress>(`/api/submissions/${submissionId}/progress`);
  },

  /**
   * Mark submission as complete
   */
  completeSubmission: (submissionId: number) => {
    return apiClient.put(`/api/submissions/${submissionId}/complete`);
  },

  /**
   * Create a response
   */
  createResponse: (submissionId: number, data: ResponseCreate) => {
    return apiClient.post<Response>(`/api/submissions/${submissionId}/responses`, data);
  },

  /**
   * List responses for a submission
   */
  listResponses: (submissionId: number) => {
    return apiClient.get<Response[]>(`/api/submissions/${submissionId}/responses`);
  },

  /**
   * Upload a photo
   */
  uploadPhoto: (slug: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload<FileUploadResponse>(`/api/surveys/${slug}/upload/photo`, formData);
  },

  /**
   * Upload a video
   */
  uploadVideo: (slug: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload<FileUploadResponse>(`/api/surveys/${slug}/upload/video`, formData);
  },

  /**
   * Get next question based on routing logic
   */
  getNextQuestion: (submissionId: number, currentQuestionId: string) => {
    return apiClient.get<NextQuestionResponse>(
      `/api/submissions/${submissionId}/next-question`,
      { params: { current_question_id: currentQuestionId } }
    );
  },
};
