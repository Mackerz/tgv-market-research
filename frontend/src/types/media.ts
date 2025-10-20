/**
 * Media Domain Types
 * Centralized type definitions for media upload and gallery
 */

export interface FileUploadResponse {
  file_url: string;
  file_id: string;
  thumbnail_url?: string;
}

export interface MediaGalleryItem {
  id: number;
  media_type: 'photo' | 'video';
  media_url: string;
  thumbnail_url: string | null;
  description: string;
  transcript: string;
  brands_detected: string[];
  reporting_labels: string[];
  submission_id: number;
  submission_email: string;
  submission_region: string;
  submission_gender: string;
  submission_age: number;
  question: string;
  responded_at: string;
}

export interface MediaGalleryResponse {
  items: MediaGalleryItem[];
  total_count: number;
  photo_count: number;
  video_count: number;
}

export interface MediaUploadConfig {
  type: 'photo' | 'video';
  accept: string;
  maxSizeMB: number;
  maxSizeBytes: number;
  uploadEndpoint: string;
  fileTypeError: string;
  fileSizeError: string;
}
