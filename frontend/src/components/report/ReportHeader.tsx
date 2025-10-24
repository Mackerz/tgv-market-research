import { SubmissionsResponse, TabType } from './types';

interface ReportHeaderProps {
  reportSlug: string;
  submissions: SubmissionsResponse | null;
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

/**
 * Report Header Component
 *
 * Displays survey name, summary statistics, and tab navigation
 */
export function ReportHeader({
  reportSlug,
  submissions,
  activeTab,
  onTabChange
}: ReportHeaderProps) {
  const tabs = [
    { key: 'submissions' as const, label: 'Submissions' },
    { key: 'reporting' as const, label: 'Reporting' },
    { key: 'media-gallery' as const, label: 'Media Gallery' },
    { key: 'taxonomies' as const, label: 'Taxonomies' },
    { key: 'settings' as const, label: 'Settings' }
  ];

  return (
    <div className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Title and Stats */}
        <div className="flex justify-between items-center py-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {submissions?.survey.name || 'Survey Report'}
            </h1>
            <p className="text-gray-500">Survey: {reportSlug}</p>
          </div>
          <div className="flex space-x-4 text-sm">
            <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded font-medium">
              Total: {submissions?.total_count || 0}
            </div>
            <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded font-medium">
              Pending: {submissions?.pending_count || 0}
            </div>
            <div className="bg-green-100 text-green-800 px-3 py-1 rounded font-medium">
              Approved: {submissions?.approved_count || 0}
            </div>
            <div className="bg-red-100 text-red-800 px-3 py-1 rounded font-medium">
              Rejected: {submissions?.rejected_count || 0}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => onTabChange(tab.key)}
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
  );
}

export default ReportHeader;
