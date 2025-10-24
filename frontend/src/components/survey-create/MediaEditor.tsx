import { TrashIcon } from '@heroicons/react/24/outline';
import { QuestionMedia } from './types';

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
                <label className="block text-xs text-gray-600 mb-1">Media URL (GCS URL)</label>
                <input
                  type="url"
                  value={mediaItem.url}
                  onChange={(e) => onUpdateMedia(mediaIndex, { url: e.target.value })}
                  placeholder="https://storage.googleapis.com/..."
                  className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                />
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
