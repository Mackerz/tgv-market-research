'use client'

import { useState, useEffect } from 'react'
import { apiUrl } from '@/config/api'

interface MediaGalleryItem {
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

interface MediaGalleryResponse {
  items: MediaGalleryItem[]
  total_count: number
  photo_count: number
  video_count: number
}

interface MediaGalleryProps {
  reportSlug: string
}

interface MediaModalProps {
  item: MediaGalleryItem
  onClose: () => void
}

const MediaModal = ({ item, onClose }: MediaModalProps) => {
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
                        className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
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

export default function MediaGallery({ reportSlug }: MediaGalleryProps) {
  const [galleryData, setGalleryData] = useState<MediaGalleryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedItem, setSelectedItem] = useState<MediaGalleryItem | null>(null)

  // Filter states
  const [selectedLabels, setSelectedLabels] = useState<string[]>([])
  const [selectedRegions, setSelectedRegions] = useState<string[]>([])
  const [selectedGenders, setSelectedGenders] = useState<string[]>([])
  const [ageMin, setAgeMin] = useState<number | undefined>()
  const [ageMax, setAgeMax] = useState<number | undefined>()
  const [mediaTypeFilter, setMediaTypeFilter] = useState<'all' | 'photo' | 'video'>('all')

  // Available filter options
  const [availableLabels, setAvailableLabels] = useState<string[]>([])
  const [availableRegions, setAvailableRegions] = useState<string[]>([])
  const [availableGenders, setAvailableGenders] = useState<string[]>([])

  const fetchGalleryData = async () => {
    try {
      setLoading(true)

      // Build query parameters
      const params = new URLSearchParams()
      if (selectedLabels.length > 0) params.append('labels', selectedLabels.join(','))
      if (selectedRegions.length > 0) params.append('regions', selectedRegions.join(','))
      if (selectedGenders.length > 0) params.append('genders', selectedGenders.join(','))
      if (ageMin !== undefined) params.append('age_min', ageMin.toString())
      if (ageMax !== undefined) params.append('age_max', ageMax.toString())

      const response = await fetch(apiUrl(`/api/reports/${reportSlug}/media-gallery?${params}`))
      if (!response.ok) {
        throw new Error('Failed to fetch media gallery')
      }

      const data: MediaGalleryResponse = await response.json()
      setGalleryData(data)

      // Extract unique filter options from the data
      const labels = new Set<string>()
      const regions = new Set<string>()
      const genders = new Set<string>()

      data.items.forEach(item => {
        item.reporting_labels.forEach(label => labels.add(label))
        regions.add(item.submission_region)
        genders.add(item.submission_gender)
      })

      setAvailableLabels(Array.from(labels).sort())
      setAvailableRegions(Array.from(regions).sort())
      setAvailableGenders(Array.from(genders).sort())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGalleryData()
  }, [reportSlug, selectedLabels, selectedRegions, selectedGenders, ageMin, ageMax])

  // Filter items by media type
  const filteredItems = galleryData?.items.filter(item => {
    if (mediaTypeFilter === 'all') return true
    return item.media_type === mediaTypeFilter
  }) || []

  const handleLabelToggle = (label: string) => {
    setSelectedLabels(prev =>
      prev.includes(label)
        ? prev.filter(l => l !== label)
        : [...prev, label]
    )
  }

  const handleRegionToggle = (region: string) => {
    setSelectedRegions(prev =>
      prev.includes(region)
        ? prev.filter(r => r !== region)
        : [...prev, region]
    )
  }

  const handleGenderToggle = (gender: string) => {
    setSelectedGenders(prev =>
      prev.includes(gender)
        ? prev.filter(g => g !== gender)
        : [...prev, gender]
    )
  }

  const clearFilters = () => {
    setSelectedLabels([])
    setSelectedRegions([])
    setSelectedGenders([])
    setAgeMin(undefined)
    setAgeMax(undefined)
    setMediaTypeFilter('all')
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-lg">Loading media gallery...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  if (!galleryData || galleryData.items.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No media found for this survey.</p>
        <p className="text-sm mt-2">Media appears when photos/videos have been processed with AI analysis.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Media Gallery</h2>
          <div className="flex space-x-4 text-sm">
            <div className="bg-blue-100 px-3 py-1 rounded">
              Total: {filteredItems.length}
            </div>
            <div className="bg-green-100 px-3 py-1 rounded">
              Photos: {filteredItems.filter(item => item.media_type === 'photo').length}
            </div>
            <div className="bg-purple-100 px-3 py-1 rounded">
              Videos: {filteredItems.filter(item => item.media_type === 'video').length}
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium">Filters</h3>
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Clear all filters
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Media Type Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Media Type</label>
            <select
              value={mediaTypeFilter}
              onChange={(e) => setMediaTypeFilter(e.target.value as 'all' | 'photo' | 'video')}
              className="w-full px-3 py-2 border rounded-md text-sm"
            >
              <option value="all">All Media</option>
              <option value="photo">Photos Only</option>
              <option value="video">Videos Only</option>
            </select>
          </div>

          {/* Age Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Age Range</label>
            <div className="flex space-x-2">
              <input
                type="number"
                placeholder="Min"
                value={ageMin || ''}
                onChange={(e) => setAgeMin(e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border rounded-md text-sm"
                min="0"
              />
              <input
                type="number"
                placeholder="Max"
                value={ageMax || ''}
                onChange={(e) => setAgeMax(e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-3 py-2 border rounded-md text-sm"
                min="0"
              />
            </div>
          </div>

          {/* Reporting Labels */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Reporting Labels</label>
            <div className="max-h-32 overflow-y-auto border rounded-md p-2 space-y-1">
              {availableLabels.map(label => (
                <label key={label} className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={selectedLabels.includes(label)}
                    onChange={() => handleLabelToggle(label)}
                    className="mr-2"
                  />
                  <span className="truncate">{label}</span>
                </label>
              ))}
              {availableLabels.length === 0 && (
                <div className="text-gray-500 text-xs">No labels available</div>
              )}
            </div>
          </div>

          {/* Demographics */}
          <div className="space-y-3">
            {/* Regions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Regions</label>
              <div className="flex flex-wrap gap-1">
                {availableRegions.map(region => (
                  <button
                    key={region}
                    onClick={() => handleRegionToggle(region)}
                    className={`px-2 py-1 text-xs rounded ${
                      selectedRegions.includes(region)
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {region}
                  </button>
                ))}
              </div>
            </div>

            {/* Genders */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Genders</label>
              <div className="flex flex-wrap gap-1">
                {availableGenders.map(gender => (
                  <button
                    key={gender}
                    onClick={() => handleGenderToggle(gender)}
                    className={`px-2 py-1 text-xs rounded ${
                      selectedGenders.includes(gender)
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {gender}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="bg-white rounded-lg shadow p-4">
        {filteredItems.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No media matches the current filters.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredItems.map((item) => (
              <div
                key={`${item.id}-${item.media_type}`}
                className="relative group cursor-pointer border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                onClick={() => setSelectedItem(item)}
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
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedItem && (
        <MediaModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      )}
    </div>
  )
}