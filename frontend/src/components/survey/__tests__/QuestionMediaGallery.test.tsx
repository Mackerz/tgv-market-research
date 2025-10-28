/**
 * Unit tests for QuestionMediaGallery component
 * Tests carousel, navigation, media display, and edge cases
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import QuestionMediaGallery from '../QuestionMediaGallery';
import type { QuestionMedia } from '@/types/survey';

describe('QuestionMediaGallery', () => {
  const mockPhotoMedia: QuestionMedia[] = [
    {
      url: 'https://example.com/photo1.jpg',
      type: 'photo',
      caption: 'First photo'
    },
    {
      url: 'https://example.com/photo2.jpg',
      type: 'photo',
      caption: 'Second photo'
    }
  ];

  const mockVideoMedia: QuestionMedia[] = [
    {
      url: 'https://example.com/video1.mp4',
      type: 'video',
      caption: 'First video'
    }
  ];

  const mockMixedMedia: QuestionMedia[] = [
    {
      url: 'https://example.com/photo.jpg',
      type: 'photo',
      caption: 'A photo'
    },
    {
      url: 'https://example.com/video.mp4',
      type: 'video',
      caption: 'A video'
    }
  ];

  describe('Single Media Item', () => {
    it('renders single photo without carousel controls', () => {
      render(<QuestionMediaGallery mediaItems={[mockPhotoMedia[0]]} />);

      const img = screen.getByRole('img');
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute('src', 'https://example.com/photo1.jpg');

      // No navigation arrows for single item
      expect(screen.queryByLabelText('Previous media')).not.toBeInTheDocument();
      expect(screen.queryByLabelText('Next media')).not.toBeInTheDocument();
    });

    it('renders single video without carousel controls', () => {
      render(<QuestionMediaGallery mediaItems={[mockVideoMedia[0]]} />);

      const video = screen.getByRole('generic').querySelector('video');
      expect(video).toBeInTheDocument();
      expect(video).toHaveAttribute('src', 'https://example.com/video1.mp4');

      // No navigation
      expect(screen.queryByLabelText('Previous media')).not.toBeInTheDocument();
    });

    it('displays caption for single media', () => {
      render(<QuestionMediaGallery mediaItems={[mockPhotoMedia[0]]} />);

      // Caption should be in img alt or in DOM
      expect(screen.getByText('First photo')).toBeInTheDocument();
    });
  });

  describe('Multiple Media Items', () => {
    it('renders first item initially', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', 'https://example.com/photo1.jpg');
    });

    it('shows navigation arrows for multiple items', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByLabelText('Previous media')).toBeInTheDocument();
      expect(screen.getByLabelText('Next media')).toBeInTheDocument();
    });

    it('shows counter with current/total', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByText('1 / 2')).toBeInTheDocument();
    });

    it('navigates to next media when next button clicked', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const nextButton = screen.getByLabelText('Next media');
      fireEvent.click(nextButton);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', 'https://example.com/photo2.jpg');
      expect(screen.getByText('2 / 2')).toBeInTheDocument();
    });

    it('navigates to previous media when prev button clicked', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      // Go to second item
      const nextButton = screen.getByLabelText('Next media');
      fireEvent.click(nextButton);

      // Go back
      const prevButton = screen.getByLabelText('Previous media');
      fireEvent.click(prevButton);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', 'https://example.com/photo1.jpg');
      expect(screen.getByText('1 / 2')).toBeInTheDocument();
    });

    it('disables prev button on first item', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const prevButton = screen.getByLabelText('Previous media');
      expect(prevButton).toBeDisabled();
    });

    it('disables next button on last item', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      // Navigate to last item
      const nextButton = screen.getByLabelText('Next media');
      fireEvent.click(nextButton);

      expect(nextButton).toBeDisabled();
    });
  });

  describe('Thumbnail Navigation', () => {
    it('shows thumbnails for 2-4 items', () => {
      const fourItems: QuestionMedia[] = [
        { url: 'https://example.com/1.jpg', type: 'photo' },
        { url: 'https://example.com/2.jpg', type: 'photo' },
        { url: 'https://example.com/3.jpg', type: 'photo' },
        { url: 'https://example.com/4.jpg', type: 'photo' }
      ];

      render(<QuestionMediaGallery mediaItems={fourItems} />);

      // Should have 4 thumbnail buttons
      const thumbnails = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );
      expect(thumbnails).toHaveLength(4);
    });

    it('clicking thumbnail navigates to that media', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const thumbnails = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );

      // Click second thumbnail
      fireEvent.click(thumbnails[1]);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('src', 'https://example.com/photo2.jpg');
    });

    it('highlights current thumbnail', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const thumbnails = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );

      // First thumbnail should have active styling (blue border)
      expect(thumbnails[0]).toHaveClass('border-[#D01A8A]');
    });
  });

  describe('Dot Indicators', () => {
    it('shows dot indicators for any multiple items', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const dots = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );
      expect(dots.length).toBeGreaterThan(0);
    });

    it('highlights current dot', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const dots = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );

      // First dot should be highlighted (wider and blue)
      expect(dots[0]).toHaveClass('bg-[#D01A8A]');
    });

    it('clicking dot navigates to that media', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const dots = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );

      fireEvent.click(dots[1]);

      expect(screen.getByText('2 / 2')).toBeInTheDocument();
    });
  });

  describe('Mixed Media Types', () => {
    it('handles photo and video in same gallery', () => {
      render(<QuestionMediaGallery mediaItems={mockMixedMedia} />);

      // First item is photo
      expect(screen.getByRole('img')).toBeInTheDocument();

      // Navigate to video
      const nextButton = screen.getByLabelText('Next media');
      fireEvent.click(nextButton);

      // Second item is video
      const video = screen.getByRole('generic').querySelector('video');
      expect(video).toBeInTheDocument();
    });

    it('shows correct icon for video in thumbnail', () => {
      render(<QuestionMediaGallery mediaItems={mockMixedMedia} />);

      // Video thumbnail should show play icon
      const thumbnails = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );

      // Second thumbnail (video) should have play icon
      const videoThumbnail = thumbnails[1];
      expect(videoThumbnail.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Captions', () => {
    it('displays caption below media', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByText('First photo')).toBeInTheDocument();
    });

    it('updates caption when navigating', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByText('First photo')).toBeInTheDocument();

      const nextButton = screen.getByLabelText('Next media');
      fireEvent.click(nextButton);

      expect(screen.getByText('Second photo')).toBeInTheDocument();
    });

    it('handles media without captions', () => {
      const noCaptionMedia: QuestionMedia[] = [
        { url: 'https://example.com/1.jpg', type: 'photo' },
        { url: 'https://example.com/2.jpg', type: 'photo' }
      ];

      render(<QuestionMediaGallery mediaItems={noCaptionMedia} />);

      // Should still render without errors
      expect(screen.getByRole('img')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('renders nothing when mediaItems is empty', () => {
      const { container } = render(<QuestionMediaGallery mediaItems={[]} />);

      expect(container.firstChild).toBeNull();
    });

    it('renders nothing when mediaItems is undefined', () => {
      const { container } = render(<QuestionMediaGallery mediaItems={undefined as any} />);

      expect(container.firstChild).toBeNull();
    });

    it('handles many media items (10+)', () => {
      const manyItems: QuestionMedia[] = Array.from({ length: 15 }, (_, i) => ({
        url: `https://example.com/photo${i + 1}.jpg`,
        type: 'photo' as const,
        caption: `Photo ${i + 1}`
      }));

      render(<QuestionMediaGallery mediaItems={manyItems} />);

      expect(screen.getByText('1 / 15')).toBeInTheDocument();

      // Should have dots instead of thumbnails
      const dots = screen.getAllByRole('button').filter(btn =>
        btn.getAttribute('aria-label')?.startsWith('Go to media')
      );
      expect(dots).toHaveLength(15);
    });

    it('uses altText prop when no caption provided', () => {
      const noCaptionMedia: QuestionMedia[] = [
        { url: 'https://example.com/photo.jpg', type: 'photo' }
      ];

      render(<QuestionMediaGallery mediaItems={noCaptionMedia} altText="Survey question image" />);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('alt', 'Survey question image');
    });

    it('prefers media caption over altText', () => {
      render(<QuestionMediaGallery mediaItems={[mockPhotoMedia[0]]} altText="Fallback text" />);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('alt', 'First photo');
    });
  });

  describe('Loading States', () => {
    it('shows loading spinner before image loads', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      // Should show spinner initially
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('hides loading spinner after image loads', async () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const img = screen.getByRole('img');

      // Simulate image load
      fireEvent.load(img);

      await waitFor(() => {
        const spinner = document.querySelector('.animate-spin');
        expect(spinner).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows error message when image fails to load', async () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const img = screen.getByRole('img');

      // Simulate image error
      fireEvent.error(img);

      await waitFor(() => {
        expect(screen.getByText('Unable to load media')).toBeInTheDocument();
      });
    });

    it('shows caption in error state', async () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      const img = screen.getByRole('img');
      fireEvent.error(img);

      await waitFor(() => {
        expect(screen.getByText('First photo')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels on navigation buttons', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByLabelText('Previous media')).toBeInTheDocument();
      expect(screen.getByLabelText('Next media')).toBeInTheDocument();
    });

    it('has proper ARIA labels on thumbnail/dot buttons', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} />);

      expect(screen.getByLabelText('Go to media 1')).toBeInTheDocument();
      expect(screen.getByLabelText('Go to media 2')).toBeInTheDocument();
    });

    it('images have alt text', () => {
      render(<QuestionMediaGallery mediaItems={mockPhotoMedia} altText="Test alt" />);

      const img = screen.getByRole('img');
      expect(img).toHaveAttribute('alt');
    });

    it('videos have fallback text', () => {
      render(<QuestionMediaGallery mediaItems={mockVideoMedia} />);

      expect(screen.getByText('Your browser does not support the video tag.')).toBeInTheDocument();
    });
  });
});
