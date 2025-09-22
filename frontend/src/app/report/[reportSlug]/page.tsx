'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'

interface Submission {
  id: number
  email: string
  phone_number: string
  region: string
  gender: string
  age: number
  submitted_at: string
  is_approved: boolean
  is_completed: boolean
}

interface SubmissionsResponse {
  submissions: Submission[]
  total_count: number
  approved_count: number
  rejected_count: number
  survey: {
    id: number
    name: string
    survey_slug: string
  }
}

interface MediaAnalysis {
  id: number
  description: string
  transcript: string
  brands_detected: string[]
  reporting_labels: string[]
}

interface Response {
  id: number
  question: string
  question_type: string
  single_answer: string | null
  free_text_answer: string | null
  multiple_choice_answer: string[] | null
  photo_url: string | null
  video_url: string | null
  responded_at: string
  media_analysis: MediaAnalysis | null
}

interface SubmissionDetailResponse {
  submission: Submission
  responses: Response[]
  survey: {
    id: number
    name: string
    survey_slug: string
  }
}

interface AgeRange {
  min: number
  max: number | null
  label: string
}

interface QuestionDisplayName {
  id: number
  question_id: string
  question_text: string
  display_name: string | null
  report_settings_id: number
  created_at: string
  updated_at: string | null
}

interface AvailableQuestion {
  id: string
  question: string
  question_type: string
}

interface ReportSettings {
  id: number
  survey_id: number
  age_ranges: AgeRange[]
  created_at: string
  updated_at: string | null
  question_display_names: QuestionDisplayName[]
  available_questions: AvailableQuestion[]
}

type TabType = 'submissions' | 'reporting' | 'settings'
type ApprovalFilter = 'all' | 'approved' | 'rejected'
type SortBy = 'submitted_at' | 'email' | 'age' | 'region'

