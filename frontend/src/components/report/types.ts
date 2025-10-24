// Submission types
export interface Submission {
  id: number;
  email: string;
  phone_number: string;
  region: string;
  gender: string;
  age: number;
  submitted_at: string;
  is_approved: boolean | null;
  is_completed: boolean;
}

export interface SubmissionsResponse {
  submissions: Submission[];
  total_count: number;
  approved_count: number;
  rejected_count: number;
  pending_count: number;
  survey: {
    id: number;
    name: string;
    survey_slug: string;
  };
}

// Response types
export interface MediaAnalysis {
  id: number;
  description: string;
  transcript: string;
  brands_detected: string[];
  reporting_labels: string[];
}

export interface Response {
  id: number;
  question: string;
  question_type: string;
  single_answer: string | null;
  free_text_answer: string | null;
  multiple_choice_answer: string[] | null;
  photo_url: string | null;
  video_url: string | null;
  responded_at: string;
  media_analysis: MediaAnalysis | null;
}

export interface SubmissionDetailResponse {
  submission: Submission;
  responses: Response[];
  survey: {
    id: number;
    name: string;
    survey_slug: string;
  };
}

// Settings types
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

// Chart types
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

// Filter types
export type TabType = 'submissions' | 'reporting' | 'media-gallery' | 'taxonomies' | 'settings';
export type ApprovalFilter = 'all' | 'approved' | 'rejected' | 'pending';
export type SortBy = 'submitted_at' | 'email' | 'age' | 'region';
