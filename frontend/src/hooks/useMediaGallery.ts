import { useState, useEffect } from 'react'
import { apiClient, ApiError } from '@/lib/api'
import type { MediaGalleryItem } from '@/components/media-gallery/MediaModal'

interface MediaGalleryResponse {
  items: MediaGalleryItem[]
  total_count: number
  photo_count: number
  video_count: number
}

export interface MediaGalleryFilters {
  selectedLabels: string[]
  selectedRegions: string[]
  selectedGenders: string[]
  ageMin?: number
  ageMax?: number
  mediaTypeFilter: 'all' | 'photo' | 'video'
}

export function useMediaGallery(reportSlug: string) {
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
      const params: Record<string, string> = {}
      if (selectedLabels.length > 0) params.labels = selectedLabels.join(',')
      if (selectedRegions.length > 0) params.regions = selectedRegions.join(',')
      if (selectedGenders.length > 0) params.genders = selectedGenders.join(',')
      if (ageMin !== undefined) params.age_min = ageMin.toString()
      if (ageMax !== undefined) params.age_max = ageMax.toString()

      const data = await apiClient.get<MediaGalleryResponse>(
        `/api/reports/${reportSlug}/media-gallery`,
        { params }
      )
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
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGalleryData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  return {
    // Data
    galleryData,
    filteredItems,
    loading,
    error,
    selectedItem,
    setSelectedItem,

    // Filters
    selectedLabels,
    selectedRegions,
    selectedGenders,
    ageMin,
    setAgeMin,
    ageMax,
    setAgeMax,
    mediaTypeFilter,
    setMediaTypeFilter,

    // Available options
    availableLabels,
    availableRegions,
    availableGenders,

    // Actions
    handleLabelToggle,
    handleRegionToggle,
    handleGenderToggle,
    clearFilters,
  }
}
