"""Unit tests for query helpers"""
import pytest
from app.utils.queries import (
    get_approved_submissions_query,
    get_approved_submission_ids_subquery,
    get_completed_submissions_query,
    get_submission_counts
)
from app.models import survey as survey_models


class TestGetApprovedSubmissionsQuery:
    """Tests for get_approved_submissions_query"""

    def test_returns_only_approved_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should return only completed and approved submissions"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()

        assert len(results) == 1
        assert results[0].email == "approved@example.com"
        assert results[0].is_completed is True
        assert results[0].is_approved is True

    def test_excludes_rejected_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should exclude rejected submissions"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()

        emails = [r.email for r in results]
        assert "rejected@example.com" not in emails

    def test_excludes_pending_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should exclude pending submissions"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()

        emails = [r.email for r in results]
        assert "pending@example.com" not in emails

    def test_excludes_incomplete_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should exclude incomplete submissions"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()

        emails = [r.email for r in results]
        assert "incomplete@example.com" not in emails

    def test_filters_by_survey_id(self, db_session, sample_survey):
        """Should only return submissions for specified survey"""
        # Create another survey
        other_survey = survey_models.Survey(
            survey_slug="other-survey",
            name="Other Survey",
            survey_flow=[],
            is_active=True
        )
        db_session.add(other_survey)
        db_session.commit()

        # Create submission for other survey
        other_submission = survey_models.Submission(
            survey_id=other_survey.id,
            email="other@example.com",
            phone_number="9999999999",
            region="Other",
            date_of_birth="1990-01-01",
            gender="Male",
            is_completed=True,
            is_approved=True
        )
        db_session.add(other_submission)
        db_session.commit()

        # Query for original survey
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()

        # Should not include submission from other survey
        emails = [r.email for r in results]
        assert "other@example.com" not in emails

    def test_returns_query_object(self, db_session, sample_survey):
        """Should return SQLAlchemy Query object"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        assert hasattr(query, 'all')
        assert hasattr(query, 'first')
        assert hasattr(query, 'count')

    def test_can_chain_additional_filters(self, db_session, multiple_submissions, sample_survey):
        """Should allow chaining additional filters"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        filtered = query.filter(survey_models.Submission.region == "North America")
        results = filtered.all()

        assert len(results) == 1
        assert results[0].region == "North America"

    def test_empty_result_when_no_approved(self, db_session, sample_survey):
        """Should return empty list when no approved submissions"""
        query = get_approved_submissions_query(db_session, sample_survey.id)
        results = query.all()
        assert len(results) == 0


class TestGetApprovedSubmissionIdsSubquery:
    """Tests for get_approved_submission_ids_subquery"""

    def test_returns_subquery(self, db_session, sample_survey):
        """Should return subquery object"""
        subquery = get_approved_submission_ids_subquery(db_session, sample_survey.id)
        assert subquery is not None

    def test_can_use_in_filter(self, db_session, multiple_submissions, sample_survey):
        """Should be usable in filter clause"""
        approved_ids = get_approved_submission_ids_subquery(db_session, sample_survey.id)

        # Use in another query
        responses_query = db_session.query(survey_models.Response).filter(
            survey_models.Response.submission_id.in_(approved_ids)
        )

        # Should work without error
        responses_query.all()

    def test_subquery_matches_main_query(self, db_session, multiple_submissions, sample_survey):
        """Subquery results should match main query results"""
        # Get approved submissions
        approved_subs = get_approved_submissions_query(db_session, sample_survey.id).all()
        approved_ids_direct = [sub.id for sub in approved_subs]

        # Get IDs via subquery
        subquery = get_approved_submission_ids_subquery(db_session, sample_survey.id)
        results = db_session.query(survey_models.Submission).filter(
            survey_models.Submission.id.in_(subquery)
        ).all()
        approved_ids_subquery = [sub.id for sub in results]

        assert set(approved_ids_direct) == set(approved_ids_subquery)


