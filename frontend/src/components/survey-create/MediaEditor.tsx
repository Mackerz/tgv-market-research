import { TrashIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import { QuestionMedia } from './types';
import { useState } from 'react';
import { apiClient, ApiError } from '@/lib/api/client';

interface MediaEditorProps {
  media: QuestionMedia[];
  onAddMedia: () => void;
  onUpdateMedia: (index: number, updates: Partial<QuestionMedia>) => void;
  onRemoveMedia: (index: number) => void;
}

export default function MediaEditor({
  media,
  onAddMedia,
  onUpdateMedia,
  onRemoveMedia
}: MediaEditorProps) {
  const [uploadingIndex, setUploadingIndex] = useState<number | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileUpload = async (mediaIndex: number, file: File) => {
    setUploadingIndex(mediaIndex);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.upload<{ file_url: string; file_id: string }>(
        '/api/questions/upload/media',
        formData
      );

      // Update the media URL with the uploaded file URL
      onUpdateMedia(mediaIndex, { url: response.file_url });
    } catch (err) {
      if (err instanceof ApiError) {
        setUploadError(err.message);
      } else {
        setUploadError('Failed to upload media. Please try again.');
      }
    } finally {
      setUploadingIndex(null);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">
          Media (Optional)
        </label>
        <button
          type="button"
          onClick={onAddMedia}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          + Add Media
        </button>
      </div>
      {uploadError && (
        <div className="mb-3 bg-red-50 border border-red-200 text-red-800 px-3 py-2 rounded-lg text-sm">
          {uploadError}
        </div>
      )}
      {media.length > 0 && (
        <div className="space-y-3">
          {media.map((mediaItem, mediaIndex) => (
            <div key={mediaIndex} className="border rounded-md p-3 space-y-2">
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium text-gray-700">Media {mediaIndex + 1}</span>
                <button
                  type="button"
                  onClick={() => onRemoveMedia(mediaIndex)}
                  className="text-red-600 hover:text-red-900"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Media Type</label>
                  <select
                    value={mediaItem.type}
                    onChange={(e) => onUpdateMedia(mediaIndex, { type: e.target.value as 'photo' | 'video' })}
                    className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                  >
                    <option value="photo">Photo</option>
                    <option value="video">Video</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Media File</label>
                <div className="space-y-2">
                  {mediaItem.url ? (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 px-2 py-1 bg-green-50 border border-green-200 rounded text-sm text-green-800 truncate">
                        {mediaItem.url}
                      </div>
                      <label className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 cursor-pointer whitespace-nowrap">
                        Change
                        <input
                          type="file"
                          accept={mediaItem.type === 'photo' ? 'image/*' : 'video/*'}
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (file) handleFileUpload(mediaIndex, file);
                          }}
                        />
                      </label>
                    </div>
                  ) : (
                    <label className="flex items-center justify-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-colors">
                      <ArrowUpTrayIcon className="h-5 w-5 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {uploadingIndex === mediaIndex ? 'Uploading...' : 'Click to upload'}
                      </span>
                      <input
                        type="file"
                        accept={mediaItem.type === 'photo' ? 'image/*' : 'video/*'}
                        className="hidden"
                        disabled={uploadingIndex === mediaIndex}
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) handleFileUpload(mediaIndex, file);
                        }}
                      />
                    </label>
                  )}
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Caption (Optional)</label>
                <input
                  type="text"
                  value={mediaItem.caption || ''}
                  onChange={(e) => onUpdateMedia(mediaIndex, { caption: e.target.value })}
                  placeholder="Media caption"
                  className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
