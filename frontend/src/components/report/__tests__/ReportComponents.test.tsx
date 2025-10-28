/**
 * Tests for Report Components
 */

import { render, screen, fireEvent } from '@testing-library/react';
import ReportTabs from '../ReportTabs';
import SubmissionsStats from '../SubmissionsStats';
import SubmissionsFilters from '../SubmissionsFilters';
import SubmissionsList from '../SubmissionsList';

describe('ReportTabs Component', () => {
  it('should render all tabs', () => {
    const onTabChange = jest.fn();

    render(
      <ReportTabs
        activeTab="submissions"
        onTabChange={onTabChange}
        surveyName="Test Survey"
      />
    );

    expect(screen.getByText('Test Survey')).toBeInTheDocument();
    expect(screen.getByText('Submissions')).toBeInTheDocument();
    expect(screen.getByText('Reporting')).toBeInTheDocument();
    expect(screen.getByText('Media Gallery')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('should highlight active tab', () => {
    const onTabChange = jest.fn();

    render(
      <ReportTabs
        activeTab="reporting"
        onTabChange={onTabChange}
        surveyName="Test Survey"
      />
    );

    const reportingButton = screen.getByText('Reporting').closest('button');
    const submissionsButton = screen.getByText('Submissions').closest('button');

    expect(reportingButton).toHaveClass('bg-[#D01A8A]');
    expect(reportingButton).toHaveClass('text-white');
    expect(submissionsButton).not.toHaveClass('bg-[#D01A8A]');
  });

  it('should call onTabChange when tab is clicked', () => {
    const onTabChange = jest.fn();

    render(
      <ReportTabs
        activeTab="submissions"
        onTabChange={onTabChange}
        surveyName="Test Survey"
      />
    );

    fireEvent.click(screen.getByText('Reporting'));
    expect(onTabChange).toHaveBeenCalledWith('reporting');

    fireEvent.click(screen.getByText('Media Gallery'));
    expect(onTabChange).toHaveBeenCalledWith('media-gallery');
  });
});

describe('SubmissionsStats Component', () => {
  it('should render all stat cards', () => {
    render(
      <SubmissionsStats
        totalCount={100}
        approvedCount={60}
        rejectedCount={20}
        pendingCount={15}
      />
    );

    expect(screen.getByText('Total')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();

    expect(screen.getByText('Approved')).toBeInTheDocument();
    expect(screen.getByText('60')).toBeInTheDocument();

    expect(screen.getByText('Rejected')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('should render with zero values', () => {
    render(
      <SubmissionsStats
        totalCount={0}
        approvedCount={0}
        rejectedCount={0}
        pendingCount={0}
      />
    );

    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThan(0);
  });

  it('should have correct color coding for each stat', () => {
    const { container } = render(
      <SubmissionsStats
        totalCount={100}
        approvedCount={60}
        rejectedCount={20}
        pendingCount={15}
      />
    );

    // Get the parent div (not just any closest div)
    const totalCard = screen.getByText('Total').parentElement?.parentElement;
    const approvedCard = screen.getByText('Approved').parentElement?.parentElement;
    const rejectedCard = screen.getByText('Rejected').parentElement?.parentElement;
    const pendingCard = screen.getByText('Pending').parentElement?.parentElement;

    expect(totalCard).toHaveClass('bg-[#F5E8F0]');
    expect(approvedCard).toHaveClass('bg-green-100');
    expect(rejectedCard).toHaveClass('bg-red-100');
    expect(pendingCard).toHaveClass('bg-yellow-100');
  });
});

describe('SubmissionsFilters Component', () => {
  const defaultProps = {
    approvalFilter: 'all' as const,
    sortBy: 'submitted_at' as const,
    sortOrder: 'desc' as const,
    onApprovalFilterChange: jest.fn(),
    onSortByChange: jest.fn(),
    onSortOrderChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all filter controls', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    expect(screen.getByText('Filter:')).toBeInTheDocument();
    expect(screen.getByText('Sort by:')).toBeInTheDocument();
  });

  it('should call onApprovalFilterChange when filter changes', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    const filterSelect = screen.getByDisplayValue('All');
    fireEvent.change(filterSelect, { target: { value: 'approved' } });

    expect(defaultProps.onApprovalFilterChange).toHaveBeenCalledWith('approved');
  });

  it('should call onSortByChange when sort changes', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    const sortSelect = screen.getByDisplayValue('Date Submitted');
    fireEvent.change(sortSelect, { target: { value: 'email' } });

    expect(defaultProps.onSortByChange).toHaveBeenCalledWith('email');
  });

  it('should call onSortOrderChange when sort order button is clicked', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    const sortOrderButton = screen.getByText('↓ Descending');
    fireEvent.click(sortOrderButton);

    expect(defaultProps.onSortOrderChange).toHaveBeenCalledWith('asc');
  });

  it('should display correct sort order icon', () => {
    const { rerender } = render(<SubmissionsFilters {...defaultProps} />);

    expect(screen.getByText('↓ Descending')).toBeInTheDocument();

    rerender(<SubmissionsFilters {...defaultProps} sortOrder="asc" />);

    expect(screen.getByText('↑ Ascending')).toBeInTheDocument();
  });

  it('should have all filter options', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    const filterSelect = screen.getByDisplayValue('All');

    expect(filterSelect.querySelectorAll('option')).toHaveLength(4);
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
    expect(screen.getByText('Rejected')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('should have all sort options', () => {
    render(<SubmissionsFilters {...defaultProps} />);

    const sortSelect = screen.getByDisplayValue('Date Submitted');

    expect(sortSelect.querySelectorAll('option')).toHaveLength(4);
  });
});

describe('SubmissionsList Component', () => {
  const mockSubmissions = [
    {
      id: 1,
      email: 'user1@example.com',
      region: 'North',
      age: 25,
      submitted_at: '2025-01-15T10:00:00Z',
      is_approved: null,
      is_completed: true,
      phone_number: '',
      gender: '',
    },
    {
      id: 2,
      email: 'user2@example.com',
      region: 'South',
      age: 30,
      submitted_at: '2025-01-16T11:00:00Z',
      is_approved: true,
      is_completed: true,
      phone_number: '',
      gender: '',
    },
    {
      id: 3,
      email: 'user3@example.com',
      region: 'East',
      age: 35,
      submitted_at: '2025-01-17T12:00:00Z',
      is_approved: false,
      is_completed: true,
      phone_number: '',
      gender: '',
    },
  ];

  const defaultProps = {
    submissions: mockSubmissions,
    onViewDetail: jest.fn(),
    onApprove: jest.fn(),
    onReject: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render all submissions', () => {
    render(<SubmissionsList {...defaultProps} />);

    expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    expect(screen.getByText('user2@example.com')).toBeInTheDocument();
    expect(screen.getByText('user3@example.com')).toBeInTheDocument();
  });

  it('should show empty state when no submissions', () => {
    render(<SubmissionsList {...defaultProps} submissions={[]} />);

    expect(screen.getByText('No submissions found')).toBeInTheDocument();
  });

  it('should display correct approval badges', () => {
    render(<SubmissionsList {...defaultProps} />);

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('should call onViewDetail when View Details is clicked', () => {
    render(<SubmissionsList {...defaultProps} />);

    const viewButtons = screen.getAllByText('View Details');
    fireEvent.click(viewButtons[0]);

    expect(defaultProps.onViewDetail).toHaveBeenCalledWith(1);
  });

  it('should show approve/reject buttons only for pending completed submissions', () => {
    render(<SubmissionsList {...defaultProps} />);

    // First submission is pending and completed - should have approve/reject buttons
    const firstSubmission = screen.getByText('user1@example.com').closest('div')?.parentElement;
    expect(firstSubmission).toBeInTheDocument();

    // Should have approve and reject buttons
    const approveButtons = screen.getAllByText('Approve');
    const rejectButtons = screen.getAllByText('Reject');

    expect(approveButtons).toHaveLength(1); // Only one pending submission
    expect(rejectButtons).toHaveLength(1);
  });

  it('should call onApprove when Approve is clicked', async () => {
    render(<SubmissionsList {...defaultProps} />);

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    expect(defaultProps.onApprove).toHaveBeenCalledWith(1);
  });

  it('should call onReject when Reject is clicked', async () => {
    render(<SubmissionsList {...defaultProps} />);

    const rejectButton = screen.getByText('Reject');
    fireEvent.click(rejectButton);

    expect(defaultProps.onReject).toHaveBeenCalledWith(1);
  });

  it('should display submission information correctly', () => {
    render(<SubmissionsList {...defaultProps} />);

    expect(screen.getByText(/North/)).toBeInTheDocument();
    expect(screen.getByText(/South/)).toBeInTheDocument();
    expect(screen.getByText(/East/)).toBeInTheDocument();
  });

  it('should show incomplete badge for incomplete submissions', () => {
    const incompleteSubmissions = [
      {
        ...mockSubmissions[0],
        is_completed: false,
      },
    ];

    render(<SubmissionsList {...defaultProps} submissions={incompleteSubmissions} />);

    expect(screen.getByText('Incomplete')).toBeInTheDocument();
  });
});