export default function ReportPage() {
  const params = useParams()
  const reportSlug = params.reportSlug as string

  const [activeTab, setActiveTab] = useState<TabType>('submissions')
  const [submissions, setSubmissions] = useState<SubmissionsResponse | null>(null)
  const [selectedSubmission, setSelectedSubmission] = useState<SubmissionDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filtering and sorting
  const [approvalFilter, setApprovalFilter] = useState<ApprovalFilter>('all')
  const [sortBy, setSortBy] = useState<SortBy>('submitted_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Settings state
  const [settings, setSettings] = useState<ReportSettings | null>(null)
  const [settingsLoading, setSettingsLoading] = useState(false)
  const [settingsSaving, setSettingsSaving] = useState(false)
  const [tempAgeRanges, setTempAgeRanges] = useState<AgeRange[]>([])
  const [tempQuestionDisplayNames, setTempQuestionDisplayNames] = useState<{[key: string]: string}>({})
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null)

  const fetchSubmissions = async () => {
    try {
      setLoading(true)
      const approved = approvalFilter === 'all' ? undefined : approvalFilter === 'approved'

      const params = new URLSearchParams()
      if (approved !== undefined) params.append('approved', approved.toString())
      params.append('sort_by', sortBy)
      params.append('sort_order', sortOrder)

      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/submissions?${params}`)
      if (!response.ok) {
        throw new Error('Failed to fetch submissions')
      }

      const data: SubmissionsResponse = await response.json()
      setSubmissions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const fetchSubmissionDetail = async (submissionId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/submissions/${submissionId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch submission details')
      }

      const data: SubmissionDetailResponse = await response.json()
      setSelectedSubmission(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const handleApproveSubmission = async (submissionId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/submissions/${submissionId}/approve`, {
        method: 'PUT'
      })
      if (!response.ok) {
        throw new Error('Failed to approve submission')
      }

      // Refresh submissions list and selected submission
      await fetchSubmissions()
      if (selectedSubmission?.submission.id === submissionId) {
        await fetchSubmissionDetail(submissionId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const handleRejectSubmission = async (submissionId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/submissions/${submissionId}/reject`, {
        method: 'PUT'
      })
      if (!response.ok) {
        throw new Error('Failed to reject submission')
      }

      // Refresh submissions list and selected submission
      await fetchSubmissions()
      if (selectedSubmission?.submission.id === submissionId) {
        await fetchSubmissionDetail(submissionId)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  // Settings functions
  const fetchSettings = async () => {
    try {
      setSettingsLoading(true)
      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/settings`)
      if (!response.ok) {
        throw new Error('Failed to fetch settings')
      }

      const data: ReportSettings = await response.json()
      setSettings(data)

      // Set temporary state for editing
      setTempAgeRanges([...data.age_ranges])
      const questionDisplayNames: {[key: string]: string} = {}
      data.question_display_names.forEach(q => {
        questionDisplayNames[q.question_id] = q.display_name || ''
      })
      setTempQuestionDisplayNames(questionDisplayNames)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSettingsLoading(false)
    }
  }

  const saveAgeRanges = async () => {
    try {
      setSettingsSaving(true)
      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/settings/age-ranges`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tempAgeRanges)
      })

      if (!response.ok) {
        throw new Error('Failed to save age ranges')
      }

      setSettingsSuccess('Age ranges updated successfully')
      setTimeout(() => setSettingsSuccess(null), 3000)
      await fetchSettings() // Refresh settings
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSettingsSaving(false)
    }
  }

  const saveQuestionDisplayNames = async () => {
    try {
      setSettingsSaving(true)
      const questionUpdates = Object.entries(tempQuestionDisplayNames).map(([questionId, displayName]) => ({
        question_id: questionId,
        display_name: displayName || null
      }))

      const response = await fetch(`http://localhost:8000/api/reports/${reportSlug}/settings/question-display-names`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question_updates: questionUpdates })
      })

      if (!response.ok) {
        throw new Error('Failed to save question display names')
      }

      setSettingsSuccess('Question display names updated successfully')
      setTimeout(() => setSettingsSuccess(null), 3000)
      await fetchSettings() // Refresh settings
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSettingsSaving(false)
    }
  }

  const addAgeRange = () => {
    const newRange: AgeRange = {
      min: 0,
      max: null,
      label: 'New Range'
    }
    setTempAgeRanges([...tempAgeRanges, newRange])
  }

  const updateAgeRange = (index: number, field: keyof AgeRange, value: any) => {
    const updatedRanges = [...tempAgeRanges]
    updatedRanges[index] = { ...updatedRanges[index], [field]: value }
    setTempAgeRanges(updatedRanges)
  }

  const removeAgeRange = (index: number) => {
    const updatedRanges = tempAgeRanges.filter((_, i) => i !== index)
    setTempAgeRanges(updatedRanges)
  }

  const updateQuestionDisplayName = (questionId: string, displayName: string) => {
    setTempQuestionDisplayNames({
      ...tempQuestionDisplayNames,
      [questionId]: displayName
    })
  }

  useEffect(() => {
    fetchSubmissions()
  }, [reportSlug, approvalFilter, sortBy, sortOrder])

  useEffect(() => {
    if (activeTab === 'settings') {
      fetchSettings()
    }
  }, [activeTab, reportSlug])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusBadge = (submission: Submission) => {
    if (submission.is_approved) {
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Approved</span>
    } else {
      return <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs">Rejected</span>
    }
  }

  if (loading && !submissions) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading report...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {submissions?.survey.name || 'Survey Report'}
              </h1>
              <p className="text-gray-500">Survey: {reportSlug}</p>
            </div>
            <div className="flex space-x-4 text-sm">
              <div className="bg-blue-100 px-3 py-1 rounded">
                Total: {submissions?.total_count || 0}
              </div>
              <div className="bg-green-100 px-3 py-1 rounded">
                Approved: {submissions?.approved_count || 0}
              </div>
              <div className="bg-red-100 px-3 py-1 rounded">
                Rejected: {submissions?.rejected_count || 0}
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { key: 'submissions', label: 'Submissions' },
                { key: 'reporting', label: 'Reporting' },
                { key: 'settings', label: 'Settings' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as TabType)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'submissions' && (
          <div className="flex space-x-6">
            {/* Submissions Table */}
            <div className={selectedSubmission ? 'w-1/2' : 'w-full'}>
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                  <h2 className="text-xl font-semibold">Submissions</h2>

                  {/* Filters */}
                  <div className="mt-4 flex space-x-4">
                    <select
                      value={approvalFilter}
                      onChange={(e) => setApprovalFilter(e.target.value as ApprovalFilter)}
                      className="px-3 py-2 border rounded-md"
                    >
                      <option value="all">All Submissions</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                    </select>

                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as SortBy)}
                      className="px-3 py-2 border rounded-md"
                    >
                      <option value="submitted_at">Date Submitted</option>
                      <option value="email">Email</option>
                      <option value="age">Age</option>
                      <option value="region">Region</option>
                    </select>

                    <select
                      value={sortOrder}
                      onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                      className="px-3 py-2 border rounded-md"
                    >
                      <option value="desc">Descending</option>
                      <option value="asc">Ascending</option>
                    </select>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Respondent
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Demographics
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Submitted
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {submissions?.submissions.map((submission) => (
                        <tr
                          key={submission.id}
                          onClick={() => fetchSubmissionDetail(submission.id)}
                          className="hover:bg-gray-50 cursor-pointer"
                        >
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {submission.email}
                              </div>
                              <div className="text-sm text-gray-500">
                                {submission.phone_number}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">
                              {submission.gender}, {submission.age}
                            </div>
                            <div className="text-sm text-gray-500">
                              {submission.region}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatDate(submission.submitted_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {getStatusBadge(submission)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Submission Detail */}
            {selectedSubmission && (
              <div className="w-1/2">
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6 border-b">
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-semibold">
                        Submission #{selectedSubmission.submission.id}
                      </h2>
                      <button
                        onClick={() => setSelectedSubmission(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        ✕
                      </button>
                    </div>

                    <div className="mt-4">
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(selectedSubmission.submission)}
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleApproveSubmission(selectedSubmission.submission.id)}
                            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => handleRejectSubmission(selectedSubmission.submission.id)}
                            className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 space-y-6">
                    {selectedSubmission.responses.map((response) => (
                      <div key={response.id} className="border-b pb-4">
                        <h3 className="font-medium text-gray-900 mb-2">
                          {response.question}
                        </h3>

                        {/* Answer */}
                        <div className="mb-3">
                          {response.single_answer && (
                            <p className="text-gray-700">{response.single_answer}</p>
                          )}
                          {response.free_text_answer && (
                            <p className="text-gray-700">{response.free_text_answer}</p>
                          )}
                          {response.multiple_choice_answer && (
                            <ul className="list-disc list-inside text-gray-700">
                              {response.multiple_choice_answer.map((answer, idx) => (
                                <li key={idx}>{answer}</li>
                              ))}
                            </ul>
                          )}
                          {response.photo_url && (
                            <div className="mb-3">
                              <div className="text-blue-600 mb-2">📷 Photo:</div>
                              <img
                                src={`http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.photo_url)}`}
                                alt="Response photo"
                                className="max-w-full h-auto max-h-64 rounded border"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = 'none';
                                  const errorDiv = document.createElement('div');
                                  errorDiv.textContent = 'Error loading image';
                                  errorDiv.className = 'text-red-500 text-sm';
                                  target.parentNode?.insertBefore(errorDiv, target.nextSibling);
                                }}
                              />
                              <div className="text-sm text-gray-500 mt-1">
                                {response.photo_url}
                              </div>
                            </div>
                          )}
                          {response.video_url && (
                            <div className="mb-3">
                              <div className="text-blue-600 mb-2">🎥 Video:</div>
                              <video
                                controls
                                preload="metadata"
                                crossOrigin="anonymous"
                                className="max-w-full h-auto max-h-64 rounded border"
                                onError={(e) => {
                                  console.error('Video loading error:', e);
                                  const target = e.target as HTMLVideoElement;
                                  target.style.display = 'none';
                                  const errorDiv = document.createElement('div');
                                  errorDiv.innerHTML = `<div class="text-red-500 text-sm">Error loading video</div><div class="text-xs text-gray-400 mt-1">Try <a href="http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}" target="_blank" class="underline">opening video directly</a></div>`;
                                  target.parentNode?.insertBefore(errorDiv, target.nextSibling);
                                }}
                                onLoadStart={() => console.log('Video loading started')}
                                onCanPlay={() => console.log('Video can play')}
                              >
                                {/* Primary MP4 source */}
                                <source
                                  src={`http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}`}
                                  type="video/mp4; codecs=avc1.42E01E,mp4a.40.2"
                                />
                                {/* Fallback MP4 without codecs */}
                                <source
                                  src={`http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}`}
                                  type="video/mp4"
                                />
                                {/* Fallback generic video */}
                                <source
                                  src={`http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}`}
                                  type="video/*"
                                />
                                <p className="text-red-500 text-sm">
                                  Your browser does not support the video tag.
                                  <a
                                    href={`http://localhost:8000/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}`}
                                    target="_blank"
                                    className="underline ml-1"
                                  >
                                    Click to download video
                                  </a>
                                </p>
                              </video>
                              <div className="text-sm text-gray-500 mt-1">
                                {response.video_url}
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Media Analysis */}
                        {response.media_analysis && (
                          <div className="bg-gray-50 p-3 rounded">
                            <h4 className="font-medium text-sm text-gray-900 mb-2">
                              AI Analysis
                            </h4>

                            {response.media_analysis.description && (
                              <div className="mb-2">
                                <strong className="text-xs text-gray-600">Description:</strong>
                                <p className="text-sm text-gray-700">
                                  {response.media_analysis.description}
                                </p>
                              </div>
                            )}

                            {response.media_analysis.transcript && (
                              <div className="mb-2">
                                <strong className="text-xs text-gray-600">Transcript:</strong>
                                <p className="text-sm text-gray-700">
                                  {response.media_analysis.transcript}
                                </p>
                              </div>
                            )}

                            {response.media_analysis.brands_detected.length > 0 && (
                              <div className="mb-2">
                                <strong className="text-xs text-gray-600">Brands:</strong>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {response.media_analysis.brands_detected.map((brand, idx) => (
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

                            {response.media_analysis.reporting_labels.length > 0 && (
                              <div>
                                <strong className="text-xs text-gray-600">Reporting Labels:</strong>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {response.media_analysis.reporting_labels.map((label, idx) => (
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
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'reporting' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Reporting</h2>
            <p className="text-gray-500">Coming soon...</p>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-8">
            {settingsLoading ? (
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-center">Loading settings...</div>
              </div>
            ) : (
              <>
                {/* Success Message */}
                {settingsSuccess && (
                  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                    {settingsSuccess}
                  </div>
                )}

                {/* Age Ranges Section */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6 border-b">
                    <h2 className="text-xl font-semibold">Age Ranges</h2>
                    <p className="text-gray-500 text-sm mt-1">
                      Configure age ranges for reporting demographics. These will be used to categorize respondents in reports.
                    </p>
                  </div>

                  <div className="p-6">
                    <div className="space-y-4">
                      {tempAgeRanges.map((range, index) => (
                        <div key={index} className="flex items-center space-x-4 p-3 border rounded">
                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Min Age
                            </label>
                            <input
                              type="number"
                              min="0"
                              value={range.min}
                              onChange={(e) => updateAgeRange(index, 'min', parseInt(e.target.value) || 0)}
                              className="w-full px-3 py-2 border rounded-md text-sm"
                            />
                          </div>

                          <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Max Age
                            </label>
                            <input
                              type="number"
                              min="0"
                              value={range.max || ''}
                              onChange={(e) => updateAgeRange(index, 'max', e.target.value ? parseInt(e.target.value) : null)}
                              placeholder="No limit"
                              className="w-full px-3 py-2 border rounded-md text-sm"
                            />
                          </div>

                          <div className="flex-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Label
                            </label>
                            <input
                              type="text"
                              value={range.label}
                              onChange={(e) => updateAgeRange(index, 'label', e.target.value)}
                              className="w-full px-3 py-2 border rounded-md text-sm"
                              placeholder="e.g., 0-18"
                            />
                          </div>

                          {tempAgeRanges.length > 1 && (
                            <button
                              onClick={() => removeAgeRange(index)}
                              className="px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="flex space-x-4 mt-6">
                      <button
                        onClick={addAgeRange}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Add Age Range
                      </button>

                      <button
                        onClick={saveAgeRanges}
                        disabled={settingsSaving}
                        className={`px-4 py-2 rounded ${
                          settingsSaving
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-green-600 hover:bg-green-700'
                        } text-white`}
                      >
                        {settingsSaving ? 'Saving...' : 'Save Age Ranges'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Question Display Names Section */}
                <div className="bg-white rounded-lg shadow">
                  <div className="p-6 border-b">
                    <h2 className="text-xl font-semibold">Question Display Names</h2>
                    <p className="text-gray-500 text-sm mt-1">
                      Set custom display names for questions in reports. If left empty, the original question text will be used.
                    </p>
                  </div>

                  <div className="p-6">
                    <div className="space-y-4">
                      {settings?.available_questions.map((question) => (
                        <div key={question.id} className="border rounded p-4">
                          <div className="mb-2">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Original Question
                            </label>
                            <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                              {question.question}
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              Type: {question.question_type}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Display Name (Optional)
                            </label>
                            <input
                              type="text"
                              value={tempQuestionDisplayNames[question.id] || ''}
                              onChange={(e) => updateQuestionDisplayName(question.id, e.target.value)}
                              placeholder="Leave empty to use original question text"
                              className="w-full px-3 py-2 border rounded-md text-sm"
                            />
                            {tempQuestionDisplayNames[question.id] && (
                              <div className="text-xs text-gray-500 mt-1">
                                Preview: {tempQuestionDisplayNames[question.id]}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="mt-6">
                      <button
                        onClick={saveQuestionDisplayNames}
                        disabled={settingsSaving}
                        className={`px-4 py-2 rounded ${
                          settingsSaving
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-green-600 hover:bg-green-700'
                        } text-white`}
                      >
                        {settingsSaving ? 'Saving...' : 'Save Question Display Names'}
                      </button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}