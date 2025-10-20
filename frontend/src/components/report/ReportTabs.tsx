/**
 * ReportTabs Component
 * Tab navigation for the report page
 */

interface ReportTabsProps {
  activeTab: 'submissions' | 'reporting' | 'media-gallery' | 'settings';
  onTabChange: (tab: 'submissions' | 'reporting' | 'media-gallery' | 'settings') => void;
  surveyName: string;
}

export default function ReportTabs({ activeTab, onTabChange, surveyName }: ReportTabsProps) {
  const tabs = [
    { id: 'submissions' as const, label: 'Submissions', icon: '📋' },
    { id: 'reporting' as const, label: 'Reporting', icon: '📊' },
    { id: 'media-gallery' as const, label: 'Media Gallery', icon: '🖼️' },
    { id: 'settings' as const, label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{surveyName}</h1>

          <div className="flex space-x-1 sm:space-x-2 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`
                  px-3 sm:px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap text-sm sm:text-base
                  ${activeTab === tab.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
