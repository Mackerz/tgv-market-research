'use client'

import { useEffect } from 'react'
import { apiUrl } from '@/config/api'

export interface MediaGalleryItem {
  id: number
  media_type: 'photo' | 'video'
  media_url: string
  thumbnail_url?: string
  description?: string
  transcript?: string
  brands_detected: string[]
  reporting_labels: string[]
  submission_id: number
  submission_email: string
  submission_region: string
  submission_gender: string
  submission_age: number
  question: string
  responded_at: string
}

interface MediaModalProps {
  item: MediaGalleryItem
  onClose: () => void
}

export function MediaModal({ item, onClose }: MediaModalProps) {
  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleEsc)
    return () => {
      window.removeEventListener('keydown', handleEsc)
    }
  }, [onClose])

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={handleBackdropClick}>
      <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] w-full overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="text-lg font-semibold truncate pr-4">{item.question}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 flex-shrink-0"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Media Content */}
        <div className="p-4 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="mb-4">
            {item.media_type === 'photo' ? (
              <img
                src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(item.media_url)}`)}
                alt="Response media"
                className="w-full h-auto max-h-96 object-contain mx-auto rounded border"
                onError={(e) => {
                  const target = e.target as HTMLImageElement
                  target.style.display = 'none'
                  const errorDiv = document.createElement('div')
                  errorDiv.textContent = 'Error loading image'
                  errorDiv.className = 'text-red-500 text-center p-4'
                  target.parentNode?.insertBefore(errorDiv, target.nextSibling)
                }}
              />
            ) : (
              <video
                controls
                preload="metadata"
                crossOrigin="anonymous"
                className="w-full h-auto max-h-96 object-contain mx-auto rounded border"
                onError={(e) => {
                  const target = e.target as HTMLVideoElement
                  target.style.display = 'none'
                  const errorDiv = document.createElement('div')
                  errorDiv.innerHTML = `<div class="text-red-500 text-center p-4">Error loading video</div><div class="text-xs text-gray-400 mt-1 text-center"><a href="${apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(item.media_url)}`)}" target="_blank" class="underline">Try opening video directly</a></div>`
                  target.parentNode?.insertBefore(errorDiv, target.nextSibling)
                }}
              >
                <source
                  src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(item.media_url)}`)}
                  type="video/mp4"
                />
                <p className="text-red-500 text-center p-4">
                  Your browser does not support the video tag.
                </p>
              </video>
            )}
          </div>

          {/* Media Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Media Analysis */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Media Analysis</h4>

              {item.description && (
                <div>
                  <div className="font-medium text-sm text-gray-600 mb-1">Description:</div>
                  <p className="text-sm text-gray-700">{item.description}</p>
                </div>
              )}

              {item.transcript && (
                <div>
                  <div className="font-medium text-sm text-gray-600 mb-1">Transcript:</div>
                  <p className="text-sm text-gray-700">{item.transcript}</p>
                </div>
              )}

              {item.brands_detected.length > 0 && (
                <div>
                  <div className="font-medium text-sm text-gray-600 mb-2">Brands Detected:</div>
                  <div className="flex flex-wrap gap-1">
                    {item.brands_detected.map((brand, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-[#F5E8F0] text-[#4E0036] rounded text-xs"
                      >
                        {brand}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {item.reporting_labels.length > 0 && (
                <div>
                  <div className="font-medium text-sm text-gray-600 mb-2">Reporting Labels:</div>
                  <div className="flex flex-wrap gap-1">
                    {item.reporting_labels.map((label, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Submission Info */}
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900">Respondent Information</h4>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="font-medium text-gray-600">Email:</div>
                  <div className="text-gray-700">{item.submission_email}</div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Region:</div>
                  <div className="text-gray-700">{item.submission_region}</div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Gender:</div>
                  <div className="text-gray-700">{item.submission_gender}</div>
                </div>
                <div>
                  <div className="font-medium text-gray-600">Age:</div>
                  <div className="text-gray-700">{item.submission_age}</div>
                </div>
              </div>

              <div>
                <div className="font-medium text-sm text-gray-600 mb-1">Submitted:</div>
                <div className="text-sm text-gray-700">
                  {new Date(item.responded_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
