import { useState } from 'react';
import type { QuestionMedia } from '@/types/survey';

interface QuestionMediaGalleryProps {
  mediaItems: QuestionMedia[];
  altText?: string;
}

interface MediaItemProps {
  media: QuestionMedia;
  altText: string;
}

function MediaItem({ media, altText }: MediaItemProps) {
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
        {media.caption && (
          <p className="text-gray-400 text-xs mt-1">{media.caption}</p>
        )}
      </div>
    );
  }

  return (
    <div className="relative w-full">
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#D01A8A]"></div>
        </div>
      )}

      {/* Photo Display */}
      {media.type === 'photo' && (
        <div className="rounded-lg overflow-hidden shadow-md border border-gray-200">
          <img
            src={media.url}
            alt={media.caption || altText}
            className={`w-full h-auto object-contain max-h-96 ${isLoading ? 'invisible' : 'visible'}`}
            onLoad={handleLoad}
            onError={handleError}
          />
          {media.caption && !isLoading && !hasError && (
            <div className="bg-gray-50 px-4 py-2 border-t border-gray-200">
              <p className="text-sm text-gray-700">{media.caption}</p>
            </div>
          )}
        </div>
      )}

      {/* Video Display */}
      {media.type === 'video' && (
        <div className="rounded-lg overflow-hidden shadow-md border border-gray-200">
          <video
            src={media.url}
            controls
            className={`w-full h-auto object-contain max-h-96 ${isLoading ? 'invisible' : 'visible'}`}
            onLoadedData={handleLoad}
            onError={handleError}
            preload="metadata"
          >
            Your browser does not support the video tag.
          </video>
          {media.caption && !isLoading && !hasError && (
            <div className="bg-gray-50 px-4 py-2 border-t border-gray-200">
              <p className="text-sm text-gray-700">{media.caption}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function QuestionMediaGallery({ mediaItems, altText = 'Question media' }: QuestionMediaGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!mediaItems || mediaItems.length === 0) {
    return null;
  }

  // Single media item - display without carousel
  if (mediaItems.length === 1) {
    return (
      <div className="mb-6">
        <MediaItem media={mediaItems[0]} altText={altText} />
      </div>
    );
  }

  // Multiple media items - display with carousel
  const canGoPrev = currentIndex > 0;
  const canGoNext = currentIndex < mediaItems.length - 1;

  const handlePrev = () => {
    if (canGoPrev) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const handleNext = () => {
    if (canGoNext) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  return (
    <div className="mb-6">
      {/* Carousel Container */}
      <div className="relative">
        {/* Main Media Display */}
        <MediaItem media={mediaItems[currentIndex]} altText={altText} />

        {/* Navigation Arrows */}
        {mediaItems.length > 1 && (
          <>
            {/* Previous Button */}
            <button
              onClick={handlePrev}
              disabled={!canGoPrev}
              className={`absolute left-2 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full p-2 shadow-lg transition-all ${
                !canGoPrev ? 'opacity-50 cursor-not-allowed' : 'opacity-100'
              }`}
              aria-label="Previous media"
            >
              <svg className="w-6 h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            {/* Next Button */}
            <button
              onClick={handleNext}
              disabled={!canGoNext}
              className={`absolute right-2 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full p-2 shadow-lg transition-all ${
                !canGoNext ? 'opacity-50 cursor-not-allowed' : 'opacity-100'
              }`}
              aria-label="Next media"
            >
              <svg className="w-6 h-6 text-gray-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </>
        )}
      </div>

      {/* Carousel Indicators */}
      {mediaItems.length > 1 && (
        <div className="flex justify-center items-center gap-2 mt-4">
          <span className="text-sm text-gray-600">
            {currentIndex + 1} / {mediaItems.length}
          </span>
          <div className="flex gap-2">
            {mediaItems.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? 'w-8 bg-[#D01A8A]'
                    : 'w-2 bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`Go to media ${index + 1}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Thumbnail Preview (for 2-4 items) */}
      {mediaItems.length > 1 && mediaItems.length <= 4 && (
        <div className="grid grid-cols-4 gap-2 mt-4">
          {mediaItems.map((item, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`relative aspect-video rounded-lg overflow-hidden border-2 transition-all ${
                index === currentIndex
                  ? 'border-[#D01A8A] ring-2 ring-[#E84AA6]'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
            >
              {item.type === 'photo' ? (
                <img
                  src={item.url}
                  alt={item.caption || `Media ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              )}
              {index === currentIndex && (
                <div className="absolute inset-0 bg-[#D01A8A]/10"></div>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
