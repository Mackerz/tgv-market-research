/**
 * SubmissionDetail Component
 * Displays detailed view of a single submission with all responses
 */

import { apiUrl } from '@/config/api';
import type { Submission, Response } from './types';

interface SubmissionDetailProps {
  submission: Submission;
  responses: Response[];
  onClose: () => void;
  onApprove?: () => Promise<void>;
  onReject?: () => Promise<void>;
}

export default function SubmissionDetail({
  submission,
  responses,
  onClose,
  onApprove,
  onReject,
}: SubmissionDetailProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const renderResponseValue = (response: Response) => {
    // Free text
    if (response.free_text_answer) {
      return (
        <div className="p-3 bg-gray-50 rounded border border-gray-200">
          <p className="text-gray-800">{response.free_text_answer}</p>
        </div>
      );
    }

    // Single choice
    if (response.single_answer) {
      return (
        <div className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
          {response.single_answer}
        </div>
      );
    }

    // Multiple choice
    if (response.multiple_choice_answer && response.multiple_choice_answer.length > 0) {
      return (
        <div className="flex flex-wrap gap-2">
          {response.multiple_choice_answer.map((answer, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
            >
              {answer}
            </span>
          ))}
        </div>
      );
    }

    // Photo
    if (response.photo_url) {
      return (
        <div className="space-y-2">
          <img
            src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(response.photo_url)}`)}
            alt="Response"
            className="max-w-md rounded-lg border border-gray-200"
          />
          {response.media_analysis && (
            <div className="p-3 bg-blue-50 rounded border border-blue-200 text-sm">
              <p className="font-medium text-blue-900 mb-2">AI Analysis:</p>
              <p className="text-gray-700 mb-2">{response.media_analysis.description}</p>
              {response.media_analysis.brands_detected.length > 0 && (
                <div className="mb-2">
                  <span className="font-medium text-blue-900">Brands: </span>
                  <span className="text-gray-700">
                    {response.media_analysis.brands_detected.join(', ')}
                  </span>
                </div>
              )}
              {response.media_analysis.reporting_labels.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {response.media_analysis.reporting_labels.map((label, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                    >
                      {label}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    // Video
    if (response.video_url) {
      return (
        <div className="space-y-2">
          <video
            src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(response.video_url)}`)}
            controls
            className="max-w-md rounded-lg border border-gray-200"
          />
          {response.media_analysis && (
            <div className="p-3 bg-blue-50 rounded border border-blue-200 text-sm">
              <p className="font-medium text-blue-900 mb-2">AI Analysis:</p>
              <p className="text-gray-700 mb-2">{response.media_analysis.description}</p>
              {response.media_analysis.transcript && (
                <div className="mb-2">
                  <span className="font-medium text-blue-900">Transcript: </span>
                  <span className="text-gray-700">{response.media_analysis.transcript}</span>
                </div>
              )}
              {response.media_analysis.brands_detected.length > 0 && (
                <div className="mb-2">
                  <span className="font-medium text-blue-900">Brands: </span>
                  <span className="text-gray-700">
                    {response.media_analysis.brands_detected.join(', ')}
                  </span>
                </div>
              )}
              {response.media_analysis.reporting_labels.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {response.media_analysis.reporting_labels.map((label, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                    >
                      {label}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    return (
      <span className="text-gray-500 italic">No response</span>
    );
  };

  const getApprovalBadge = (isApproved: boolean | null) => {
    if (isApproved === null) {
      return (
        <span className="px-3 py-1 text-sm font-medium bg-yellow-100 text-yellow-800 rounded-full">
          Pending Review
        </span>
      );
    }
    if (isApproved) {
      return (
        <span className="px-3 py-1 text-sm font-medium bg-green-100 text-green-800 rounded-full">
          Approved
        </span>
      );
    }
    return (
      <span className="px-3 py-1 text-sm font-medium bg-red-100 text-red-800 rounded-full">
        Rejected
      </span>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Submission Details
            </h2>
            <div className="flex items-center gap-2">
              {getApprovalBadge(submission.is_approved)}
              {!submission.is_completed && (
                <span className="px-3 py-1 text-sm font-medium bg-gray-100 text-gray-600 rounded-full">
                  Incomplete
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Submission Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Submission Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div>
                <span className="font-medium text-gray-700">Email:</span>
                <span className="ml-2 text-gray-900">{submission.email}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Region:</span>
                <span className="ml-2 text-gray-900">{submission.region}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Age:</span>
                <span className="ml-2 text-gray-900">{submission.age || 'N/A'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Submitted:</span>
                <span className="ml-2 text-gray-900">
                  {formatDate(submission.submitted_at)}
                </span>
              </div>
            </div>
          </div>

          {/* Responses */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Responses</h3>
            <div className="space-y-6">
              {responses.map((response) => (
                <div key={response.id} className="border-b border-gray-200 pb-6 last:border-0">
                  <div className="mb-3">
                    <h4 className="font-medium text-gray-900">{response.question}</h4>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDate(response.responded_at)}
                    </p>
                  </div>
                  {renderResponseValue(response)}
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          {submission.is_approved === null && submission.is_completed && (
            <div className="flex gap-3 pt-4 border-t border-gray-200">
              {onApprove && (
                <button
                  onClick={onApprove}
                  className="flex-1 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
                >
                  Approve Submission
                </button>
              )}
              {onReject && (
                <button
                  onClick={onReject}
                  className="flex-1 px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
                >
                  Reject Submission
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
