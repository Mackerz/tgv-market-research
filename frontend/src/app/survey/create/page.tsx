'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  PlusIcon,
  TrashIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { apiUrl } from '@/config/api';

interface QuestionMedia {
  url: string;
  type: 'photo' | 'video';
  caption?: string;
}

interface RoutingCondition {
  question_id: string;
  operator: string;
  value?: string | string[] | number;
}

interface RoutingRule {
  conditions: RoutingCondition[];
  action: string;
  target_question_id?: string;
}

interface Question {
  id: string;
  question: string;
  question_type: string;
  required: boolean;
  options?: string[];
  routing_rules?: RoutingRule[];
  media?: QuestionMedia[];
}

const questionTypes = [
  { value: 'single', label: 'Single Choice' },
  { value: 'multi', label: 'Multiple Choice' },
  { value: 'free_text', label: 'Free Text' },
  { value: 'photo', label: 'Photo Upload' },
  { value: 'video', label: 'Video Upload' }
];

const operators = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Not Contains' },
  { value: 'contains_any', label: 'Contains Any' },
  { value: 'contains_all', label: 'Contains All' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
  { value: 'is_answered', label: 'Is Answered' },
  { value: 'is_not_answered', label: 'Is Not Answered' }
];

const routingActions = [
  { value: 'continue', label: 'Continue to Next Question' },
  { value: 'goto_question', label: 'Go to Specific Question' },
  { value: 'end_survey', label: 'End Survey' }
];

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
          const response = await fetch(apiUrl(`/api/surveys/slug/${editSlug}`));

          if (!response.ok) {
            throw new Error('Failed to fetch survey');
          }

          const surveyData = await response.json();

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
          console.error('Error fetching survey:', err);
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
      const response = await fetch(apiUrl(`/api/surveys/slug/${surveySlug}`));

      if (!response.ok) {
        throw new Error('Failed to fetch survey details');
      }

      const surveyData = await response.json();

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
      console.error('Error exporting survey:', err);
      alert('Failed to export survey. Please try again.');
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

      // Determine API endpoint and method based on mode
      const apiEndpoint = isEditMode ? apiUrl(`/api/surveys/${surveyId}`) : apiUrl('/api/surveys/');
      const httpMethod = isEditMode ? 'PUT' : 'POST';

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

      const response = await fetch(apiEndpoint, {
        method: httpMethod,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Survey creation error:', errorData);
        console.error('Request payload:', JSON.stringify({
          survey_slug: surveySlug,
          name: surveyName,
          ...(client && client.trim() !== '' ? { client } : {}),
          is_active: isActive,
          survey_flow: cleanedQuestions
        }, null, 2));

        // Format validation errors if present
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map((err: any) => {
            const location = err.loc ? err.loc.join(' -> ') : 'Unknown';
            const input = err.input ? `\nInput: ${JSON.stringify(err.input)}` : '';
            return `${location}: ${err.msg}${input}`;
          }).join('\n\n');
          throw new Error(`Validation errors:\n${errorMessages}`);
        }

        throw new Error(errorData.detail || 'Failed to create survey');
      }

      const data = await response.json();
      alert(isEditMode ? 'Survey updated successfully!' : 'Survey created successfully!');
      router.push(`/report/${data.survey_slug}`);
    } catch (err) {
      console.error('Error creating survey:', err);
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
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-700">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 inline-block mr-3"></div>
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
                  onChange={(e) => setSurveySlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'))}
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
                  onChange={(e) => setSurveyName(e.target.value)}
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
                  onChange={(e) => setClient(e.target.value)}
                  placeholder="Client name"
                  className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
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
                  onChange={(e) => setCompleteRedirectUrl(e.target.value)}
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
                  onChange={(e) => setScreenoutRedirectUrl(e.target.value)}
                  placeholder="https://partner.com/screenout"
                  className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
                />
                <p className="text-xs text-gray-500 mt-1">Redirect URL when survey is screened out (early termination)</p>
              </div>
            </div>
          </div>

          {/* Questions */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Questions</h2>
              <button
                type="button"
                onClick={addQuestion}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
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
            <div>
              {isEditMode && (
                <button
                  type="button"
                  onClick={handleExportSurvey}
                  className="px-6 py-3 border border-purple-300 rounded-md text-purple-700 hover:bg-purple-50 font-medium"
                  title="Export survey metadata as JSON"
                >
                  Export JSON
                </button>
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

// Question Builder Component
interface QuestionBuilderProps {
  question: Question;
  index: number;
  total: number;
  expanded: boolean;
  onToggleExpand: () => void;
  onUpdate: (updates: Partial<Question>) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onAddOption: () => void;
  onUpdateOption: (optionIndex: number, value: string) => void;
  onRemoveOption: (optionIndex: number) => void;
  onAddRoutingRule: () => void;
  onUpdateRoutingRule: (ruleIndex: number, updates: Partial<RoutingRule>) => void;
  onRemoveRoutingRule: (ruleIndex: number) => void;
  onAddMedia: () => void;
  onUpdateMedia: (mediaIndex: number, updates: Partial<QuestionMedia>) => void;
  onRemoveMedia: (mediaIndex: number) => void;
  allQuestions: Question[];
}

function QuestionBuilder({
  question,
  index,
  total,
  expanded,
  onToggleExpand,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  onAddOption,
  onUpdateOption,
  onRemoveOption,
  onAddRoutingRule,
  onUpdateRoutingRule,
  onRemoveRoutingRule,
  onAddMedia,
  onUpdateMedia,
  onRemoveMedia,
  allQuestions
}: QuestionBuilderProps) {
  const needsOptions = question.question_type === 'single' || question.question_type === 'multi';

  return (
    <div className="border rounded-lg">
      {/* Question Header */}
      <div className="p-4 bg-gray-50 flex justify-between items-center border-b">
        <div className="flex items-center space-x-3 flex-1">
          <button
            type="button"
            onClick={onToggleExpand}
            className="text-gray-600 hover:text-gray-900"
          >
            {expanded ? (
              <ChevronDownIcon className="h-5 w-5" />
            ) : (
              <ChevronRightIcon className="h-5 w-5" />
            )}
          </button>
          <span className="font-medium text-gray-900">
            Question {index + 1}: {question.question || '(Untitled)'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {index > 0 && (
            <button
              type="button"
              onClick={onMoveUp}
              className="p-1 text-gray-600 hover:text-gray-900"
              title="Move up"
            >
              <ArrowUpIcon className="h-5 w-5" />
            </button>
          )}
          {index < total - 1 && (
            <button
              type="button"
              onClick={onMoveDown}
              className="p-1 text-gray-600 hover:text-gray-900"
              title="Move down"
            >
              <ArrowDownIcon className="h-5 w-5" />
            </button>
          )}
          <button
            type="button"
            onClick={onRemove}
            className="p-1 text-red-600 hover:text-red-900"
            title="Remove question"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Question Body */}
      {expanded && (
        <div className="p-4 space-y-4">
          {/* Question ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Question ID
            </label>
            <input
              type="text"
              value={question.id}
              onChange={(e) => onUpdate({ id: e.target.value.replace(/[^a-z0-9_]/g, '_') })}
              className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white"
            />
            <p className="text-xs text-gray-500 mt-1">Unique identifier (lowercase, underscores only)</p>
          </div>

          {/* Question Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Question Text *
            </label>
            <textarea
              value={question.question}
              onChange={(e) => onUpdate({ question: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
              placeholder="Enter your question here"
            />
          </div>

          {/* Question Type and Required */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Question Type
              </label>
              <select
                value={question.question_type}
                onChange={(e) => onUpdate({ question_type: e.target.value })}
                className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white"
              >
                {questionTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={question.required}
                  onChange={(e) => onUpdate({ required: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <span className="text-sm font-medium text-gray-700">Required</span>
              </label>
            </div>
          </div>

          {/* Options (for single/multi choice) */}
          {needsOptions && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Answer Options
                </label>
                <button
                  type="button"
                  onClick={onAddOption}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  + Add Option
                </button>
              </div>
              <div className="space-y-2">
                {question.options?.map((option, optIndex) => (
                  <div key={optIndex} className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={option}
                      onChange={(e) => onUpdateOption(optIndex, e.target.value)}
                      placeholder={`Option ${optIndex + 1}`}
                      className="flex-1 px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
                    />
                    <button
                      type="button"
                      onClick={() => onRemoveOption(optIndex)}
                      className="p-2 text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Media Section */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Media (Optional)
              </label>
              <button
                type="button"
                onClick={onAddMedia}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                + Add Media
              </button>
            </div>
            {question.media && question.media.length > 0 && (
              <div className="space-y-3">
                {question.media.map((media, mediaIndex) => (
                  <div key={mediaIndex} className="border rounded-md p-3 space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="text-sm font-medium text-gray-700">Media {mediaIndex + 1}</span>
                      <button
                        type="button"
                        onClick={() => onRemoveMedia(mediaIndex)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Media Type</label>
                        <select
                          value={media.type}
                          onChange={(e) => onUpdateMedia(mediaIndex, { type: e.target.value as 'photo' | 'video' })}
                          className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                        >
                          <option value="photo">Photo</option>
                          <option value="video">Video</option>
                        </select>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Media URL (GCS URL)</label>
                      <input
                        type="url"
                        value={media.url}
                        onChange={(e) => onUpdateMedia(mediaIndex, { url: e.target.value })}
                        placeholder="https://storage.googleapis.com/..."
                        className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Caption (Optional)</label>
                      <input
                        type="text"
                        value={media.caption || ''}
                        onChange={(e) => onUpdateMedia(mediaIndex, { caption: e.target.value })}
                        placeholder="Media caption"
                        className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Routing Rules Section */}
          <div>
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700">
                  Routing Rules (Optional)
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  Multiple rules are evaluated in order (OR logic). First matching rule wins.
                </p>
              </div>
              <button
                type="button"
                onClick={onAddRoutingRule}
                className="text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap"
              >
                + Add Routing Rule
              </button>
            </div>
            {question.routing_rules && question.routing_rules.length > 0 && (
              <div className="space-y-3">
                {question.routing_rules.map((rule, ruleIndex) => (
                  <div key={ruleIndex} className="border rounded-md p-3 bg-gray-50 space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="text-sm font-medium text-gray-700">Rule {ruleIndex + 1}</span>
                      <button
                        type="button"
                        onClick={() => onRemoveRoutingRule(ruleIndex)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Condition */}
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Operator</label>
                        <select
                          value={rule.conditions[0]?.operator || 'equals'}
                          onChange={(e) => {
                            const newConditions = [...rule.conditions];
                            newConditions[0] = {
                              question_id: newConditions[0]?.question_id || question.id,
                              operator: e.target.value,
                              value: newConditions[0]?.value
                            };
                            onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                          }}
                          className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                        >
                          {operators.map(op => (
                            <option key={op.value} value={op.value}>{op.label}</option>
                          ))}
                        </select>
                      </div>
                      <div className="col-span-2">
                        <label className="block text-xs text-gray-600 mb-1">Value</label>
                        {needsOptions ? (
                          <select
                            value={rule.conditions[0]?.value as string || ''}
                            onChange={(e) => {
                              const newConditions = [...rule.conditions];
                              newConditions[0] = {
                                question_id: newConditions[0]?.question_id || question.id,
                                operator: newConditions[0]?.operator || 'equals',
                                value: e.target.value
                              };
                              onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                            }}
                            className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                          >
                            <option value="">Select an option</option>
                            {question.options?.map((opt, i) => (
                              <option key={i} value={opt}>{opt}</option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="text"
                            value={rule.conditions[0]?.value as string || ''}
                            onChange={(e) => {
                              const newConditions = [...rule.conditions];
                              newConditions[0] = {
                                question_id: newConditions[0]?.question_id || question.id,
                                operator: newConditions[0]?.operator || 'equals',
                                value: e.target.value
                              };
                              onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                            }}
                            placeholder="Condition value"
                            className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                          />
                        )}
                      </div>
                    </div>

                    {/* Action */}
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">Action</label>
                      <select
                        value={rule.action}
                        onChange={(e) => onUpdateRoutingRule(ruleIndex, { action: e.target.value })}
                        className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                      >
                        {routingActions.map(action => (
                          <option key={action.value} value={action.value}>{action.label}</option>
                        ))}
                      </select>
                    </div>

                    {/* Target Question (if goto_question) */}
                    {rule.action === 'goto_question' && (
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Target Question</label>
                        <select
                          value={rule.target_question_id || ''}
                          onChange={(e) => onUpdateRoutingRule(ruleIndex, { target_question_id: e.target.value })}
                          className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                        >
                          <option value="">Select a question</option>
                          {allQuestions.map((q, i) => (
                            <option key={i} value={q.id}>
                              {q.id} - {q.question || '(Untitled)'}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function CreateSurveyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <CreateSurveyForm />
    </Suspense>
  );
}
