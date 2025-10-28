import { ReportSettings, AgeRange } from './types';
import { LoadingCard } from '../loading';

interface SettingsTabProps {
  settings: ReportSettings | null;
  settingsLoading: boolean;
  settingsSaving: boolean;
  settingsSuccess: string | null;
  tempAgeRanges: AgeRange[];
  tempQuestionDisplayNames: Record<string, string>;
  onUpdateAgeRange: (index: number, field: 'min' | 'max' | 'label', value: string | number | null) => void;
  onAddAgeRange: () => void;
  onRemoveAgeRange: (index: number) => void;
  onSaveAgeRanges: () => void;
  onUpdateQuestionDisplayName: (questionId: string, value: string) => void;
  onSaveQuestionDisplayNames: () => void;
}

/**
 * Settings Tab Component
 *
 * Displays and manages age ranges and question display names configuration
 */
export function SettingsTab({
  settings,
  settingsLoading,
  settingsSaving,
  settingsSuccess,
  tempAgeRanges,
  tempQuestionDisplayNames,
  onUpdateAgeRange,
  onAddAgeRange,
  onRemoveAgeRange,
  onSaveAgeRanges,
  onUpdateQuestionDisplayName,
  onSaveQuestionDisplayNames
}: SettingsTabProps) {
  if (settingsLoading) {
    return <LoadingCard message="Loading settings..." />;
  }

  return (
    <div className="space-y-8">
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
                    onChange={(e) => onUpdateAgeRange(index, 'min', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white"
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
                    onChange={(e) => onUpdateAgeRange(index, 'max', e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="No limit"
                    className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white placeholder-gray-400"
                  />
                </div>

                <div className="flex-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Label
                  </label>
                  <input
                    type="text"
                    value={range.label}
                    onChange={(e) => onUpdateAgeRange(index, 'label', e.target.value)}
                    className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white placeholder-gray-400"
                    placeholder="e.g., 0-18"
                  />
                </div>

                {tempAgeRanges.length > 1 && (
                  <button
                    onClick={() => onRemoveAgeRange(index)}
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
              onClick={onAddAgeRange}
              className="px-4 py-2 bg-[#D01A8A] text-white rounded hover:bg-[#B0156E]"
            >
              Add Age Range
            </button>

            <button
              onClick={onSaveAgeRanges}
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
                    onChange={(e) => onUpdateQuestionDisplayName(question.id, e.target.value)}
                    placeholder="Leave empty to use original question text"
                    className="w-full px-3 py-2 border rounded-md text-sm text-gray-900 bg-white placeholder-gray-400"
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
              onClick={onSaveQuestionDisplayNames}
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
    </div>
  );
}

export default SettingsTab;
