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
  complete_redirect_url?: string;
  screenout_redirect_url?: string;
}

export interface QuestionMedia {
  url: string;
  type: QuestionMediaType;
  caption?: string;
}

export interface SurveyQuestion {
  id: string;
  question: string;
  question_type: QuestionType;
  required: boolean;
  options?: string[];
  routing_rules?: RoutingRule[];
  media?: QuestionMedia[];
  // Legacy support (deprecated)
  media_url?: string;
  media_type?: QuestionMediaType;
}

export type QuestionType = 'free_text' | 'single' | 'multi' | 'photo' | 'video';

export type QuestionMediaType = 'photo' | 'video';

export type ConditionOperator =
  | 'equals'
  | 'not_equals'
  | 'contains'
  | 'not_contains'
  | 'contains_any'
  | 'contains_all'
  | 'greater_than'
  | 'less_than'
  | 'is_answered'
  | 'is_not_answered';

export type RoutingAction = 'goto_question' | 'end_survey' | 'continue';

export interface RoutingCondition {
  question_id: string;
  operator: ConditionOperator;
  value?: string | string[] | number;
}

export interface RoutingRule {
  conditions: RoutingCondition[];
  action: RoutingAction;
  target_question_id?: string;
}

export interface NextQuestionResponse {
  action: RoutingAction;
  next_question_id?: string;
  question_index?: number;
  question?: SurveyQuestion;
}

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
  external_user_id?: string;
}

export interface SubmissionCreate {
  survey_id: number;
  email: string;
  phone_number: string;
  region: string;
  date_of_birth: string;
  gender: string;
  external_user_id?: string;
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
