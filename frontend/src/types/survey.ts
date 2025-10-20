/**
 * Survey Domain Types
 * Centralized type definitions for survey-related entities
 */

export interface Survey {
  id: number;
  survey_slug: string;
  name: string;
  survey_flow: SurveyQuestion[];
  is_active: boolean;
  client?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SurveyQuestion {
  id: string;
  question: string;
  question_type: QuestionType;
  required: boolean;
  options?: string[];
}

export type QuestionType = 'free_text' | 'single' | 'multi' | 'photo' | 'video';

export interface Submission {
  id: number;
  survey_id: number;
  email: string;
  phone_number: string;
  region: string;
  gender: string;
  date_of_birth?: string;
  age: number;
  submitted_at: string;
  is_approved: boolean | null;
  is_completed: boolean;
}

export interface SubmissionCreate {
  survey_id: number;
  email: string;
  phone_number: string;
  region: string;
  date_of_birth: string;
  gender: string;
}

export interface Response {
  id: number;
  submission_id: number;
  question: string;
  question_type: string;
  single_answer?: string | null;
  free_text_answer?: string | null;
  multiple_choice_answer?: string[] | null;
  photo_url?: string | null;
  video_url?: string | null;
  video_thumbnail_url?: string | null;
  responded_at: string;
  media_analysis?: MediaAnalysis | null;
}

export interface ResponseCreate {
  question: string;
  question_type: string;
  single_answer?: string;
  free_text_answer?: string;
  multiple_choice_answer?: string[];
  photo_url?: string;
  video_url?: string;
}

export interface SurveyProgress {
  current_question: number;
  total_questions: number;
  submission_id: number;
  is_completed: boolean;
}

export interface MediaAnalysis {
  id: number;
  description: string;
  transcript: string;
  brands_detected: string[];
  reporting_labels: string[];
}
