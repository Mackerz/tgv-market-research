import { useState } from 'react';
import type { QuestionMediaType } from '@/types/survey';

interface QuestionMediaProps {
  mediaUrl: string;
  mediaType: QuestionMediaType;
  altText?: string;
}

export default function QuestionMedia({ mediaUrl, mediaType, altText = 'Question media' }: QuestionMediaProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  if (hasError) {
    return (
      <div className="w-full bg-gray-100 rounded-lg p-8 text-center border border-gray-300">
        <div className="text-gray-400 text-4xl mb-2">📷</div>
        <p className="text-gray-600 text-sm">Unable to load media</p>
        <p className="text-gray-400 text-xs mt-1">The media file could not be displayed</p>
      </div>
    );
  }

  return (
    <div className="relative w-full mb-6">
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#D01A8A]"></div>
        </div>
      )}

      {/* Photo Display */}
      {mediaType === 'photo' && (
        <div className="rounded-lg overflow-hidden shadow-md border border-gray-200">
          <img
            src={mediaUrl}
            alt={altText}
            className={`w-full h-auto object-contain max-h-96 ${isLoading ? 'invisible' : 'visible'}`}
            onLoad={handleLoad}
            onError={handleError}
          />
        </div>
      )}

      {/* Video Display */}
      {mediaType === 'video' && (
        <div className="rounded-lg overflow-hidden shadow-md border border-gray-200">
          <video
            src={mediaUrl}
            controls
            className={`w-full h-auto object-contain max-h-96 ${isLoading ? 'invisible' : 'visible'}`}
            onLoadedData={handleLoad}
            onError={handleError}
            preload="metadata"
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
}
