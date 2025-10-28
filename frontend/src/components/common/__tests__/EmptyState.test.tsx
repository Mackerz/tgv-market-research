/**
 * Tests for EmptyState Component
 */

import { render, screen, fireEvent } from '@testing-library/react';
import EmptyState from '../EmptyState';

describe('EmptyState Component', () => {
  it('should render with required props only', () => {
    render(<EmptyState title="No items found" />);

    expect(screen.getByText('No items found')).toBeInTheDocument();
    expect(screen.getByText('📭')).toBeInTheDocument(); // default icon
  });

  it('should render with custom icon', () => {
    render(<EmptyState icon="🔍" title="No results" />);

    expect(screen.getByText('🔍')).toBeInTheDocument();
    expect(screen.queryByText('📭')).not.toBeInTheDocument();
  });

  it('should render with message', () => {
    render(
      <EmptyState
        title="No surveys"
        message="Create your first survey to get started"
      />
    );

    expect(screen.getByText('No surveys')).toBeInTheDocument();
    expect(screen.getByText('Create your first survey to get started')).toBeInTheDocument();
  });

  it('should not render message when not provided', () => {
    render(<EmptyState title="Empty" />);

    // Only title should be present
    expect(screen.getByText('Empty')).toBeInTheDocument();
  });

  it('should render action button when provided', () => {
    const onClick = jest.fn();

    render(
      <EmptyState
        title="No items"
        action={{
          label: 'Create Item',
          onClick,
        }}
      />
    );

    const button = screen.getByText('Create Item');
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should not render action button when not provided', () => {
    render(<EmptyState title="Empty" />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('should not render with fullScreen class by default', () => {
    const { container } = render(<EmptyState title="Empty" />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).not.toHaveClass('min-h-screen');
    expect(wrapper).toHaveClass('py-12');
  });

  it('should render with fullScreen class when fullScreen is true', () => {
    const { container } = render(<EmptyState title="Empty" fullScreen={true} />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('min-h-screen');
  });

  it('should have proper styling', () => {
    const onClick = jest.fn();

    render(
      <EmptyState
        title="No items"
        message="Get started by creating one"
        action={{ label: 'Create', onClick }}
      />
    );

    const title = screen.getByText('No items');
    const message = screen.getByText('Get started by creating one');
    const button = screen.getByText('Create');

    // Title should be bold
    expect(title).toHaveClass('font-bold');
    expect(title).toHaveClass('text-2xl');

    // Message should have muted color
    expect(message).toHaveClass('text-gray-600');

    // Button should have primary styling
    expect(button).toHaveClass('bg-[#D01A8A]');
    expect(button).toHaveClass('text-white');
  });

  it('should handle complex action scenarios', () => {
    const handleCreate = jest.fn();

    render(
      <EmptyState
        icon="📝"
        title="No surveys yet"
        message="Surveys help you gather valuable insights from your audience"
        action={{
          label: 'Create Your First Survey',
          onClick: handleCreate,
        }}
        fullScreen={true}
      />
    );

    expect(screen.getByText('📝')).toBeInTheDocument();
    expect(screen.getByText('No surveys yet')).toBeInTheDocument();
    expect(screen.getByText('Surveys help you gather valuable insights from your audience')).toBeInTheDocument();

    const button = screen.getByText('Create Your First Survey');
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(handleCreate).toHaveBeenCalledTimes(1);
  });
});
