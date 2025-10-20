/**
 * Tests for API Services
 */

import { surveyService, reportingService } from '../';
import { apiClient } from '../client';

// Mock the API client
jest.mock('../client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    upload: jest.fn(),
  },
  ApiError: class ApiError extends Error {
    constructor(public status: number, public statusText: string, public data: any, message?: string) {
      super(message);
      this.name = 'ApiError';
    }
  },
}));

describe('Survey Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSurveyBySlug', () => {
    it('should fetch survey by slug', async () => {
      const mockSurvey = {
        id: 1,
        survey_slug: 'test-survey',
        name: 'Test Survey',
        survey_flow: [],
        is_active: true,
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockSurvey);

      const result = await surveyService.getSurveyBySlug('test-survey');

      expect(apiClient.get).toHaveBeenCalledWith('/api/surveys/slug/test-survey');
      expect(result).toEqual(mockSurvey);
    });
  });

  describe('createSubmission', () => {
    it('should create a new submission', async () => {
      const submissionData = {
        email: 'test@example.com',
        region: 'North',
        age: 25,
      };

      const mockSubmission = {
        id: 1,
        ...submissionData,
        submitted_at: new Date().toISOString(),
        is_completed: false,
        is_approved: null,
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce(mockSubmission);

      const result = await surveyService.createSubmission('test-survey', submissionData);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/surveys/test-survey/submit',
        submissionData
      );
      expect(result).toEqual(mockSubmission);
    });
  });

  describe('getProgress', () => {
    it('should fetch submission progress', async () => {
      const mockProgress = {
        current_question: 5,
        total_questions: 10,
        submission_id: 1,
        is_completed: false,
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockProgress);

      const result = await surveyService.getProgress(1);

      expect(apiClient.get).toHaveBeenCalledWith('/api/submissions/1/progress');
      expect(result).toEqual(mockProgress);
    });
  });

  describe('completeSubmission', () => {
    it('should complete a submission', async () => {
      (apiClient.put as jest.Mock).mockResolvedValueOnce({ success: true });

      await surveyService.completeSubmission(1);

      expect(apiClient.put).toHaveBeenCalledWith('/api/submissions/1/complete');
    });
  });

  describe('createResponse', () => {
    it('should create a response', async () => {
      const responseData = {
        question_id: 'q1',
        value: 'Test answer',
      };

      const mockResponse = {
        id: 1,
        question_id: 'q1',
        single_answer: 'Test answer',
        responded_at: new Date().toISOString(),
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await surveyService.createResponse(1, responseData);

      expect(apiClient.post).toHaveBeenCalledWith(
        '/api/submissions/1/responses',
        responseData
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('uploadPhoto', () => {
    it('should upload a photo', async () => {
      const mockFile = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const mockResponse = {
        file_url: 'https://example.com/photo.jpg',
        file_id: '123',
      };

      (apiClient.upload as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await surveyService.uploadPhoto('test-survey', mockFile);

      expect(apiClient.upload).toHaveBeenCalledWith(
        '/api/surveys/test-survey/upload/photo',
        expect.any(FormData)
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('uploadVideo', () => {
    it('should upload a video', async () => {
      const mockFile = new File(['video'], 'test.mp4', { type: 'video/mp4' });
      const mockResponse = {
        file_url: 'https://example.com/video.mp4',
        file_id: '456',
      };

      (apiClient.upload as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await surveyService.uploadVideo('test-survey', mockFile);

      expect(apiClient.upload).toHaveBeenCalledWith(
        '/api/surveys/test-survey/upload/video',
        expect.any(FormData)
      );
      expect(result).toEqual(mockResponse);
    });
  });
});

describe('Reporting Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getSubmissions', () => {
    it('should fetch submissions with default params', async () => {
      const mockResponse = {
        submissions: [],
        total_count: 0,
        approved_count: 0,
        rejected_count: 0,
        pending_count: 0,
        survey: { id: 1, name: 'Test', survey_slug: 'test' },
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await reportingService.getSubmissions('test-survey');

      expect(apiClient.get).toHaveBeenCalledWith('/api/reports/test-survey/submissions', {
        params: {},
      });
      expect(result).toEqual(mockResponse);
    });

    it('should convert approval filter to API format', async () => {
      const mockResponse = {
        submissions: [],
        total_count: 0,
        approved_count: 0,
        rejected_count: 0,
        pending_count: 0,
        survey: { id: 1, name: 'Test', survey_slug: 'test' },
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockResponse);

      await reportingService.getSubmissions('test-survey', { approved: 'approved' });

      expect(apiClient.get).toHaveBeenCalledWith('/api/reports/test-survey/submissions', {
        params: { approved: 'true' },
      });
    });

    it('should handle pending filter correctly', async () => {
      const mockResponse = {
        submissions: [],
        total_count: 0,
        approved_count: 0,
        rejected_count: 0,
        pending_count: 0,
        survey: { id: 1, name: 'Test', survey_slug: 'test' },
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockResponse);

      await reportingService.getSubmissions('test-survey', { approved: 'pending' });

      expect(apiClient.get).toHaveBeenCalledWith('/api/reports/test-survey/submissions', {
        params: { approved: 'null' },
      });
    });
  });

  describe('approveSubmission', () => {
    it('should approve a submission', async () => {
      (apiClient.put as jest.Mock).mockResolvedValueOnce({ success: true });

      await reportingService.approveSubmission('test-survey', 1);

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/reports/test-survey/submissions/1/approve'
      );
    });
  });

  describe('rejectSubmission', () => {
    it('should reject a submission', async () => {
      (apiClient.put as jest.Mock).mockResolvedValueOnce({ success: true });

      await reportingService.rejectSubmission('test-survey', 1);

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/reports/test-survey/submissions/1/reject'
      );
    });
  });

  describe('getReportingData', () => {
    it('should fetch reporting data', async () => {
      const mockData = {
        total_submissions: 100,
        completed_approved_submissions: 80,
        survey_name: 'Test Survey',
        survey_slug: 'test-survey',
        generated_at: new Date().toISOString(),
        demographics: {
          age_ranges: { labels: [], data: [] },
          regions: { labels: [], data: [] },
          genders: { labels: [], data: [] },
        },
        question_responses: [],
        media_analysis: {
          photos: { labels: [], data: [] },
          videos: { labels: [], data: [] },
        },
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockData);

      const result = await reportingService.getReportingData('test-survey');

      expect(apiClient.get).toHaveBeenCalledWith('/api/reports/test-survey/data');
      expect(result).toEqual(mockData);
    });
  });

  describe('getMediaGallery', () => {
    it('should fetch media gallery with filters', async () => {
      const mockResponse = {
        items: [],
        total_count: 0,
      };

      (apiClient.get as jest.Mock).mockResolvedValueOnce(mockResponse);

      await reportingService.getMediaGallery('test-survey', {
        labels: 'label1,label2',
        regions: 'North,South',
      });

      expect(apiClient.get).toHaveBeenCalledWith('/api/reports/test-survey/media-gallery', {
        params: { labels: 'label1,label2', regions: 'North,South' },
      });
    });
  });

  describe('updateAgeRanges', () => {
    it('should update age ranges', async () => {
      const ageRanges = [
        { min: 18, max: 25, label: '18-25' },
        { min: 26, max: 35, label: '26-35' },
      ];

      (apiClient.put as jest.Mock).mockResolvedValueOnce({ success: true });

      await reportingService.updateAgeRanges('test-survey', ageRanges);

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/reports/test-survey/settings/age-ranges',
        { age_ranges: ageRanges }
      );
    });
  });

  describe('updateQuestionDisplayNames', () => {
    it('should update question display names', async () => {
      const updates = [
        { question_id: 'q1', display_name: 'Question 1' },
        { question_id: 'q2', display_name: 'Question 2' },
      ];

      (apiClient.put as jest.Mock).mockResolvedValueOnce({ success: true });

      await reportingService.updateQuestionDisplayNames('test-survey', updates);

      expect(apiClient.put).toHaveBeenCalledWith(
        '/api/reports/test-survey/settings/question-display-names',
        { question_updates: updates }
      );
    });
  });
});
