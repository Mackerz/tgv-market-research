'use client';

import { useState, useEffect, Suspense } from 'react';
import { logger } from '@/lib/logger';
import { useRouter, useSearchParams } from 'next/navigation';
import { PlusIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import { surveyService } from '@/lib/api';
import { Question, QuestionMedia, RoutingRule } from '@/components/survey-create/types';
import QuestionBuilder from '@/components/survey-create/QuestionBuilder';
import SurveyDetailsForm from '@/components/survey-create/SurveyDetailsForm';

function CreateSurveyForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const editSlug = searchParams.get('edit'); // Get the survey slug to edit
  const isEditMode = !!editSlug;

  const [surveyId, setSurveyId] = useState<number | null>(null);
  const [surveySlug, setSurveySlug] = useState('');
  const [surveyName, setSurveyName] = useState('');
  const [client, setClient] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [completeRedirectUrl, setCompleteRedirectUrl] = useState('');
  const [screenoutRedirectUrl, setScreenoutRedirectUrl] = useState('');
  const [questions, setQuestions] = useState<Question[]>([]);
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch survey data when in edit mode
  useEffect(() => {
    if (isEditMode && editSlug) {
      const fetchSurvey = async () => {
        try {
          setLoading(true);
          const surveyData = await surveyService.getSurveyBySlug(editSlug);

          // Pre-fill form fields
          setSurveyId(surveyData.id);
          setSurveySlug(surveyData.survey_slug);
          setSurveyName(surveyData.name);
          setClient(surveyData.client || '');
          setIsActive(surveyData.is_active);
          setCompleteRedirectUrl(surveyData.complete_redirect_url || '');
          setScreenoutRedirectUrl(surveyData.screenout_redirect_url || '');
          setQuestions(surveyData.survey_flow || []);
        } catch (err) {
          logger.error('Error fetching survey:', err);
          setError(err instanceof Error ? err.message : 'Failed to load survey');
        } finally {
          setLoading(false);
        }
      };

      fetchSurvey();
    }
  }, [isEditMode, editSlug]);

  const addQuestion = () => {
    const newQuestion: Question = {
      id: `q${Date.now()}`,
      question: '',
      question_type: 'single',
      required: true,
      options: [''],
      routing_rules: [],
      media: []
    };
    setQuestions([...questions, newQuestion]);
    setExpandedQuestion(questions.length);
  };

  const removeQuestion = (index: number) => {
    if (confirm('Are you sure you want to remove this question?')) {
      setQuestions(questions.filter((_, i) => i !== index));
      if (expandedQuestion === index) {
        setExpandedQuestion(null);
      }
    }
  };

  const moveQuestion = (index: number, direction: 'up' | 'down') => {
    const newQuestions = [...questions];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    [newQuestions[index], newQuestions[newIndex]] = [newQuestions[newIndex], newQuestions[index]];
    setQuestions(newQuestions);
  };

  const updateQuestion = (index: number, updates: Partial<Question>) => {
    const newQuestions = [...questions];
    newQuestions[index] = { ...newQuestions[index], ...updates };
    setQuestions(newQuestions);
  };

  const addOption = (questionIndex: number) => {
    const newQuestions = [...questions];
    if (!newQuestions[questionIndex].options) {
      newQuestions[questionIndex].options = [];
    }
    newQuestions[questionIndex].options!.push('');
    setQuestions(newQuestions);
  };

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].options![optionIndex] = value;
    setQuestions(newQuestions);
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].options!.splice(optionIndex, 1);
    setQuestions(newQuestions);
  };

  const addRoutingRule = (questionIndex: number) => {
    const newQuestions = [...questions];
    if (!newQuestions[questionIndex].routing_rules) {
      newQuestions[questionIndex].routing_rules = [];
    }
    newQuestions[questionIndex].routing_rules!.push({
      conditions: [{
        question_id: newQuestions[questionIndex].id,
        operator: 'equals',
        value: undefined // Don't set a value initially - let it be undefined or set properly
      }],
      action: 'continue',
      target_question_id: undefined // Make sure it's undefined for non-goto actions
    });
    setQuestions(newQuestions);
  };

  const updateRoutingRule = (questionIndex: number, ruleIndex: number, updates: Partial<RoutingRule>) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].routing_rules![ruleIndex] = {
      ...newQuestions[questionIndex].routing_rules![ruleIndex],
      ...updates
    };
    setQuestions(newQuestions);
  };

  const removeRoutingRule = (questionIndex: number, ruleIndex: number) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].routing_rules!.splice(ruleIndex, 1);
    setQuestions(newQuestions);
  };

  const addMedia = (questionIndex: number) => {
    const newQuestions = [...questions];
    if (!newQuestions[questionIndex].media) {
      newQuestions[questionIndex].media = [];
    }
    newQuestions[questionIndex].media!.push({
      url: '',
      type: 'photo',
      caption: ''
    });
    setQuestions(newQuestions);
  };

  const updateMedia = (questionIndex: number, mediaIndex: number, updates: Partial<QuestionMedia>) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].media![mediaIndex] = {
      ...newQuestions[questionIndex].media![mediaIndex],
      ...updates
    };
    setQuestions(newQuestions);
  };

  const removeMedia = (questionIndex: number, mediaIndex: number) => {
    const newQuestions = [...questions];
    newQuestions[questionIndex].media!.splice(mediaIndex, 1);
    setQuestions(newQuestions);
  };

  const handleExportSurvey = async () => {
    if (!surveySlug) {
      alert('Please save the survey first before exporting');
      return;
    }

    try {
      // Fetch the full survey details including survey_flow using the slug endpoint
      const surveyData = await surveyService.getSurveyBySlug(surveySlug);

      // Create a formatted JSON with proper indentation
      const jsonString = JSON.stringify(surveyData, null, 2);

      // Create a blob and download it
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${surveySlug}-metadata.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      logger.error('Error exporting survey:', err);
      alert('Failed to export survey. Please try again.');
    }
  };

  const handleCopySurvey = async () => {
    if (!surveyId) {
      alert('Please save the survey first before copying');
      return;
    }

    if (!confirm('Create a copy of this survey? The copy will have a new slug and "(Copy)" appended to the name.')) {
      return;
    }

    try {
      setSaving(true);
      const copiedSurvey = await surveyService.copySurvey(surveyId);
      alert(`Survey copied successfully! Redirecting to edit the copy...`);
      // Navigate to edit the copied survey
      router.push(`/survey/create?edit=${copiedSurvey.survey_slug}`);
    } catch (err) {
      logger.error('Error copying survey:', err);
      alert('Failed to copy survey. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!surveySlug.trim()) {
      setError('Survey slug is required');
      return;
    }
    if (!surveyName.trim()) {
      setError('Survey name is required');
      return;
    }
    if (questions.length === 0) {
      setError('At least one question is required');
      return;
    }

    // Validate each question
    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      if (!q.question.trim()) {
        setError(`Question ${i + 1}: Question text is required`);
        return;
      }
      if ((q.question_type === 'single' || q.question_type === 'multi') && (!q.options || q.options.length === 0)) {
        setError(`Question ${i + 1}: At least one option is required for choice questions`);
        return;
      }
    }

    setSaving(true);

    try {
      // Clean up the survey data before sending
      const cleanedQuestions = questions.map((q, qIndex) => {
        const cleaned: any = {
          id: q.id,
          question: q.question,
          question_type: q.question_type,
          required: q.required
        };

        // Add options only if it's a choice question and has valid options
        if ((q.question_type === 'single' || q.question_type === 'multi') && q.options) {
          const validOptions = q.options.filter(o => o.trim() !== '');
          if (validOptions.length > 0) {
            cleaned.options = validOptions;
          }
        }

        // Add routing rules only if they exist and are valid
        if (q.routing_rules && q.routing_rules.length > 0) {
          const validRules = q.routing_rules.filter(r => {
            // Rule must have at least one condition
            if (!r.conditions || r.conditions.length === 0) return false;
            // Rule must have valid conditions
            const validCondition = r.conditions[0];
            if (!validCondition.question_id || !validCondition.operator) return false;
            // For operators that need a value, make sure value is provided
            const operatorsNeedingValue = ['equals', 'not_equals', 'contains', 'not_contains', 'contains_any', 'contains_all', 'greater_than', 'less_than'];
            if (operatorsNeedingValue.includes(validCondition.operator) && (validCondition.value === undefined || validCondition.value === '')) {
              return false;
            }
            // If goto_question, must have target
            if (r.action === 'goto_question' && !r.target_question_id) return false;
            return true;
          });

          if (validRules.length > 0) {
            cleaned.routing_rules = validRules.map(r => {
              const cleanedRule: any = {
                conditions: r.conditions,
                action: r.action
              };
              // Only add target_question_id if action is goto_question
              if (r.action === 'goto_question' && r.target_question_id) {
                cleanedRule.target_question_id = r.target_question_id;
              }
              return cleanedRule;
            });
          }
        }

        // Add media only if it exists and has valid URLs
        if (q.media && q.media.length > 0) {
          const validMedia = q.media.filter(m => m.url && m.url.trim() !== '');
          if (validMedia.length > 0) {
            cleaned.media = validMedia.map(m => ({
              url: m.url,
              type: m.type,
              ...(m.caption && m.caption.trim() !== '' ? { caption: m.caption } : {})
            }));
          }
        }

        return cleaned;
      });

      const requestBody: any = {
        name: surveyName,
        ...(client && client.trim() !== '' ? { client } : {}),
        is_active: isActive,
        survey_flow: cleanedQuestions,
        ...(completeRedirectUrl && completeRedirectUrl.trim() !== '' ? { complete_redirect_url: completeRedirectUrl } : {}),
        ...(screenoutRedirectUrl && screenoutRedirectUrl.trim() !== '' ? { screenout_redirect_url: screenoutRedirectUrl } : {})
      };

      // Only include survey_slug for POST (create)
      if (!isEditMode) {
        requestBody.survey_slug = surveySlug;
      }

      const data = isEditMode && surveyId
        ? await surveyService.updateSurvey(surveyId, requestBody)
        : await surveyService.createSurvey(requestBody);
      alert(isEditMode ? 'Survey updated successfully!' : 'Survey created successfully!');
      router.push(`/report/${data.survey_slug}`);
    } catch (err) {
      logger.error('Error creating survey:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {isEditMode ? 'Edit Survey' : 'Create New Survey'}
          </h1>
          <p className="text-gray-600">
            {isEditMode ? 'Update your survey configuration' : 'Design a survey with questions, routing, and media'}
          </p>
        </div>

        {loading && (
          <div className="mb-6 bg-[#F5E8F0] border border-[#F5E8F0] rounded-lg p-4 text-[#B0156E]">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#D01A8A] inline-block mr-3"></div>
            Loading survey data...
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <div className="font-semibold mb-2">{isEditMode ? 'Error Loading Survey' : 'Error Creating Survey'}</div>
            <pre className="text-sm whitespace-pre-wrap font-mono">{error}</pre>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Survey Details */}
          <SurveyDetailsForm
            surveySlug={surveySlug}
            surveyName={surveyName}
            client={client}
            isActive={isActive}
            completeRedirectUrl={completeRedirectUrl}
            screenoutRedirectUrl={screenoutRedirectUrl}
            isEditMode={isEditMode}
            onSurveySlugChange={setSurveySlug}
            onSurveyNameChange={setSurveyName}
            onClientChange={setClient}
            onIsActiveChange={setIsActive}
            onCompleteRedirectUrlChange={setCompleteRedirectUrl}
            onScreenoutRedirectUrlChange={setScreenoutRedirectUrl}
          />

          {/* Questions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Questions</h2>
              <button
                type="button"
                onClick={addQuestion}
                className="flex items-center space-x-2 px-4 py-2 bg-[#D01A8A] text-white rounded-md hover:bg-[#B0156E]"
              >
                <PlusIcon className="h-5 w-5" />
                <span>Add Question</span>
              </button>
            </div>

            {questions.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                No questions yet. Click "Add Question" to get started.
              </div>
            )}

            <div className="space-y-4">
              {questions.map((question, qIndex) => (
                <QuestionBuilder
                  key={qIndex}
                  question={question}
                  index={qIndex}
                  total={questions.length}
                  expanded={expandedQuestion === qIndex}
                  onToggleExpand={() => setExpandedQuestion(expandedQuestion === qIndex ? null : qIndex)}
                  onUpdate={(updates) => updateQuestion(qIndex, updates)}
                  onRemove={() => removeQuestion(qIndex)}
                  onMoveUp={() => moveQuestion(qIndex, 'up')}
                  onMoveDown={() => moveQuestion(qIndex, 'down')}
                  onAddOption={() => addOption(qIndex)}
                  onUpdateOption={(optIndex, value) => updateOption(qIndex, optIndex, value)}
                  onRemoveOption={(optIndex) => removeOption(qIndex, optIndex)}
                  onAddRoutingRule={() => addRoutingRule(qIndex)}
                  onUpdateRoutingRule={(ruleIndex, updates) => updateRoutingRule(qIndex, ruleIndex, updates)}
                  onRemoveRoutingRule={(ruleIndex) => removeRoutingRule(qIndex, ruleIndex)}
                  onAddMedia={() => addMedia(qIndex)}
                  onUpdateMedia={(mediaIndex, updates) => updateMedia(qIndex, mediaIndex, updates)}
                  onRemoveMedia={(mediaIndex) => removeMedia(qIndex, mediaIndex)}
                  allQuestions={questions}
                />
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-between items-center">
            <div className="flex space-x-4">
              {isEditMode && (
                <>
                  <button
                    type="button"
                    onClick={handleCopySurvey}
                    disabled={saving || loading}
                    className="flex items-center space-x-2 px-6 py-3 border border-[#D01A8A] rounded-md text-[#D01A8A] hover:bg-[#F5E8F0] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Create a copy of this survey with a new slug and name"
                  >
                    <DocumentDuplicateIcon className="h-5 w-5" />
                    <span>Copy Survey</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleExportSurvey}
                    className="px-6 py-3 border border-purple-300 rounded-md text-purple-700 hover:bg-purple-50 font-medium"
                    title="Export survey metadata as JSON"
                  >
                    Export JSON
                  </button>
                </>
              )}
            </div>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving || loading}
                className={`px-6 py-3 rounded-md text-white font-medium ${
                  saving || loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {saving ? (isEditMode ? 'Updating...' : 'Creating...') : (isEditMode ? 'Update Survey' : 'Create Survey')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function CreateSurveyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#D01A8A] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <CreateSurveyForm />
    </Suspense>
  );
}
