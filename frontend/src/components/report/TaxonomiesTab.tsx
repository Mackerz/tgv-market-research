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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TaxonomiesTabProps {
  surveyId: number;
}

export default function TaxonomiesTab({ surveyId }: TaxonomiesTabProps) {
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

  useEffect(() => {
    fetchTaxonomy();
  }, [surveyId]);

  const fetchTaxonomy = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/surveys/${surveyId}/taxonomy`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setTaxonomy(data);
      }
    } catch (error) {
      console.error('Error fetching taxonomy:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateTaxonomy = async () => {
    try {
      setGenerating(true);
      const response = await fetch(`${API_URL}/api/surveys/${surveyId}/taxonomy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ survey_id: surveyId, max_categories: 6 }),
      });
      if (response.ok) {
        await fetchTaxonomy();
      }
    } catch (error) {
      console.error('Error generating taxonomy:', error);
    } finally {
      setGenerating(false);
    }
  };

  const fetchMediaPreviews = async (systemLabel: string) => {
    try {
      const response = await fetch(
        `${API_URL}/api/surveys/${surveyId}/system-labels/${encodeURIComponent(systemLabel)}/media?limit=5`,
        { credentials: 'include' }
      );
      if (response.ok) {
        const data = await response.json();
        setMediaPreviews(data);
      }
    } catch (error) {
      console.error('Error fetching media previews:', error);
    }
  };

  const addSystemLabel = async (reportingLabelId: number, systemLabel: string) => {
    try {
      const response = await fetch(`${API_URL}/api/reporting-labels/${reportingLabelId}/system-labels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ system_label: systemLabel }),
      });
      if (response.ok) {
        await fetchTaxonomy();
        setSelectedLabel(null);
        setMediaPreviews([]);
      }
    } catch (error) {
      console.error('Error adding system label:', error);
    }
  };

  const removeSystemLabel = async (reportingLabelId: number, systemLabel: string) => {
    try {
      const response = await fetch(`${API_URL}/api/reporting-labels/${reportingLabelId}/system-labels`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ system_label: systemLabel }),
      });
      if (response.ok) {
        await fetchTaxonomy();
      }
    } catch (error) {
      console.error('Error removing system label:', error);
    }
  };

  const updateReportingLabel = async (labelId: number) => {
    try {
      const updateData: ReportingLabelUpdate = {
        label_name: editName,
        description: editDescription || undefined,
      };
      const response = await fetch(`${API_URL}/api/reporting-labels/${labelId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(updateData),
      });
      if (response.ok) {
        await fetchTaxonomy();
        setEditingLabel(null);
      }
    } catch (error) {
      console.error('Error updating label:', error);
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
      const response = await fetch(`${API_URL}/api/reporting-labels`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(createData),
      });
      if (response.ok) {
        await fetchTaxonomy();
        setCreatingNew(false);
        setNewLabelName('');
        setNewLabelDescription('');
      }
    } catch (error) {
      console.error('Error creating label:', error);
    }
  };

  const deleteReportingLabel = async (labelId: number) => {
    if (!confirm('Delete this reporting label? This is only possible if no system labels are mapped to it.')) {
      return;
    }
    try {
      const response = await fetch(`${API_URL}/api/reporting-labels/${labelId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (response.ok) {
        await fetchTaxonomy();
      } else {
        alert('Cannot delete label. Remove all system label mappings first.');
      }
    } catch (error) {
      console.error('Error deleting label:', error);
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
                      <img src={media.media_url} alt="Preview" className="w-full h-32 object-cover rounded" />
                    ) : (
                      <video src={media.media_url} className="w-full h-32 object-cover rounded" />
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
