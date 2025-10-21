'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'
import { apiUrl } from '@/config/api'

interface Survey {
  id: number
  name: string
  survey_slug: string
  client: string | null
  created_at: string
  is_active: boolean
}

interface SurveysResponse {
  surveys: Survey[]
  total_count: number
}

export default function SurveysListPage() {
  const [surveys, setSurveys] = useState<SurveysResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter and search states
  const [searchTerm, setSearchTerm] = useState('')
  const [clientFilter, setClientFilter] = useState('')
  const [sortBy, setSortBy] = useState<'created_at' | 'name' | 'client'>('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const fetchSurveys = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()

      if (searchTerm) {
        params.append('search', searchTerm)
      }
      if (clientFilter) {
        params.append('client', clientFilter)
      }
      params.append('sort_by', sortBy)
      params.append('sort_order', sortOrder)
      params.append('active_only', 'false') // Show all surveys

      const response = await fetch(apiUrl(`/api/surveys/?${params}`))

      if (!response.ok) {
        throw new Error('Failed to fetch surveys')
      }

      const data = await response.json()
      setSurveys(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setSurveys(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSurveys()
  }, [sortBy, sortOrder])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchSurveys()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Surveys</h1>
          <p className="text-gray-600">View and manage all market research surveys</p>
        </div>

        {/* Search and Filter Bar */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Survey Name Search */}
              <div className="relative">
                <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                  Search Survey Name
                </label>
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    id="search"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search by survey name..."
                    className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Client Filter */}
              <div className="relative">
                <label htmlFor="client" className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Client
                </label>
                <div className="relative">
                  <FunnelIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    id="client"
                    value={clientFilter}
                    onChange={(e) => setClientFilter(e.target.value)}
                    placeholder="Filter by client name..."
                    className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Sort Controls */}
              <div>
                <label htmlFor="sort" className="block text-sm font-medium text-gray-700 mb-1">
                  Sort By
                </label>
                <div className="flex space-x-2">
                  <select
                    id="sort"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'created_at' | 'name' | 'client')}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="created_at">Created Date</option>
                    <option value="name">Survey Name</option>
                    <option value="client">Client Name</option>
                  </select>
                  <button
                    type="button"
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
              </div>
            </div>

            {/* Search Button */}
            <div className="flex justify-end">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Apply Filters
              </button>
            </div>
          </form>
        </div>

        {/* Results Count */}
        {surveys && (
          <div className="mb-4 text-sm text-gray-600">
            Showing {surveys.surveys.length} of {surveys.total_count} surveys
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading surveys...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <p className="font-medium">Error loading surveys</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Surveys Table */}
        {!loading && !error && surveys && surveys.surveys.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Survey Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {surveys.surveys.map((survey) => (
                  <tr key={survey.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{survey.name}</div>
                      <div className="text-sm text-gray-500">{survey.survey_slug}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {survey.client || <span className="text-gray-400 italic">No client</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{formatDate(survey.created_at)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {survey.is_active ? (
                        <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                      <Link
                        href={`/survey/${survey.survey_slug}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Take Survey
                      </Link>
                      <span className="text-gray-300">|</span>
                      <Link
                        href={`/report/${survey.survey_slug}`}
                        className="text-green-600 hover:text-green-900"
                      >
                        View Report
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && surveys && surveys.surveys.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <p className="text-gray-500 text-lg">No surveys found</p>
            <p className="text-gray-400 text-sm mt-2">Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>
    </div>
  )
}
