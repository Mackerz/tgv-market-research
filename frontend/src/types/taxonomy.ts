/**
 * Taxonomy Domain Types
 * Type definitions for managing label taxonomies and mappings
 */

export interface LabelMapping {
  id: number;
  reporting_label_id: number;
  system_label: string;
  created_at: string;
}

export interface ReportingLabel {
  id: number;
  survey_id: number;
  label_name: string;
  description: string | null;
  is_ai_generated: boolean;
  created_at: string;
  updated_at: string | null;
  label_mappings: LabelMapping[];
}

export interface SystemLabelWithCount {
  label: string;
  count: number;
  sample_media_ids: number[];
}

export interface TaxonomyOverview {
  reporting_labels: ReportingLabel[];
  unmapped_system_labels: SystemLabelWithCount[];
  total_media_items: number;
}

export interface ReportingLabelCreate {
  survey_id: number;
  label_name: string;
  description?: string;
  is_ai_generated?: boolean;
  system_labels?: string[];
}

export interface ReportingLabelUpdate {
  label_name?: string;
  description?: string;
}

export interface AddSystemLabelRequest {
  system_label: string;
}

export interface RemoveSystemLabelRequest {
  system_label: string;
}

export interface GenerateTaxonomyRequest {
  survey_id: number;
  max_categories?: number;
}

export interface MediaPreview {
  id: number;
  media_type: string;
  media_url: string;
  thumbnail_url: string | null;
  description: string;
  submission_id: number;
  respondent_info: {
    region?: string;
    gender?: string;
    age?: number;
  };
}
