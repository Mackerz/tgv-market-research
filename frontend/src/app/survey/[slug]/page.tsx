"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import PersonalInfoForm from "@/components/survey/PersonalInfoForm";
import QuestionComponent from "@/components/survey/QuestionComponent";
import SurveyComplete from "@/components/survey/SurveyComplete";
import { LoadingState, ErrorState, EmptyState } from "@/components/common";
import { useSurvey } from "@/hooks";
import type { Survey, SurveyProgress } from "@/types";

type SurveyStep = 'personal-info' | 'questions' | 'complete';

export default function SurveyPage() {
  const params = useParams();
  const router = useRouter();
  const surveySlug = params.slug as string;

  const [currentStep, setCurrentStep] = useState<SurveyStep>('personal-info');

  // Use the new useSurvey hook
  const {
    survey,
    submission,
    progress,
    loading,
    error,
    startSurvey,
    refetchProgress,
    completeAndSubmit,
  } = useSurvey({
    surveySlug,
    onComplete: () => setCurrentStep('complete'),
  });

  const handlePersonalInfoComplete = async (email: string, region: string, age?: number) => {
    try {
      await startSurvey(email, region, age);
      setCurrentStep('questions');
    } catch (err) {
      console.error('Failed to start survey:', err);
    }
  };

  const handleQuestionComplete = async () => {
    await refetchProgress();
  };

  const handleSurveyComplete = async () => {
    try {
      await completeAndSubmit();
    } catch (err) {
      console.error('Failed to complete survey:', err);
    }
  };

  // Loading state
  if (loading) {
    return <LoadingState message="Loading survey..." />;
  }

  // Error state
  if (error || !survey) {
    return (
      <ErrorState
        title="Survey Not Found"
        message={error || 'This survey does not exist or is not available'}
        showHomeButton={true}
      />
    );
  }

  // Inactive survey
  if (!survey.is_active) {
    return (
      <EmptyState
        icon="⏸️"
        title="Survey Unavailable"
        message="This survey is currently not accepting responses."
        action={{
          label: 'Go Home',
          onClick: () => router.push('/'),
        }}
        fullScreen={true}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8 max-w-2xl">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2 leading-tight">
            {survey.name}
          </h1>
          {progress && (
            <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{
                  width: `${(progress.current_question / progress.total_questions) * 100}%`,
                }}
              ></div>
            </div>
          )}
        </div>

        {/* Survey Steps */}
        {currentStep === 'personal-info' && (
          <PersonalInfoForm
            surveySlug={surveySlug}
            onComplete={(submissionId) => {
              // The useSurvey hook handles submission creation
              // We just need to move to the next step
              setCurrentStep('questions');
            }}
          />
        )}

        {currentStep === 'questions' && survey && progress && submission && (
          <QuestionComponent
            survey={survey}
            submissionId={submission.id}
            progress={progress}
            onQuestionComplete={handleQuestionComplete}
            onSurveyComplete={handleSurveyComplete}
          />
        )}

        {currentStep === 'complete' && <SurveyComplete surveyName={survey.name} />}
      </div>
    </div>
  );
}
