import { ReportingData } from './types';
import CustomBarChart from './CustomBarChart';
import { LoadingCard } from '../loading';

interface ReportingTabProps {
  reportingData: ReportingData | null;
  reportingLoading: boolean;
}

/**
 * Reporting Tab Component
 *
 * Displays demographics, question responses, and media analysis charts
 */
export function ReportingTab({ reportingData, reportingLoading }: ReportingTabProps) {
  if (reportingLoading) {
    return <LoadingCard message="Loading report data..." />;
  }

  if (!reportingData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">
          No reporting data available
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Summary Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {reportingData.completed_approved_submissions} Approved Submissions
          </h2>
          <p className="text-gray-600">
            Out of {reportingData.total_submissions} total completed submissions for &ldquo;{reportingData.survey_name}&rdquo;
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Generated at {new Date(reportingData.generated_at).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Demographics Charts */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Demographics</h2>
          <p className="text-gray-500 text-sm mt-1">
            Breakdown of approved submissions by demographic categories
          </p>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <CustomBarChart
              chartData={reportingData.demographics.age_ranges}
              title="Age Ranges"
            />
            <CustomBarChart
              chartData={reportingData.demographics.regions}
              title="Regions"
            />
            <CustomBarChart
              chartData={reportingData.demographics.genders}
              title="Genders"
            />
          </div>
        </div>
      </div>

      {/* Question Response Charts */}
      {reportingData.question_responses.length > 0 ? (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Survey Response Analysis</h2>
            <p className="text-gray-500 text-sm mt-1">
              Response distribution for single-choice and multi-choice questions
            </p>
          </div>

          <div className="p-6">
            <div className="space-y-12">
              {reportingData.question_responses.map((question) => (
                <div key={question.question_id} className="border rounded-lg p-6">
                  <div className="mb-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {question.display_name || question.question_text}
                    </h3>
                    {question.display_name && (
                      <p className="text-sm text-gray-500 mb-1">
                        Original: {question.question_text}
                      </p>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-gray-400">
                      <span>Type: {question.question_type}</span>
                      <span>Total responses: {question.chart_data.data.reduce((a, b) => a + b, 0)}</span>
                    </div>
                  </div>

                  <div className="w-full max-w-4xl">
                    <CustomBarChart
                      chartData={question.chart_data}
                      title={question.question_type === 'single'
                        ? 'Single Choice Responses'
                        : 'Multi-Choice Responses (Distinct Submissions per Option)'
                      }
                    />
                  </div>

                  <div className="mt-4 text-xs text-gray-500">
                    {question.question_type === 'single' &&
                      "Single-choice: Shows number of submissions for each answer option"
                    }
                    {question.question_type === 'multi' &&
                      "Multi-choice: Shows number of distinct submissions that selected each option (submissions may select multiple options)"
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center text-gray-500">
            <p>No single-choice or multi-choice questions found in this survey.</p>
            <p className="text-sm mt-2">Charts are only shown for single and multi-choice questions.</p>
          </div>
        </div>
      )}

      {/* Media Analysis Charts */}
      {(reportingData.media_analysis.photos.labels.length > 0 || reportingData.media_analysis.videos.labels.length > 0) && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Media Analysis</h2>
            <p className="text-gray-500 text-sm mt-1">
              AI-generated reporting labels for photos and videos (distinct submission count)
            </p>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {reportingData.media_analysis.photos.labels.length > 0 && (
                <div>
                  <CustomBarChart
                    chartData={reportingData.media_analysis.photos}
                    title="Photo Analysis - Reporting Labels"
                  />
                  <div className="mt-2 text-xs text-gray-500 text-center">
                    Shows distinct submissions with photos containing each reporting label
                  </div>
                </div>
              )}

              {reportingData.media_analysis.videos.labels.length > 0 && (
                <div>
                  <CustomBarChart
                    chartData={reportingData.media_analysis.videos}
                    title="Video Analysis - Reporting Labels"
                  />
                  <div className="mt-2 text-xs text-gray-500 text-center">
                    Shows distinct submissions with videos containing each reporting label
                  </div>
                </div>
              )}
            </div>

            {reportingData.media_analysis.photos.labels.length === 0 && reportingData.media_analysis.videos.labels.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <p>No photo or video analysis data available.</p>
                <p className="text-sm mt-2">Media analysis appears when photos/videos have been processed with AI reporting labels.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ReportingTab;
