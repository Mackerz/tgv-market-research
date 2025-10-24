import { useState, useEffect } from 'react';
import { apiUrl } from '@/config/api';
import { ReportSettings, AgeRange } from '@/components/report/types';

/**
 * Custom hook for managing report settings
 * Handles age ranges and question display names
 */
export function useReportSettings(reportSlug: string, activeTab: string) {
  const [settings, setSettings] = useState<ReportSettings | null>(null);
  const [settingsLoading, setSettingsLoading] = useState(false);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [tempAgeRanges, setTempAgeRanges] = useState<AgeRange[]>([]);
  const [tempQuestionDisplayNames, setTempQuestionDisplayNames] = useState<{[key: string]: string}>({});
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      setSettingsLoading(true);
      const response = await fetch(apiUrl(`/api/reports/${reportSlug}/settings`), {
        credentials: 'include'
      });
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }

      const data: ReportSettings = await response.json();
      setSettings(data);

      // Set temporary state for editing
      setTempAgeRanges([...data.age_ranges]);
      const questionDisplayNames: {[key: string]: string} = {};
      data.question_display_names.forEach(q => {
        questionDisplayNames[q.question_id] = q.display_name || '';
      });
      setTempQuestionDisplayNames(questionDisplayNames);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSettingsLoading(false);
    }
  };

  const saveAgeRanges = async () => {
    try {
      setSettingsSaving(true);
      const response = await fetch(apiUrl(`/api/reports/${reportSlug}/settings/age-ranges`), {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tempAgeRanges)
      });

      if (!response.ok) {
        throw new Error('Failed to save age ranges');
      }

      setSettingsSuccess('Age ranges updated successfully');
      setTimeout(() => setSettingsSuccess(null), 3000);
      await fetchSettings(); // Refresh settings
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSettingsSaving(false);
    }
  };

  const saveQuestionDisplayNames = async () => {
    try {
      setSettingsSaving(true);
      const questionUpdates = Object.entries(tempQuestionDisplayNames).map(([questionId, displayName]) => ({
        question_id: questionId,
        display_name: displayName || null
      }));

      const response = await fetch(apiUrl(`/api/reports/${reportSlug}/settings/question-display-names`), {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question_updates: questionUpdates })
      });

      if (!response.ok) {
        throw new Error('Failed to save question display names');
      }

      setSettingsSuccess('Question display names updated successfully');
      setTimeout(() => setSettingsSuccess(null), 3000);
      await fetchSettings(); // Refresh settings
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSettingsSaving(false);
    }
  };

  const addAgeRange = () => {
    const newRange: AgeRange = {
      min: 0,
      max: null,
      label: 'New Range'
    };
    setTempAgeRanges([...tempAgeRanges, newRange]);
  };

  const updateAgeRange = (index: number, field: keyof AgeRange, value: string | number | null) => {
    const updatedRanges = [...tempAgeRanges];
    updatedRanges[index] = { ...updatedRanges[index], [field]: value };
    setTempAgeRanges(updatedRanges);
  };

  const removeAgeRange = (index: number) => {
    const updatedRanges = tempAgeRanges.filter((_, i) => i !== index);
    setTempAgeRanges(updatedRanges);
  };

  const updateQuestionDisplayName = (questionId: string, displayName: string) => {
    setTempQuestionDisplayNames({
      ...tempQuestionDisplayNames,
      [questionId]: displayName
    });
  };

  // Fetch settings when settings tab is active
  useEffect(() => {
    if (activeTab === 'settings') {
      fetchSettings();
    }
  }, [activeTab, reportSlug]);

  return {
    settings,
    settingsLoading,
    settingsSaving,
    tempAgeRanges,
    tempQuestionDisplayNames,
    settingsSuccess,
    error,
    setError,
    fetchSettings,
    saveAgeRanges,
    saveQuestionDisplayNames,
    addAgeRange,
    updateAgeRange,
    removeAgeRange,
    updateQuestionDisplayName,
  };
}
