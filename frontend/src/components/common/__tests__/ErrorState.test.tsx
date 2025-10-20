/**
 * Tests for ErrorState Component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import ErrorState from '../ErrorState';
import { useRouter } from 'next/navigation';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

describe('ErrorState Component', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  it('should render with default props', () => {
    render(<ErrorState message="Something went wrong" />);

    // Title and message are the same, so we get multiple elements
    const elements = screen.getAllByText('Something went wrong');
    expect(elements.length).toBeGreaterThan(0);
    expect(screen.getByText('❌')).toBeInTheDocument();
  });

  it('should render with custom title', () => {
    render(<ErrorState title="Custom Error" message="Error message" />);

    expect(screen.getByText('Custom Error')).toBeInTheDocument();
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('should show retry button when onRetry is provided', () => {
    const onRetry = jest.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);

    const retryButton = screen.getByText('Try Again');
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('should not show retry button when onRetry is not provided', () => {
    render(<ErrorState message="Error" />);

    expect(screen.queryByText('Try Again')).not.toBeInTheDocument();
  });

  it('should show home button by default', () => {
    render(<ErrorState message="Error" />);

    const homeButton = screen.getByText('Go Home');
    expect(homeButton).toBeInTheDocument();

    fireEvent.click(homeButton);
    expect(mockPush).toHaveBeenCalledWith('/');
  });

  it('should not show home button when showHomeButton is false', () => {
    render(<ErrorState message="Error" showHomeButton={false} />);

    expect(screen.queryByText('Go Home')).not.toBeInTheDocument();
  });

  it('should show both retry and home buttons when both are enabled', () => {
    const onRetry = jest.fn();
    render(<ErrorState message="Error" onRetry={onRetry} showHomeButton={true} />);

    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
  });

  it('should render with fullScreen class by default', () => {
    const { container } = render(<ErrorState message="Error" />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('min-h-screen');
  });

  it('should render without fullScreen class when fullScreen is false', () => {
    const { container } = render(<ErrorState message="Error" fullScreen={false} />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).not.toHaveClass('min-h-screen');
    expect(wrapper).toHaveClass('py-12');
  });

  it('should have proper button styles', () => {
    const onRetry = jest.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);

    const retryButton = screen.getByText('Try Again');
    const homeButton = screen.getByText('Go Home');

    // Retry button should have primary styles
    expect(retryButton).toHaveClass('bg-blue-500');
    expect(retryButton).toHaveClass('text-white');

    // Home button should have secondary styles
    expect(homeButton).toHaveClass('border');
    expect(homeButton).toHaveClass('text-gray-700');
  });
});
