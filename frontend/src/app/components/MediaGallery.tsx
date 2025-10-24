'use client'

import { useMediaGallery } from '@/hooks/useMediaGallery'
import { MediaModal } from '@/components/media-gallery/MediaModal'
import { MediaGalleryFilters } from '@/components/media-gallery/MediaGalleryFilters'
import { MediaGridItem } from '@/components/media-gallery/MediaGridItem'

interface MediaGalleryProps {
  reportSlug: string
}

export default function MediaGallery({ reportSlug }: MediaGalleryProps) {
  const {
    galleryData,
    filteredItems,
    loading,
    error,
    selectedItem,
    setSelectedItem,
    selectedLabels,
    selectedRegions,
    selectedGenders,
    ageMin,
    setAgeMin,
    ageMax,
    setAgeMax,
    mediaTypeFilter,
    setMediaTypeFilter,
    availableLabels,
    availableRegions,
    availableGenders,
    handleLabelToggle,
    handleRegionToggle,
    handleGenderToggle,
    clearFilters,
  } = useMediaGallery(reportSlug)

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
          <h2 className="text-xl font-semibold text-gray-900">Media Gallery</h2>
          <div className="flex space-x-4 text-sm">
            <div className="bg-blue-100 px-3 py-1 rounded text-blue-800">
              Total: {filteredItems.length}
            </div>
            <div className="bg-green-100 px-3 py-1 rounded text-green-800">
              Photos: {filteredItems.filter(item => item.media_type === 'photo').length}
            </div>
            <div className="bg-purple-100 px-3 py-1 rounded text-purple-800">
              Videos: {filteredItems.filter(item => item.media_type === 'video').length}
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <MediaGalleryFilters
        mediaTypeFilter={mediaTypeFilter}
        setMediaTypeFilter={setMediaTypeFilter}
        ageMin={ageMin}
        setAgeMin={setAgeMin}
        ageMax={ageMax}
        setAgeMax={setAgeMax}
        availableLabels={availableLabels}
        selectedLabels={selectedLabels}
        handleLabelToggle={handleLabelToggle}
        availableRegions={availableRegions}
        selectedRegions={selectedRegions}
        handleRegionToggle={handleRegionToggle}
        availableGenders={availableGenders}
        selectedGenders={selectedGenders}
        handleGenderToggle={handleGenderToggle}
        clearFilters={clearFilters}
      />

      {/* Gallery Grid */}
      <div className="bg-white rounded-lg shadow p-4">
        {filteredItems.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No media matches the current filters.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredItems.map((item) => (
              <MediaGridItem
                key={`${item.id}-${item.media_type}`}
                item={item}
                onClick={() => setSelectedItem(item)}
              />
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
