"use client";

import { useState, useEffect } from "react";
import { logger } from '@/lib/logger';
import FreeTextQuestion from "./questions/FreeTextQuestion";
import SingleChoiceQuestion from "./questions/SingleChoiceQuestion";
import MultipleChoiceQuestion from "./questions/MultipleChoiceQuestion";
import PhotoQuestion from "./questions/PhotoQuestion";
import VideoQuestion from "./questions/VideoQuestion";
import QuestionMedia from "./QuestionMedia";
import QuestionMediaGallery from "./QuestionMediaGallery";
import { apiClient, ApiError } from "@/lib/api";
import type { SurveyQuestion, NextQuestionResponse, QuestionMedia as QuestionMediaType } from "@/types/survey";

interface Survey {
  id: number;
  survey_slug: string;
  name: string;
  survey_flow: SurveyQuestion[];
  is_active: boolean;
}

interface SurveyProgress {
  current_question: number;
  total_questions: number;
  submission_id: number;
  is_completed: boolean;
}

interface QuestionComponentProps {
  survey: Survey;
  submissionId: number;
  progress: SurveyProgress;
  onQuestionComplete: () => void;
  onSurveyComplete: () => void;
  onScreenedOut?: () => void;
}

export default function QuestionComponent({
  survey,
  submissionId,
  progress,
  onQuestionComplete,
  onSurveyComplete,
  onScreenedOut
}: QuestionComponentProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(progress.current_question);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // Get current question
  const currentQuestion = survey.survey_flow[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === survey.survey_flow.length - 1;

  const handleAnswerSubmit = async (answerData: any) => {
    if (!currentQuestion) return;

    setLoading(true);
    setError('');

    try {
      // Submit the response
      await apiClient.post(`/api/submissions/${submissionId}/responses`, {
        question: currentQuestion.question,
        question_type: currentQuestion.question_type,
        ...answerData
      });

      // Check if question has routing rules
      if (currentQuestion.routing_rules && currentQuestion.routing_rules.length > 0) {
        // Use routing logic to determine next question
        // Increase timeout to 60 seconds for video/photo questions that might trigger analysis
        const routingResponse = await apiClient.get<NextQuestionResponse>(
          `/api/submissions/${submissionId}/next-question`,
          {
            params: { current_question_id: currentQuestion.id },
            timeout: 60000 // 60 seconds timeout for routing queries
          }
        );

        if (routingResponse.action === 'end_survey') {
          // Survey ended early due to routing rule (screenout)
          if (onScreenedOut) {
            onScreenedOut();
          }
          onSurveyComplete();
          return;
        }

        // Navigate to the routed question
        if (routingResponse.question_index !== undefined) {
          setCurrentQuestionIndex(routingResponse.question_index);

          // Check if this is the last question after routing
          if (routingResponse.question_index === survey.survey_flow.length - 1) {
            // Still call onQuestionComplete for consistency
            onQuestionComplete();
          } else {
            onQuestionComplete();
          }
        }
      } else {
        // No routing rules - use sequential navigation
        if (isLastQuestion) {
          onSurveyComplete();
        } else {
          setCurrentQuestionIndex(prev => prev + 1);
          onQuestionComplete();
        }
      }
    } catch (error) {
      logger.error('Error submitting answer:', error);
      if (error instanceof ApiError) {
        setError(error.message);
      } else {
        setError(error instanceof Error ? error.message : 'An error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!currentQuestion) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-4">❓</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Question Not Found</h2>
        <p className="text-gray-600">Unable to load the current question.</p>
      </div>
    );
  }

  const renderQuestion = () => {
    const commonProps = {
      question: currentQuestion,
      onSubmit: handleAnswerSubmit,
      loading,
      surveySlug: survey.survey_slug
    };

    switch (currentQuestion.question_type) {
      case 'free_text':
        return <FreeTextQuestion {...commonProps} />;
      case 'single':
        return <SingleChoiceQuestion {...commonProps} />;
      case 'multi':
        return <MultipleChoiceQuestion {...commonProps} />;
      case 'photo':
        return <PhotoQuestion {...commonProps} />;
      case 'video':
        return <VideoQuestion {...commonProps} />;
      default:
        return (
          <div className="text-center text-red-600">
            <p>Unsupported question type: {currentQuestion.question_type}</p>
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6 lg:p-8">
      {/* Progress Header */}
      <div className="mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 space-y-2 sm:space-y-0">
          <span className="text-sm font-medium text-gray-600">
            Question {currentQuestionIndex + 1} of {survey.survey_flow.length}
          </span>
          <span className="text-sm font-medium text-blue-600">
            {Math.round(((currentQuestionIndex + 1) / survey.survey_flow.length) * 100)}% Complete
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / survey.survey_flow.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 leading-tight">
          {currentQuestion.question}
          {currentQuestion.required && <span className="text-red-500 ml-1">*</span>}
        </h2>
        <p className="text-gray-600 text-sm sm:text-base">
          {currentQuestion.required ? 'This question is required.' : 'This question is optional.'}
        </p>
      </div>

      {/* Question Media (Photo or Video) */}
      {currentQuestion.media && currentQuestion.media.length > 0 ? (
        // New array format
        <QuestionMediaGallery
          mediaItems={currentQuestion.media}
          altText={currentQuestion.question}
        />
      ) : currentQuestion.media_url && currentQuestion.media_type ? (
        // Legacy single media format (backward compatibility)
        <QuestionMedia
          mediaUrl={currentQuestion.media_url}
          mediaType={currentQuestion.media_type}
          altText={currentQuestion.question}
        />
      ) : null}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Question Component */}
      {renderQuestion()}

      {/* Navigation Info */}
      <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center text-sm text-gray-500 space-y-2 sm:space-y-0">
          <span className="order-2 sm:order-1">
            {isLastQuestion ? 'This is the final question' : `${survey.survey_flow.length - currentQuestionIndex - 1} questions remaining`}
          </span>
          <span className="order-1 sm:order-2 font-medium">
            Survey: {survey.name}
          </span>
        </div>
      </div>
    </div>
  );
}