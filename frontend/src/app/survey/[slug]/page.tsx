"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import PersonalInfoForm from "@/components/survey/PersonalInfoForm";
import QuestionComponent from "@/components/survey/QuestionComponent";
import SurveyComplete from "@/components/survey/SurveyComplete";

interface Survey {
  id: number;
  survey_slug: string;
  name: string;
  survey_flow: SurveyQuestion[];
  is_active: boolean;
}

interface SurveyQuestion {
  id: string;
  question: string;
  question_type: 'free_text' | 'single' | 'multi' | 'photo' | 'video';
  required: boolean;
  options?: string[];
}

interface SurveyProgress {
  current_question: number;
  total_questions: number;
  submission_id: number;
  is_completed: boolean;
}

export default function SurveyPage() {
  const params = useParams();
  const router = useRouter();
  const surveySlug = params.slug as string;

  const [survey, setSurvey] = useState<Survey | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submissionId, setSubmissionId] = useState<number | null>(null);
  const [currentStep, setCurrentStep] = useState<'personal-info' | 'questions' | 'complete'>('personal-info');
  const [progress, setProgress] = useState<SurveyProgress | null>(null);

  useEffect(() => {
    if (surveySlug) {
      fetchSurvey();
    }
  }, [surveySlug]);

  const fetchSurvey = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/surveys/slug/${surveySlug}`);
      if (!response.ok) {
        throw new Error('Survey not found');
      }
      const data = await response.json();
      setSurvey(data);
      setLoading(false);
    } catch (error) {
      setError('Survey not found or is not available');
      setLoading(false);
    }
  };

  const fetchProgress = async (submissionId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/submissions/${submissionId}/progress`);
      if (response.ok) {
        const data = await response.json();
        setProgress(data);

        if (data.is_completed) {
          setCurrentStep('complete');
        } else {
          // If we have a submission ID, we've completed personal info
          // Move to questions regardless of current_question count
          setCurrentStep('questions');
        }
      }
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  };

  const handlePersonalInfoComplete = (submissionId: number) => {
    console.log('handlePersonalInfoComplete called with ID:', submissionId);
    console.log('Survey object:', survey);
    setSubmissionId(submissionId);
    setCurrentStep('questions');
    // Set initial progress data
    if (survey) {
      const progressData = {
        current_question: 0,
        total_questions: survey.survey_flow.length,
        submission_id: submissionId,
        is_completed: false
      };
      console.log('Setting progress to:', progressData);
      setProgress(progressData);
    } else {
      console.log('Survey is null, cannot set progress');
    }
  };

  const handleQuestionComplete = () => {
    if (submissionId) {
      fetchProgress(submissionId);
    }
  };

  const handleSurveyComplete = async () => {
    if (submissionId) {
      try {
        await fetch(`http://localhost:8000/api/submissions/${submissionId}/complete`, {
          method: 'PUT',
        });
        setCurrentStep('complete');
      } catch (error) {
        console.error('Failed to complete survey:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading survey...</p>
        </div>
      </div>
    );
  }

  if (error || !survey) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Survey Not Found</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  if (!survey.is_active) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⏸️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Survey Unavailable</h1>
          <p className="text-gray-600 mb-4">This survey is currently not accepting responses.</p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{survey.name}</h1>
          {progress && (
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(progress.current_question / progress.total_questions) * 100}%` }}
              ></div>
            </div>
          )}
        </div>

        {/* Debug Info */}
        <div className="mb-4 p-2 bg-gray-100 text-xs">
          Debug: Step={currentStep}, SubmissionID={submissionId}, Progress={progress?.current_question}/{progress?.total_questions}
          <br />Survey: {survey ? 'loaded' : 'null'}, Progress obj: {progress ? JSON.stringify(progress) : 'null'}
        </div>

        {/* Survey Steps */}
        {currentStep === 'personal-info' && (
          <PersonalInfoForm
            surveySlug={surveySlug}
            onComplete={handlePersonalInfoComplete}
          />
        )}

        {currentStep === 'questions' && survey && progress && submissionId && (
          <QuestionComponent
            survey={survey}
            submissionId={submissionId}
            progress={progress}
            onQuestionComplete={handleQuestionComplete}
            onSurveyComplete={handleSurveyComplete}
          />
        )}

        {currentStep === 'complete' && (
          <SurveyComplete surveyName={survey.name} />
        )}
      </div>
    </div>
  );
}