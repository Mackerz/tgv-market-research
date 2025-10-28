'use client';

import { useState, useEffect } from 'react';
import {
  TaxonomyOverview,
  ReportingLabel,
  SystemLabelWithCount,
  MediaPreview,
  ReportingLabelUpdate,
  ReportingLabelCreate
} from '@/types/taxonomy';
import { logger } from '@/lib/logger';
import { taxonomyService, surveyService } from '@/lib/api';
import { useErrorHandler } from '@/hooks/useErrorHandler';
import { DEFAULT_MEDIA_PREVIEW_LIMIT, DEFAULT_TAXONOMY_CATEGORIES } from '@/config/constants';
import { apiUrl } from '@/config/api';

interface TaxonomiesTabProps {
  surveyId: number;
}

export default function TaxonomiesTab({ surveyId }: TaxonomiesTabProps) {
  // Use error handling hook
  const { error, handleError, clearError } = useErrorHandler();

  const [taxonomy, setTaxonomy] = useState<TaxonomyOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [selectedLabel, setSelectedLabel] = useState<SystemLabelWithCount | null>(null);
  const [mediaPreviews, setMediaPreviews] = useState<MediaPreview[]>([]);
  const [editingLabel, setEditingLabel] = useState<number | null>(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [creatingNew, setCreatingNew] = useState(false);
  const [newLabelName, setNewLabelName] = useState('');
  const [newLabelDescription, setNewLabelDescription] = useState('');
  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null);
  const [availableQuestions, setAvailableQuestions] = useState<Array<{ id: string; question: string; type: string }>>([]);

  useEffect(() => {
    fetchSurveyQuestions();
  }, [surveyId]);

  useEffect(() => {
    if (selectedQuestionId) {
      fetchTaxonomy();
    }
  }, [selectedQuestionId]);

  const fetchSurveyQuestions = async () => {
    try {
      const survey = await surveyService.getSurvey(surveyId);
      // Filter for only photo and video questions
      const mediaQuestions = survey.survey_flow
        .filter(q => q.question_type === 'photo' || q.question_type === 'video')
        .map(q => ({
          id: q.id,
          question: q.question,
          type: q.question_type
        }));
      setAvailableQuestions(mediaQuestions);

      // Auto-select first media question if available
      if (mediaQuestions.length > 0 && !selectedQuestionId) {
        setSelectedQuestionId(mediaQuestions[0].id);
      }
    } catch (err) {
      logger.error('Error fetching survey questions', err);
      handleError(err);
    }
  };

  const fetchTaxonomy = async () => {
    try {
      setLoading(true);
      const data = await taxonomyService.getTaxonomy(surveyId, selectedQuestionId || undefined);
      setTaxonomy(data);
      clearError();
    } catch (err) {
      logger.error('Error fetching taxonomy', err);
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const generateTaxonomy = async () => {
    try {
      setGenerating(true);
      await taxonomyService.generateTaxonomy(surveyId, DEFAULT_TAXONOMY_CATEGORIES);
      await fetchTaxonomy();
    } catch (err) {
      logger.error('Error generating taxonomy:', err);
      handleError(err);
    } finally {
      setGenerating(false);
    }
  };

  const fetchMediaPreviews = async (systemLabel: string) => {
    try {
      const data = await taxonomyService.getMediaPreviews(
        surveyId,
        systemLabel,
        DEFAULT_MEDIA_PREVIEW_LIMIT,
        selectedQuestionId || undefined
      );
      setMediaPreviews(data);
    } catch (err) {
      logger.error('Error fetching media previews:', err);
      handleError(err);
    }
  };

  const addSystemLabel = async (reportingLabelId: number, systemLabel: string) => {
    try {
      await taxonomyService.addSystemLabel(reportingLabelId, systemLabel);
      await fetchTaxonomy();
      setSelectedLabel(null);
      setMediaPreviews([]);
    } catch (err) {
      logger.error('Error adding system label:', err);
      handleError(err);
    }
  };

  const removeSystemLabel = async (reportingLabelId: number, systemLabel: string) => {
    try {
      await taxonomyService.removeSystemLabel(reportingLabelId, systemLabel);
      await fetchTaxonomy();
    } catch (err) {
      logger.error('Error removing system label:', err);
      handleError(err);
    }
  };

  const updateReportingLabel = async (labelId: number) => {
    try {
      const updateData: ReportingLabelUpdate = {
        label_name: editName,
        description: editDescription || undefined,
      };
      await taxonomyService.updateReportingLabel(labelId, updateData);
      await fetchTaxonomy();
      setEditingLabel(null);
    } catch (err) {
      logger.error('Error updating label:', err);
      handleError(err);
    }
  };

  const createReportingLabel = async () => {
    try {
      const createData: ReportingLabelCreate = {
        survey_id: surveyId,
        label_name: newLabelName,
        description: newLabelDescription || undefined,
        is_ai_generated: false,
        system_labels: [],
      };
      await taxonomyService.createReportingLabel(createData);
      await fetchTaxonomy();
      setCreatingNew(false);
      setNewLabelName('');
      setNewLabelDescription('');
    } catch (err) {
      logger.error('Error creating label:', err);
      handleError(err);
    }
  };

  const deleteReportingLabel = async (labelId: number) => {
    if (!confirm('Delete this reporting label? This is only possible if no system labels are mapped to it.')) {
      return;
    }
    try {
      await taxonomyService.deleteReportingLabel(labelId);
      await fetchTaxonomy();
    } catch (err) {
      logger.error('Error deleting label:', err);
      handleError(err);
      alert('Cannot delete label. Remove all system label mappings first.');
    }
  };

  const handleLabelClick = (label: SystemLabelWithCount) => {
    setSelectedLabel(label);
    fetchMediaPreviews(label.label);
  };

  const startEditingLabel = (label: ReportingLabel) => {
    setEditingLabel(label.id);
    setEditName(label.label_name);
    setEditDescription(label.description || '');
  };

  if (loading) {
    return <div className="text-center py-8">Loading taxonomy...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-start justify-between">
          <div className="flex items-start">
            <svg className="w-5 h-5 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-red-600 hover:text-red-800 ml-4"
            aria-label="Dismiss error"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold text-gray-900">Label Taxonomy</h2>
          <p className="text-sm text-gray-600 mt-1 break-words">
            Map system-generated labels to high-level reporting categories
          </p>
        </div>
        <div className="flex flex-shrink-0 space-x-3">
          <button
            onClick={() => setCreatingNew(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 whitespace-nowrap"
          >
            + New Category
          </button>
          <button
            onClick={generateTaxonomy}
            disabled={generating}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 whitespace-nowrap"
          >
            {generating ? 'Generating...' : 'Generate with AI'}
          </button>
        </div>
      </div>

      {/* Question Selector */}
      {availableQuestions.length > 0 ? (
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Question (Photo/Video only):
          </label>
          <select
            value={selectedQuestionId || ''}
            onChange={(e) => setSelectedQuestionId(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 font-medium"
          >
            {availableQuestions.map((q) => (
              <option key={q.id} value={q.id} className="text-gray-900">
                {q.question} ({q.type === 'photo' ? 'Photo' : 'Video'})
              </option>
            ))}
          </select>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
          <p className="text-sm text-yellow-800">
            No photo or video questions found in this survey. Taxonomy is only available for media questions.
          </p>
        </div>
      )}

      {/* Stats */}
      {taxonomy && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-700">{taxonomy.reporting_labels.length}</div>
            <div className="text-sm text-blue-600">Reporting Categories</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-700">{taxonomy.unmapped_system_labels.length}</div>
            <div className="text-sm text-yellow-600">Unmapped Labels</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-gray-700">{taxonomy.total_media_items}</div>
            <div className="text-sm text-gray-600">Total Media Items</div>
          </div>
        </div>
      )}

      {/* Create New Label Modal */}
      {creatingNew && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-96">
            <h3 className="text-lg font-bold mb-4">Create New Reporting Label</h3>
            <input
              type="text"
              placeholder="Label Name"
              value={newLabelName}
              onChange={(e) => setNewLabelName(e.target.value)}
              className="w-full px-3 py-2 border rounded mb-3"
            />
            <textarea
              placeholder="Description (optional)"
              value={newLabelDescription}
              onChange={(e) => setNewLabelDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded mb-4"
              rows={3}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setCreatingNew(false);
                  setNewLabelName('');
                  setNewLabelDescription('');
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={createReportingLabel}
                disabled={!newLabelName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column - Reporting Labels */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Reporting Categories</h3>
          {taxonomy?.reporting_labels.map((label) => (
            <div key={label.id} className="bg-white p-4 rounded-lg shadow">
              {editingLabel === label.id ? (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="w-full px-3 py-2 border rounded"
                  />
                  <textarea
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    className="w-full px-3 py-2 border rounded"
                    rows={2}
                    placeholder="Description (optional)"
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={() => setEditingLabel(null)}
                      className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => updateReportingLabel(label.id)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Save
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-gray-900">{label.label_name}</h4>
                      {label.description && (
                        <p className="text-sm text-gray-600 mt-1">{label.description}</p>
                      )}
                      <span className="text-xs text-gray-500">
                        {label.is_ai_generated ? 'AI Generated' : 'User Created'}
                      </span>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => startEditingLabel(label)}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => deleteReportingLabel(label.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="text-xs text-gray-500 mb-2">
                      Mapped Labels ({label.label_mappings.length}):
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {label.label_mappings.map((mapping) => (
                        <span
                          key={mapping.id}
                          className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded text-xs"
                        >
                          {mapping.system_label}
                          <button
                            onClick={() => removeSystemLabel(label.id, mapping.system_label)}
                            className="ml-2 text-green-600 hover:text-green-900"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                      {label.label_mappings.length === 0 && (
                        <span className="text-xs text-gray-400">No labels mapped yet</span>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>

        {/* Right Column - Unmapped System Labels */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Unmapped System Labels</h3>
          <div className="space-y-2">
            {taxonomy?.unmapped_system_labels.map((label) => (
              <div
                key={label.label}
                className={`bg-white p-3 rounded-lg shadow cursor-pointer hover:bg-gray-50 ${
                  selectedLabel?.label === label.label ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => handleLabelClick(label)}
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium text-gray-900">{label.label}</span>
                  <span className="text-sm text-gray-500">({label.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Selected Label Details and Media Preview */}
      {selectedLabel && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-lg font-semibold">
                {selectedLabel.label} <span className="text-gray-500 text-sm">({selectedLabel.count} occurrences)</span>
              </h3>
              <p className="text-sm text-gray-600 mt-1">Select a reporting category to map this label to:</p>
            </div>
            <button
              onClick={() => {
                setSelectedLabel(null);
                setMediaPreviews([]);
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>

          {/* Category Assignment Buttons */}
          <div className="flex flex-wrap gap-2 mb-6">
            {taxonomy?.reporting_labels.map((label) => (
              <button
                key={label.id}
                onClick={() => addSystemLabel(label.id, selectedLabel.label)}
                className="px-4 py-2 bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
              >
                + {label.label_name}
              </button>
            ))}
          </div>

          {/* Media Previews */}
          {mediaPreviews.length > 0 && (
            <div>
              <h4 className="font-semibold mb-3">Sample Submissions:</h4>
              <div className="grid grid-cols-5 gap-4">
                {mediaPreviews.map((media) => (
                  <div key={media.id} className="border rounded p-2">
                    {media.media_type === 'photo' ? (
                      <img
                        src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(media.media_url)}`)}
                        alt="Preview"
                        className="w-full h-32 object-cover rounded"
                      />
                    ) : (
                      <video
                        src={apiUrl(`/api/media/proxy?gcs_url=${encodeURIComponent(media.media_url)}`)}
                        className="w-full h-32 object-cover rounded"
                      />
                    )}
                    <div className="text-xs text-gray-600 mt-2">
                      <div>{media.respondent_info.region}</div>
                      <div>{media.respondent_info.gender}, {media.respondent_info.age}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
