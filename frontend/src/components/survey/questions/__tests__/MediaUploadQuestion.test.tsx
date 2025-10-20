/**
 * Tests for MediaUploadQuestion Component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MediaUploadQuestion from '../MediaUploadQuestion';
import { surveyService } from '@/lib/api';

// Mock the survey service
jest.mock('@/lib/api', () => ({
  surveyService: {
    uploadPhoto: jest.fn(),
    uploadVideo: jest.fn(),
  },
}));

describe('MediaUploadQuestion Component', () => {
  const mockQuestion = {
    id: 'q1',
    question: 'Upload a photo',
    question_type: 'photo' as const,
    required: true,
  };

  const defaultProps = {
    question: mockQuestion,
    onSubmit: jest.fn(),
    loading: false,
    surveySlug: 'test-survey',
    mediaType: 'photo' as const,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset URL mocks
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();
  });

  describe('Initial Render', () => {
    it('should render upload area for photo', () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      expect(screen.getByText(/Tap to upload/)).toBeInTheDocument();
      expect(screen.getByText(/PNG, JPG, GIF up to 10MB/)).toBeInTheDocument();
    });

    it('should render upload area for video', () => {
      render(<MediaUploadQuestion {...defaultProps} mediaType="video" />);

      expect(screen.getByText(/Tap to upload/)).toBeInTheDocument();
      expect(screen.getByText(/MP4, MOV, AVI up to 100MB/)).toBeInTheDocument();
    });

    it('should show Continue button', () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      expect(screen.getByText('Continue')).toBeInTheDocument();
    });

    it('should show Skip button for optional questions', () => {
      render(
        <MediaUploadQuestion
          {...defaultProps}
          question={{ ...mockQuestion, required: false }}
        />
      );

      expect(screen.getByText('Skip')).toBeInTheDocument();
    });

    it('should not show Skip button for required questions', () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      expect(screen.queryByText('Skip')).not.toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('should accept and preview photo file', async () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalledWith(file);
      });

      // Check that file info is displayed
      expect(screen.getByText('test.jpg')).toBeInTheDocument();
    });

    it('should accept and preview video file', async () => {
      render(<MediaUploadQuestion {...defaultProps} mediaType="video" />);

      const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalledWith(file);
      });

      expect(screen.getByText('test.mp4')).toBeInTheDocument();
    });

    it('should show error for invalid photo file type', async () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['not-image'], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Please select an image file')).toBeInTheDocument();
      });
    });

    it('should show error for invalid video file type', async () => {
      render(<MediaUploadQuestion {...defaultProps} mediaType="video" />);

      const file = new File(['not-video'], 'test.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Please select a video file')).toBeInTheDocument();
      });
    });

    it('should show error for photo file size too large', async () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      // Create a mock file larger than 10MB
      const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
      Object.defineProperty(largeFile, 'size', { value: 11 * 1024 * 1024 });

      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [largeFile] } });

      await waitFor(() => {
        expect(screen.getByText('Image must be smaller than 10MB')).toBeInTheDocument();
      });
    });

    it('should show error for video file size too large', async () => {
      render(<MediaUploadQuestion {...defaultProps} mediaType="video" />);

      // Create a mock file larger than 100MB
      const largeFile = new File(['x'.repeat(101 * 1024 * 1024)], 'large.mp4', { type: 'video/mp4' });
      Object.defineProperty(largeFile, 'size', { value: 101 * 1024 * 1024 });

      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [largeFile] } });

      await waitFor(() => {
        expect(screen.getByText('Video must be smaller than 100MB')).toBeInTheDocument();
      });
    });
  });

  describe('File Upload', () => {
    it('should upload photo successfully', async () => {
      (surveyService.uploadPhoto as jest.Mock).mockResolvedValue({
        file_url: 'https://example.com/photo.jpg',
        file_id: '123',
      });

      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Photo')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Photo'));

      await waitFor(() => {
        expect(surveyService.uploadPhoto).toHaveBeenCalledWith('test-survey', file);
        expect(screen.getByText('✅ Photo uploaded successfully!')).toBeInTheDocument();
      });
    });

    it('should upload video successfully', async () => {
      (surveyService.uploadVideo as jest.Mock).mockResolvedValue({
        file_url: 'https://example.com/video.mp4',
        file_id: '456',
      });

      render(<MediaUploadQuestion {...defaultProps} mediaType="video" />);

      const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Video')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Video'));

      await waitFor(() => {
        expect(surveyService.uploadVideo).toHaveBeenCalledWith('test-survey', file);
        expect(screen.getByText('✅ Video uploaded successfully!')).toBeInTheDocument();
      });
    });

    it('should show loading state during upload', async () => {
      (surveyService.uploadPhoto as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ file_url: 'url', file_id: '1' }), 1000))
      );

      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Photo')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Photo'));

      expect(screen.getByText('Uploading...')).toBeInTheDocument();
    });

    it('should handle upload error', async () => {
      (surveyService.uploadPhoto as jest.Mock).mockRejectedValue(new Error('Upload failed'));

      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Photo')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Photo'));

      await waitFor(() => {
        expect(screen.getByText('Upload failed')).toBeInTheDocument();
      });
    });
  });

  describe('File Removal', () => {
    it('should remove selected file', async () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('test.jpg')).toBeInTheDocument();
      });

      // Find and click remove button
      const removeButton = document.querySelector('button[type="button"]') as HTMLButtonElement;
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(screen.queryByText('test.jpg')).not.toBeInTheDocument();
        expect(global.URL.revokeObjectURL).toHaveBeenCalled();
      });
    });
  });

  describe('Form Submission', () => {
    it('should submit photo URL on form submit', async () => {
      (surveyService.uploadPhoto as jest.Mock).mockResolvedValue({
        file_url: 'https://example.com/photo.jpg',
        file_id: '123',
      });

      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Photo')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Photo'));

      await waitFor(() => {
        expect(screen.getByText('✅ Photo uploaded successfully!')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Continue'));

      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        photo_url: 'https://example.com/photo.jpg',
      });
    });

    it('should submit video URL on form submit', async () => {
      (surveyService.uploadVideo as jest.Mock).mockResolvedValue({
        file_url: 'https://example.com/video.mp4',
        file_id: '456',
      });

      const videoProps = { ...defaultProps, mediaType: 'video' as const };
      render(<MediaUploadQuestion {...videoProps} />);

      const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Video')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Video'));

      await waitFor(() => {
        expect(screen.getByText('✅ Video uploaded successfully!')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Continue'));

      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        video_url: 'https://example.com/video.mp4',
      });
    });

    it('should show error if required field not uploaded', async () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      const continueButton = screen.getByText('Continue');
      fireEvent.click(continueButton);

      // The error should appear after clicking submit
      await waitFor(() => {
        expect(screen.queryByText(/Please upload/)).toBeInTheDocument();
      });
      expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    });

    it('should allow skip for optional questions', () => {
      const optionalProps = {
        ...defaultProps,
        question: { ...mockQuestion, required: false },
      };

      render(<MediaUploadQuestion {...optionalProps} />);

      fireEvent.click(screen.getByText('Skip'));

      expect(defaultProps.onSubmit).toHaveBeenCalledWith({
        photo_url: '',
      });
    });
  });

  describe('Disabled States', () => {
    it('should disable input when loading', () => {
      render(<MediaUploadQuestion {...defaultProps} loading={true} />);

      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      expect(input).toBeDisabled();
    });

    it('should disable submit button when required and not uploaded', () => {
      render(<MediaUploadQuestion {...defaultProps} />);

      const continueButton = screen.getByText('Continue');

      expect(continueButton).toBeDisabled();
    });

    it('should enable submit button after successful upload', async () => {
      (surveyService.uploadPhoto as jest.Mock).mockResolvedValue({
        file_url: 'https://example.com/photo.jpg',
        file_id: '123',
      });

      render(<MediaUploadQuestion {...defaultProps} />);

      const file = new File(['photo'], 'test.jpg', { type: 'image/jpeg' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      fireEvent.change(input, { target: { files: [file] } });

      await waitFor(() => {
        expect(screen.getByText('Upload Photo')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Upload Photo'));

      await waitFor(() => {
        expect(screen.getByText('✅ Photo uploaded successfully!')).toBeInTheDocument();
      });

      const continueButton = screen.getByText('Continue');
      expect(continueButton).not.toBeDisabled();
    });
  });
});
