/**
 * useSurvey Hook
 * Manages survey state, navigation, and submission
 */

import { useState, useCallback, useEffect } from 'react';
import { surveyService } from '@/lib/api';
import type { Survey, SurveyQuestion, Submission, Response, ResponseCreate, SurveyProgress, NextQuestionResponse } from '@/types';
import { useApi } from './useApi';

interface UseSurveyOptions {
  surveySlug: string;
  onComplete?: (submissionId: number) => void;
}

interface UseSurveyReturn {
  // Survey data
  survey: Survey | null;
  currentQuestion: SurveyQuestion | null;
  submission: Submission | null;
  progress: SurveyProgress | null;

  // State
  loading: boolean;
  error: string | null;
  currentIndex: number;
  isLastQuestion: boolean;

  // Actions
  startSurvey: (
    email: string,
    phone_number: string,
    region: string,
    date_of_birth: string,
    gender: string,
    external_user_id?: string
  ) => Promise<void>;
  submitResponse: (response: ResponseCreate) => Promise<void>;
  nextQuestion: () => void;
  previousQuestion: () => void;
  completeAndSubmit: () => Promise<void>;
  refetchProgress: () => Promise<void>;
}

export function useSurvey({ surveySlug, onComplete }: UseSurveyOptions): UseSurveyReturn {
  // Fetch survey data
  const {
    data: survey,
    loading: surveyLoading,
    error: surveyError,
  } = useApi<Survey>(
    () => surveyService.getSurveyBySlug(surveySlug),
    [surveySlug]
  );

  // Local state
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [progress, setProgress] = useState<SurveyProgress | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [responseLoading, setResponseLoading] = useState(false);
  const [responseError, setResponseError] = useState<string | null>(null);

  // Derived state
  const currentQuestion = survey?.survey_flow?.[currentIndex] || null;
  const isLastQuestion = survey ? currentIndex === survey.survey_flow.length - 1 : false;
  const loading = surveyLoading || responseLoading;
  const error = surveyError || responseError;

  // Start survey (create submission)
  const startSurvey = useCallback(async (
    email: string,
    phone_number: string,
    region: string,
    date_of_birth: string,
    gender: string,
    external_user_id?: string
  ) => {
    try {
      setResponseLoading(true);
      setResponseError(null);

      const newSubmission = await surveyService.createSubmission(surveySlug, {
        email,
        phone_number,
        region,
        date_of_birth,
        gender,
        external_user_id,
      });

      setSubmission(newSubmission);
      setCurrentIndex(0);

      // Fetch initial progress
      const initialProgress = await surveyService.getProgress(newSubmission.id);
      setProgress(initialProgress);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start survey';
      setResponseError(errorMessage);
      throw err;
    } finally {
      setResponseLoading(false);
    }
  }, [surveySlug]);

  // Submit response for current question
  const submitResponse = useCallback(async (response: ResponseCreate) => {
    if (!submission) {
      throw new Error('No active submission');
    }

    try {
      setResponseLoading(true);
      setResponseError(null);

      await surveyService.createResponse(submission.id, response);

      // Refresh progress
      const updatedProgress = await surveyService.getProgress(submission.id);
      setProgress(updatedProgress);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to submit response';
      setResponseError(errorMessage);
      throw err;
    } finally {
      setResponseLoading(false);
    }
  }, [submission]);

  // Complete submission
  const completeAndSubmit = useCallback(async () => {
    if (!submission) {
      throw new Error('No active submission');
    }

    try {
      setResponseLoading(true);
      setResponseError(null);

      await surveyService.completeSubmission(submission.id);

      if (onComplete) {
        onComplete(submission.id);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to complete survey';
      setResponseError(errorMessage);
      throw err;
    } finally {
      setResponseLoading(false);
    }
  }, [submission, onComplete]);

  // Navigation with routing logic
  const nextQuestion = useCallback(async () => {
    if (!survey || !submission || !currentQuestion) return;

    try {
      setResponseLoading(true);

      // Check if current question has routing rules
      if (currentQuestion.routing_rules && currentQuestion.routing_rules.length > 0) {
        // Use backend routing logic
        const routingResponse = await surveyService.getNextQuestion(
          submission.id,
          currentQuestion.id
        );

        if (routingResponse.action === 'end_survey') {
          // Survey ended early due to routing rule
          await completeAndSubmit();
          return;
        }

        // Navigate to the routed question
        if (routingResponse.question_index !== undefined) {
          setCurrentIndex(routingResponse.question_index);
        }
      } else {
        // No routing rules - use sequential navigation
        if (currentIndex < survey.survey_flow.length - 1) {
          setCurrentIndex(prev => prev + 1);
        }
      }
    } catch (err) {
      console.error('Error in routing logic:', err);
      // Fallback to sequential navigation
      if (currentIndex < survey.survey_flow.length - 1) {
        setCurrentIndex(prev => prev + 1);
      }
    } finally {
      setResponseLoading(false);
    }
  }, [survey, submission, currentQuestion, currentIndex, completeAndSubmit]);

  const previousQuestion = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  // Refetch progress
  const refetchProgress = useCallback(async () => {
    if (!submission) return;

    try {
      const updatedProgress = await surveyService.getProgress(submission.id);
      setProgress(updatedProgress);
    } catch (err) {
      console.error('Failed to refetch progress:', err);
    }
  }, [submission]);

  return {
    // Survey data
    survey,
    currentQuestion,
    submission,
    progress,

    // State
    loading,
    error,
    currentIndex,
    isLastQuestion,

    // Actions
    startSurvey,
    submitResponse,
    nextQuestion,
    previousQuestion,
    completeAndSubmit,
    refetchProgress,
  };
}
