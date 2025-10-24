'use client'

import { apiUrl } from '@/config/api'
import type { MediaGalleryItem } from './MediaModal'

interface MediaGridItemProps {
  item: MediaGalleryItem
  onClick: () => void
}

export function MediaGridItem({ item, onClick }: MediaGridItemProps) {
  return (
    <div
      className="relative group cursor-pointer border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      {/* Media Preview */}
      <div className="aspect-square bg-gray-100 flex items-center justify-center">
        {item.media_type === 'photo' ? (
          <>
            <img
              src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(item.media_url)}`)}
              alt="Response media"
              className="w-full h-full object-cover"
              onError={(e) => {
                const target = e.target as HTMLImageElement
                target.style.display = 'none'
                const errorDiv = document.createElement('div')
                errorDiv.textContent = '📷 Photo unavailable'
                errorDiv.className = 'text-gray-500 text-sm'
                target.parentNode?.appendChild(errorDiv)
              }}
            />
            <div className="absolute top-2 left-2 bg-green-500 text-white px-2 py-1 rounded text-xs">
              📷 Photo
            </div>
          </>
        ) : (
          <>
            <video
              className="w-full h-full object-cover"
              preload="metadata"
              muted
            >
              <source
                src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(item.media_url)}`)}
                type="video/mp4"
              />
            </video>
            <div className="absolute top-2 left-2 bg-blue-500 text-white px-2 py-1 rounded text-xs">
              🎥 Video
            </div>
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 group-hover:bg-opacity-30 transition-all">
              <div className="text-white text-2xl">▶</div>
            </div>
          </>
        )}
      </div>

      {/* Info Overlay */}
      <div className="p-3 bg-white">
        <div className="text-sm font-medium text-gray-900 mb-1 truncate">
          {item.question}
        </div>
        <div className="text-xs text-gray-500 mb-2">
          {item.submission_gender}, {item.submission_age} • {item.submission_region}
        </div>
        {item.reporting_labels.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.reporting_labels.slice(0, 2).map((label, idx) => (
              <span
                key={idx}
                className="px-1 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
              >
                {label}
              </span>
            ))}
            {item.reporting_labels.length > 2 && (
              <span className="px-1 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                +{item.reporting_labels.length - 2}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
