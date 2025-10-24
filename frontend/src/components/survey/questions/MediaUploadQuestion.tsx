"use client";

import { useState, useRef } from "react";
import { logger } from '@/lib/logger';
import { PhotoIcon, VideoCameraIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { surveyService } from "@/lib/api";
import type { SurveyQuestion, FileUploadResponse, MediaUploadConfig } from "@/types";

interface MediaUploadQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
  mediaType: 'photo' | 'video';
}

// Configuration for each media type
const MEDIA_CONFIGS: Record<'photo' | 'video', MediaUploadConfig> = {
  photo: {
    type: 'photo',
    accept: 'image/*',
    maxSizeMB: 10,
    maxSizeBytes: 10 * 1024 * 1024,
    uploadEndpoint: 'photo',
    fileTypeError: 'Please select an image file',
    fileSizeError: 'Image must be smaller than 10MB',
  },
  video: {
    type: 'video',
    accept: 'video/*',
    maxSizeMB: 100,
    maxSizeBytes: 100 * 1024 * 1024,
    uploadEndpoint: 'video',
    fileTypeError: 'Please select a video file',
    fileSizeError: 'Video must be smaller than 100MB',
  },
};

export default function MediaUploadQuestion({
  question,
  onSubmit,
  loading,
  surveySlug,
  mediaType,
}: MediaUploadQuestionProps) {
  const config = MEDIA_CONFIGS[mediaType];

  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadedUrl, setUploadedUrl] = useState<string>('');
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const expectedType = config.type === 'photo' ? 'image/' : 'video/';
    if (!file.type.startsWith(expectedType)) {
      setError(config.fileTypeError);
      return;
    }

    // Validate file size
    if (file.size > config.maxSizeBytes) {
      setError(config.fileSizeError);
      return;
    }

    setUploadedFile(file);
    setError('');

    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleUpload = async () => {
    if (!uploadedFile) return;

    setUploading(true);
    setError('');

    try {
      let result: FileUploadResponse;

      if (config.type === 'photo') {
        result = await surveyService.uploadPhoto(surveySlug, uploadedFile);
      } else {
        result = await surveyService.uploadVideo(surveySlug, uploadedFile);
      }

      setUploadedUrl(result.file_url);
    } catch (error) {
      logger.error('Upload error:', error);
      setError(error instanceof Error ? error.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl('');
    }
    setUploadedUrl('');
    setError('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (question.required && !uploadedUrl) {
      setError(`Please upload a ${config.type}`);
      return;
    }

    // Submit answer with correct field name
    const fieldName = config.type === 'photo' ? 'photo_url' : 'video_url';
    onSubmit({
      [fieldName]: uploadedUrl
    });
  };

  const handleSkip = () => {
    if (question.required) return;

    const fieldName = config.type === 'photo' ? 'photo_url' : 'video_url';
    onSubmit({
      [fieldName]: ''
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Render upload icon based on media type
  const UploadIcon = config.type === 'photo' ? PhotoIcon : VideoCameraIcon;
  const uploadLabel = config.type === 'photo' ? 'PNG, JPG, GIF up to 10MB' : 'MP4, MOV, AVI up to 100MB';
  const uploadButtonText = config.type === 'photo' ? 'Upload Photo' : 'Upload Video';
  const successMessage = config.type === 'photo' ? 'Photo uploaded successfully!' : 'Video uploaded successfully!';

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload Area */}
      <div>
        {!uploadedFile ? (
          <label className="flex flex-col items-center justify-center w-full h-48 sm:h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors touch-manipulation">
            <div className="flex flex-col items-center justify-center pt-5 pb-6 px-4">
              <UploadIcon className="w-8 h-8 sm:w-10 sm:h-10 mb-3 text-gray-400" />
              <p className="mb-2 text-sm text-center text-gray-500">
                <span className="font-semibold">Tap to upload</span> or drag and drop
              </p>
              <p className="text-xs text-center text-gray-500">{uploadLabel}</p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept={config.accept}
              onChange={handleFileSelect}
              disabled={loading || uploading}
            />
          </label>
        ) : (
          <div className="relative">
            {/* Preview */}
            <div className="w-full max-w-sm sm:max-w-md mx-auto bg-gray-100 rounded-lg overflow-hidden">
              {config.type === 'photo' ? (
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full h-48 sm:h-64 object-cover"
                />
              ) : (
                <video
                  src={previewUrl}
                  controls
                  className="w-full h-48 sm:h-64 object-cover"
                  preload="metadata"
                />
              )}
            </div>

            {/* Remove Button */}
            <button
              type="button"
              onClick={handleRemoveFile}
              className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors touch-manipulation"
              disabled={loading || uploading}
            >
              <XMarkIcon className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>

            {/* File Info */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700 font-medium">{uploadedFile.name}</p>
              <p className="text-xs text-gray-500">
                {formatFileSize(uploadedFile.size)}
              </p>
            </div>

            {/* Upload Button */}
            {!uploadedUrl && (
              <button
                type="button"
                onClick={handleUpload}
                disabled={uploading}
                className={`mt-4 w-full py-2 px-4 rounded-lg text-white font-medium transition-colors ${
                  uploading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {uploading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...{config.type === 'video' && ' (this may take a while)'}
                  </div>
                ) : (
                  uploadButtonText
                )}
              </button>
            )}

            {/* Upload Progress Info (video only) */}
            {uploading && config.type === 'video' && (
              <div className="mt-2 text-center text-xs text-gray-500">
                Large videos may take several minutes to upload
              </div>
            )}

            {/* Upload Success */}
            {uploadedUrl && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 text-sm font-medium">✅ {successMessage}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {error && (
        <p className="text-red-500 text-sm">{error}</p>
      )}

      {/* Submit Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        {!question.required && (
          <button
            type="button"
            onClick={handleSkip}
            disabled={loading || uploading}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
          >
            Skip
          </button>
        )}

        <button
          type="submit"
          disabled={loading || uploading || (question.required && !uploadedUrl)}
          className={`flex-1 py-3 px-6 rounded-lg text-white font-medium transition-colors touch-manipulation ${
            loading || uploading || (question.required && !uploadedUrl)
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Submitting...
            </div>
          ) : (
            'Continue'
          )}
        </button>
      </div>
    </form>
  );
}
