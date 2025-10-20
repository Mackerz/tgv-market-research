/**
 * Reporting Domain Types
 * Centralized type definitions for reporting and analytics
 */

import { Submission, Response } from './survey';

export interface SubmissionsResponse {
  submissions: Submission[];
  total_count: number;
  approved_count: number;
  rejected_count: number;
  pending_count: number;
  survey: SurveyInfo;
}

export interface SurveyInfo {
  id: number;
  name: string;
  survey_slug: string;
}

export interface SubmissionDetailResponse {
  submission: Submission;
  responses: Response[];
  survey: SurveyInfo;
}

export interface ChartData {
  labels: string[];
  data: number[];
  backgroundColor?: string[];
}

export interface DemographicData {
  age_ranges: ChartData;
  regions: ChartData;
  genders: ChartData;
}

export interface QuestionResponseData {
  question_id: string;
  question_text: string;
  display_name: string | null;
  question_type: string;
  chart_data: ChartData;
}

export interface MediaData {
  photos: ChartData;
  videos: ChartData;
}

export interface ReportingData {
  total_submissions: number;
  completed_approved_submissions: number;
  survey_name: string;
  survey_slug: string;
  generated_at: string;
  demographics: DemographicData;
  question_responses: QuestionResponseData[];
  media_analysis: MediaData;
}

export interface AgeRange {
  min: number;
  max: number | null;
  label: string;
}

export interface QuestionDisplayName {
  id: number;
  question_id: string;
  question_text: string;
  display_name: string | null;
  report_settings_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface AvailableQuestion {
  id: string;
  question: string;
  question_type: string;
}

export interface ReportSettings {
  id: number;
  survey_id: number;
  age_ranges: AgeRange[];
  created_at: string;
  updated_at: string | null;
  question_display_names: QuestionDisplayName[];
  available_questions: AvailableQuestion[];
}

export type ApprovalFilter = 'all' | 'approved' | 'rejected' | 'pending';
export type SortBy = 'submitted_at' | 'email' | 'age' | 'region';
export type SortOrder = 'asc' | 'desc';
