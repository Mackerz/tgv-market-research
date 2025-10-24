interface SurveyDetailsFormProps {
  surveySlug: string;
  surveyName: string;
  client: string;
  isActive: boolean;
  completeRedirectUrl: string;
  screenoutRedirectUrl: string;
  isEditMode: boolean;
  onSurveySlugChange: (value: string) => void;
  onSurveyNameChange: (value: string) => void;
  onClientChange: (value: string) => void;
  onIsActiveChange: (value: boolean) => void;
  onCompleteRedirectUrlChange: (value: string) => void;
  onScreenoutRedirectUrlChange: (value: string) => void;
}

export default function SurveyDetailsForm({
  surveySlug,
  surveyName,
  client,
  isActive,
  completeRedirectUrl,
  screenoutRedirectUrl,
  isEditMode,
  onSurveySlugChange,
  onSurveyNameChange,
  onClientChange,
  onIsActiveChange,
  onCompleteRedirectUrlChange,
  onScreenoutRedirectUrlChange
}: SurveyDetailsFormProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Survey Details</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Survey Slug *
          </label>
          <input
            type="text"
            value={surveySlug}
            onChange={(e) => onSurveySlugChange(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'))}
            placeholder="my-survey-slug"
            className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
            required
            disabled={isEditMode}
            title={isEditMode ? 'Survey slug cannot be changed' : ''}
          />
          <p className="text-xs text-gray-500 mt-1">
            {isEditMode ? 'Survey slug cannot be changed after creation' : 'URL-friendly identifier (lowercase, hyphens only)'}
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Survey Name *
          </label>
          <input
            type="text"
            value={surveyName}
            onChange={(e) => onSurveyNameChange(e.target.value)}
            placeholder="My Survey Name"
            className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Client (Optional)
          </label>
          <input
            type="text"
            value={client}
            onChange={(e) => onClientChange(e.target.value)}
            placeholder="Client name"
            className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
          />
        </div>

        <div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => onIsActiveChange(e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm font-medium text-gray-700">Survey is Active</span>
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Complete Redirect URL (Optional)
          </label>
          <input
            type="url"
            value={completeRedirectUrl}
            onChange={(e) => onCompleteRedirectUrlChange(e.target.value)}
            placeholder="https://partner.com/complete"
            className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
          />
          <p className="text-xs text-gray-500 mt-1">Redirect URL when survey is completed</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Screenout Redirect URL (Optional)
          </label>
          <input
            type="url"
            value={screenoutRedirectUrl}
            onChange={(e) => onScreenoutRedirectUrlChange(e.target.value)}
            placeholder="https://partner.com/screenout"
            className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
          />
          <p className="text-xs text-gray-500 mt-1">Redirect URL when survey is screened out (early termination)</p>
        </div>
      </div>
    </div>
  );
}
