'use client'

interface MediaGalleryFiltersProps {
  mediaTypeFilter: 'all' | 'photo' | 'video'
  setMediaTypeFilter: (value: 'all' | 'photo' | 'video') => void
  ageMin?: number
  setAgeMin: (value: number | undefined) => void
  ageMax?: number
  setAgeMax: (value: number | undefined) => void
  availableLabels: string[]
  selectedLabels: string[]
  handleLabelToggle: (label: string) => void
  availableRegions: string[]
  selectedRegions: string[]
  handleRegionToggle: (region: string) => void
  availableGenders: string[]
  selectedGenders: string[]
  handleGenderToggle: (gender: string) => void
  clearFilters: () => void
}

export function MediaGalleryFilters({
  mediaTypeFilter,
  setMediaTypeFilter,
  ageMin,
  setAgeMin,
  ageMax,
  setAgeMax,
  availableLabels,
  selectedLabels,
  handleLabelToggle,
  availableRegions,
  selectedRegions,
  handleRegionToggle,
  availableGenders,
  selectedGenders,
  handleGenderToggle,
  clearFilters,
}: MediaGalleryFiltersProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-medium text-gray-900">Filters</h3>
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
            className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white"
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
              className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white placeholder-gray-400"
              min="0"
            />
            <input
              type="number"
              placeholder="Max"
              value={ageMax || ''}
              onChange={(e) => setAgeMax(e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white placeholder-gray-400"
              min="0"
            />
          </div>
        </div>

        {/* Reporting Labels */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Reporting Labels</label>
          <div className="max-h-32 overflow-y-auto border rounded-md p-2 space-y-1 bg-white">
            {availableLabels.map(label => (
              <label key={label} className="flex items-center text-sm hover:bg-gray-50 px-1 py-0.5 rounded cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedLabels.includes(label)}
                  onChange={() => handleLabelToggle(label)}
                  className="mr-2 flex-shrink-0"
                />
                <span className="truncate text-gray-900">{label}</span>
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
  )
}
