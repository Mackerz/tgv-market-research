import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
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
      const data = await apiClient.get<ReportSettings>(
        `/api/reports/${reportSlug}/settings`
      );
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
      await apiClient.put(
        `/api/reports/${reportSlug}/settings/age-ranges`,
        tempAgeRanges
      );

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

      await apiClient.put(
        `/api/reports/${reportSlug}/settings/question-display-names`,
        { question_updates: questionUpdates }
      );

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