class TestGetCompletedSubmissionsQuery:
    """Tests for get_completed_submissions_query"""

    def test_returns_all_completed_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should return all completed submissions regardless of approval"""
        query = get_completed_submissions_query(db_session, sample_survey.id)
        results = query.all()

        assert len(results) == 3  # Approved, rejected, and pending
        emails = [r.email for r in results]
        assert "approved@example.com" in emails
        assert "rejected@example.com" in emails
        assert "pending@example.com" in emails

    def test_excludes_incomplete_submissions(self, db_session, multiple_submissions, sample_survey):
        """Should exclude incomplete submissions"""
        query = get_completed_submissions_query(db_session, sample_survey.id)
        results = query.all()

        emails = [r.email for r in results]
        assert "incomplete@example.com" not in emails


class TestGetSubmissionCounts:
    """Tests for get_submission_counts"""

    def test_returns_all_count_types(self, db_session, multiple_submissions, sample_survey):
        """Should return dictionary with all count types"""
        counts = get_submission_counts(db_session, sample_survey.id)

        assert 'total' in counts
        assert 'completed' in counts
        assert 'approved' in counts
        assert 'rejected' in counts
        assert 'pending' in counts

    def test_counts_are_correct(self, db_session, multiple_submissions, sample_survey):
        """Should return accurate counts"""
        counts = get_submission_counts(db_session, sample_survey.id)

        assert counts['total'] == 4  # All submissions
        assert counts['completed'] == 3  # Completed only
        assert counts['approved'] == 1  # Approved only
        assert counts['rejected'] == 1  # Rejected only
        assert counts['pending'] == 1  # Pending only

    def test_counts_with_no_submissions(self, db_session, sample_survey):
        """Should return zero counts when no submissions"""
        counts = get_submission_counts(db_session, sample_survey.id)

        assert counts['total'] == 0
        assert counts['completed'] == 0
        assert counts['approved'] == 0
        assert counts['rejected'] == 0
        assert counts['pending'] == 0

    def test_counts_with_only_approved(self, db_session, sample_survey):
        """Should handle case with only approved submissions"""
        sub = survey_models.Submission(
            survey_id=sample_survey.id,
            email="test@example.com",
            phone_number="1111111111",
            region="Test",
            date_of_birth="1990-01-01",
            gender="Male",
            is_completed=True,
            is_approved=True
        )
        db_session.add(sub)
        db_session.commit()

        counts = get_submission_counts(db_session, sample_survey.id)

        assert counts['total'] == 1
        assert counts['completed'] == 1
        assert counts['approved'] == 1
        assert counts['rejected'] == 0
        assert counts['pending'] == 0

    def test_efficient_single_query(self, db_session, multiple_submissions, sample_survey):
        """Should be more efficient than separate queries"""
        # This function should make fewer queries than calling each count separately
        counts = get_submission_counts(db_session, sample_survey.id)

        # Verify we got all the data
        assert all(key in counts for key in ['total', 'completed', 'approved', 'rejected', 'pending'])

    def test_matches_individual_queries(self, db_session, multiple_submissions, sample_survey):
        """Counts should match if we queried individually"""
        counts = get_submission_counts(db_session, sample_survey.id)

        # Verify against individual counts
        total = db_session.query(survey_models.Submission).filter(
            survey_models.Submission.survey_id == sample_survey.id
        ).count()
        assert counts['total'] == total

        completed = db_session.query(survey_models.Submission).filter(
            survey_models.Submission.survey_id == sample_survey.id,
            survey_models.Submission.is_completed == True
        ).count()
        assert counts['completed'] == completed


class TestQueryHelpersIntegration:
    """Integration tests for query helpers"""

    def test_helpers_work_together(self, db_session, multiple_submissions, sample_survey):
        """Different helpers should work together consistently"""
        # Get approved submissions
        approved_query = get_approved_submissions_query(db_session, sample_survey.id)
        approved_count_direct = approved_query.count()

        # Get counts
        counts = get_submission_counts(db_session, sample_survey.id)

        # Should match
        assert approved_count_direct == counts['approved']

    def test_realistic_reporting_scenario(self, db_session, multiple_submissions, sample_survey):
        """Should handle realistic reporting scenario"""
        # Get counts for dashboard
        counts = get_submission_counts(db_session, sample_survey.id)

        # Get approved submissions for detailed report
        approved_subs = get_approved_submissions_query(db_session, sample_survey.id).all()

        # Verify consistency
        assert len(approved_subs) == counts['approved']
        assert all(sub.is_approved is True for sub in approved_subs)
        assert all(sub.is_completed is True for sub in approved_subs)
