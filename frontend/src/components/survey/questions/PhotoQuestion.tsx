"use client";

import { useState, useRef } from "react";
import { PhotoIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { apiUrl } from "@/config/api";

interface SurveyQuestion {
  id: string;
  question: string;
  question_type: string;
  required: boolean;
  options?: string[];
}

interface PhotoQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

export default function PhotoQuestion({ question, onSubmit, loading, surveySlug }: PhotoQuestionProps) {
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
    if (!file.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be smaller than 10MB');
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
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await fetch(apiUrl(`/api/surveys/${surveySlug}/upload/photo`), {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setUploadedUrl(result.file_url);
    } catch (error) {
      console.error('Upload error:', error);
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
      setError('Please upload a photo');
      return;
    }

    // Submit answer
    onSubmit({
      photo_url: uploadedUrl
    });
  };

  const handleSkip = () => {
    if (question.required) return;

    onSubmit({
      photo_url: ''
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload Area */}
      <div>
        {!uploadedFile ? (
          <label className="flex flex-col items-center justify-center w-full h-48 sm:h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors touch-manipulation">
            <div className="flex flex-col items-center justify-center pt-5 pb-6 px-4">
              <PhotoIcon className="w-8 h-8 sm:w-10 sm:h-10 mb-3 text-gray-400" />
              <p className="mb-2 text-sm text-center text-gray-500">
                <span className="font-semibold">Tap to upload</span> or drag and drop
              </p>
              <p className="text-xs text-center text-gray-500">PNG, JPG, GIF up to 10MB</p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept="image/*"
              onChange={handleFileSelect}
              disabled={loading || uploading}
            />
          </label>
        ) : (
          <div className="relative">
            {/* Preview */}
            <div className="w-full max-w-sm sm:max-w-md mx-auto bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={previewUrl}
                alt="Preview"
                className="w-full h-48 sm:h-64 object-cover"
              />
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
                {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
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
                    Uploading...
                  </div>
                ) : (
                  'Upload Photo'
                )}
              </button>
            )}

            {/* Upload Success */}
            {uploadedUrl && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 text-sm font-medium">✅ Photo uploaded successfully!</p>
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