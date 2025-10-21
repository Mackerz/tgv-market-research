/**
 * Tests for useSurvey Hook
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useSurvey } from '../useSurvey';
import { surveyService } from '@/lib/api';

// Mock the survey service
jest.mock('@/lib/api', () => ({
  surveyService: {
    getSurveyBySlug: jest.fn(),
    createSubmission: jest.fn(),
    createResponse: jest.fn(),
    getProgress: jest.fn(),
    completeSubmission: jest.fn(),
  },
}));

describe('useSurvey Hook', () => {
  const mockSurvey = {
    id: 1,
    survey_slug: 'test-survey',
    name: 'Test Survey',
    survey_flow: [
      { id: 'q1', question: 'Question 1', question_type: 'free_text' as const, required: true },
      { id: 'q2', question: 'Question 2', question_type: 'single' as const, required: false, options: ['A', 'B'] },
    ],
    is_active: true,
  };

  const mockSubmission = {
    id: 1,
    email: 'test@example.com',
    phone_number: '+1234567890',
    region: 'US',
    date_of_birth: '1998-01-01',
    gender: 'Male',
    submitted_at: new Date().toISOString(),
    is_completed: false,
    is_approved: null,
  };

  const mockProgress = {
    current_question: 0,
    total_questions: 2,
    submission_id: 1,
    is_completed: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (surveyService.getSurveyBySlug as jest.Mock).mockResolvedValue(mockSurvey);
  });

  it('should fetch survey on mount', async () => {
    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.survey).toEqual(mockSurvey);
    expect(surveyService.getSurveyBySlug).toHaveBeenCalledWith('test-survey');
  });

  it('should start survey and create submission', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    // Start survey
    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    expect(surveyService.createSubmission).toHaveBeenCalledWith('test-survey', {
      email: 'test@example.com',
      phone_number: '+1234567890',
      region: 'US',
      date_of_birth: '1998-01-01',
      gender: 'Male',
    });
    expect(result.current.submission).toEqual(mockSubmission);
    expect(result.current.progress).toEqual(mockProgress);
  });

  it('should submit response for a question', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);
    (surveyService.createResponse as jest.Mock).mockResolvedValue({});

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    // Start survey first
    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    // Submit response
    await act(async () => {
      await result.current.submitResponse({
        question: 'q1',
        question_type: 'free_text',
        free_text_answer: 'My answer',
      });
    });

    expect(surveyService.createResponse).toHaveBeenCalledWith(1, {
      question: 'q1',
      question_type: 'free_text',
      free_text_answer: 'My answer',
    });
  });

  it('should navigate to next question', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    expect(result.current.currentIndex).toBe(0);
    expect(result.current.currentQuestion?.id).toBe('q1');

    // Navigate to next question
    act(() => {
      result.current.nextQuestion();
    });

    expect(result.current.currentIndex).toBe(1);
    expect(result.current.currentQuestion?.id).toBe('q2');
  });

  it('should navigate to previous question', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue({
      ...mockProgress,
      current_question: 1,
    });

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    // Move to second question first
    act(() => {
      result.current.nextQuestion();
    });

    expect(result.current.currentIndex).toBe(1);

    // Navigate back
    act(() => {
      result.current.previousQuestion();
    });

    expect(result.current.currentIndex).toBe(0);
  });

  it('should not navigate before first question', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    expect(result.current.currentIndex).toBe(0);

    // Try to go back
    act(() => {
      result.current.previousQuestion();
    });

    // Should still be at 0
    expect(result.current.currentIndex).toBe(0);
  });

  it('should not navigate beyond last question', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    // Navigate to last question
    act(() => {
      result.current.nextQuestion();
    });

    expect(result.current.currentIndex).toBe(1);
    expect(result.current.isLastQuestion).toBe(true);

    // Try to go forward
    act(() => {
      result.current.nextQuestion();
    });

    // Should still be at last question
    expect(result.current.currentIndex).toBe(1);
  });

  it('should complete survey and call onComplete callback', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);
    (surveyService.completeSubmission as jest.Mock).mockResolvedValue({});

    const onComplete = jest.fn();

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey', onComplete })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    // Complete survey
    await act(async () => {
      await result.current.completeAndSubmit();
    });

    expect(surveyService.completeSubmission).toHaveBeenCalledWith(1);
    expect(onComplete).toHaveBeenCalledWith(1);
  });

  it('should refetch progress', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock)
      .mockResolvedValueOnce(mockProgress)
      .mockResolvedValueOnce({ ...mockProgress, current_question: 1 });

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    expect(result.current.progress?.current_question).toBe(0);

    // Refetch progress
    await act(async () => {
      await result.current.refetchProgress();
    });

    expect(result.current.progress?.current_question).toBe(1);
    expect(surveyService.getProgress).toHaveBeenCalledTimes(2);
  });

  it('should handle errors when starting survey', async () => {
    const error = new Error('Failed to create submission');
    (surveyService.createSubmission as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    // Attempt to start survey
    await expect(
      act(async () => {
        await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
      })
    ).rejects.toThrow('Failed to create submission');

    expect(result.current.error).toBe('Failed to create submission');
  });

  it('should throw error if submitting response without active submission', async () => {
    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    // Try to submit response without starting survey
    await expect(
      act(async () => {
        await result.current.submitResponse({
          question: 'q1',
          question_type: 'free_text',
          free_text_answer: 'answer',
        });
      })
    ).rejects.toThrow('No active submission');
  });

  it('should provide current question information', async () => {
    (surveyService.createSubmission as jest.Mock).mockResolvedValue(mockSubmission);
    (surveyService.getProgress as jest.Mock).mockResolvedValue(mockProgress);

    const { result } = renderHook(() =>
      useSurvey({ surveySlug: 'test-survey' })
    );

    await waitFor(() => {
      expect(result.current.survey).toEqual(mockSurvey);
    });

    await act(async () => {
      await result.current.startSurvey('test@example.com', '+1234567890', 'US', '1998-01-01', 'Male');
    });

    expect(result.current.currentQuestion).toEqual(mockSurvey.survey_flow[0]);
    expect(result.current.currentIndex).toBe(0);
    expect(result.current.isLastQuestion).toBe(false);
  });
});
