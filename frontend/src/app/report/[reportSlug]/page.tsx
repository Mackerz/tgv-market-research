'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import MediaGallery from '../../components/MediaGallery'
import {
  ReportHeader,
  SubmissionsTab,
  ReportingTab,
  SettingsTab,
  TaxonomiesTab
} from '@/components/report'
import { useReportData } from '@/hooks/report/useReportData'
import { useReportSettings } from '@/hooks/report/useReportSettings'

type TabType = 'submissions' | 'reporting' | 'media-gallery' | 'taxonomies' | 'settings'

/**
 * Report Page
 *
 * Main page for viewing and managing survey submissions, reporting data,
 * media gallery, taxonomies, and settings for a specific survey report.
 */
export default function ReportPage() {
  const params = useParams()
  const reportSlug = params.reportSlug as string

  // Tab state
  const [activeTab, setActiveTab] = useState<TabType>('submissions')

  // Report data hook - handles submissions, filtering, approval/rejection, reporting
  const {
    // Submissions data
    submissions,
    selectedSubmission,
    loading,
    error,

    // Filtering and sorting
    approvalFilter,
    sortBy,
    sortOrder,
    setApprovalFilter,
    setSortBy,
    setSortOrder,

    // Reporting data
    reportingData,
    reportingLoading,

    // Actions
    fetchSubmissionDetail,
    setSelectedSubmission,
    handleApproveSubmission,
    handleRejectSubmission
  } = useReportData(reportSlug)

  // Settings hook - handles age ranges and question display names
  const {
    settings,
    settingsLoading,
    settingsSaving,
    settingsSuccess,
    tempAgeRanges,
    tempQuestionDisplayNames,
    updateAgeRange,
    addAgeRange,
    removeAgeRange,
    saveAgeRanges,
    updateQuestionDisplayName,
    saveQuestionDisplayNames
  } = useReportSettings(reportSlug, activeTab)

  // Loading state
  if (loading && !submissions) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading report...</div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Report Header with stats and tab navigation */}
      <ReportHeader
        reportSlug={reportSlug}
        submissions={submissions}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Submissions Tab */}
        {activeTab === 'submissions' && (
          <SubmissionsTab
            submissions={submissions}
            selectedSubmission={selectedSubmission}
            approvalFilter={approvalFilter}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onApprovalFilterChange={setApprovalFilter}
            onSortByChange={setSortBy}
            onSortOrderChange={setSortOrder}
            onSubmissionClick={fetchSubmissionDetail}
            onCloseDetail={() => setSelectedSubmission(null)}
            onApprove={handleApproveSubmission}
            onReject={handleRejectSubmission}
          />
        )}

        {/* Reporting Tab */}
        {activeTab === 'reporting' && (
          <ReportingTab
            reportingData={reportingData}
            reportingLoading={reportingLoading}
          />
        )}

        {/* Media Gallery Tab */}
        {activeTab === 'media-gallery' && (
          <MediaGallery reportSlug={reportSlug} />
        )}

        {/* Taxonomies Tab */}
        {activeTab === 'taxonomies' && submissions?.survey && (
          <TaxonomiesTab surveyId={submissions.survey.id} />
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <SettingsTab
            settings={settings}
            settingsLoading={settingsLoading}
            settingsSaving={settingsSaving}
            settingsSuccess={settingsSuccess}
            tempAgeRanges={tempAgeRanges}
            tempQuestionDisplayNames={tempQuestionDisplayNames}
            onUpdateAgeRange={updateAgeRange}
            onAddAgeRange={addAgeRange}
            onRemoveAgeRange={removeAgeRange}
            onSaveAgeRanges={saveAgeRanges}
            onUpdateQuestionDisplayName={updateQuestionDisplayName}
            onSaveQuestionDisplayNames={saveQuestionDisplayNames}
          />
        )}
      </div>
    </div>
  )
}
