/**
 * Tests for LoadingState Component
 */

import { render, screen } from '@testing-library/react';
import LoadingState from '../LoadingState';

describe('LoadingState Component', () => {
  it('should render with default props', () => {
    render(<LoadingState />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Check for spinner (by class or role)
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('should render with custom message', () => {
    render(<LoadingState message="Loading survey..." />);

    expect(screen.getByText('Loading survey...')).toBeInTheDocument();
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('should render with fullScreen class by default', () => {
    const { container } = render(<LoadingState />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('min-h-screen');
  });

  it('should render without fullScreen class when fullScreen is false', () => {
    const { container } = render(<LoadingState fullScreen={false} />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).not.toHaveClass('min-h-screen');
    expect(wrapper).toHaveClass('py-12');
  });

  it('should have proper accessibility structure', () => {
    render(<LoadingState message="Loading data..." />);

    // The component should communicate loading state to screen readers
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  it('should render spinner with correct styles', () => {
    render(<LoadingState />);

    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('rounded-full');
    expect(spinner).toHaveClass('border-b-2');
    expect(spinner).toHaveClass('border-[#D01A8A]');
  });
});
