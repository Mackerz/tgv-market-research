"""Tests for N+1 query fixes"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.models.survey import Survey, Submission, Response
from app.crud import survey as survey_crud
from app.schemas.survey import SurveyCreate, SubmissionCreate, ResponseCreate


# Query counter for tracking database queries
query_counter = {'count': 0}


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    query_counter['count'] += 1


def reset_query_counter():
    """Reset the query counter"""
    query_counter['count'] = 0


def get_query_count():
    """Get current query count"""
    return query_counter['count']


class TestN1QueryFixes:
    """Tests for N+1 query optimization"""

    @pytest.fixture
    def setup_test_data(self, db_session: Session):
        """Create test survey with submissions and responses"""
        # Create survey
        survey_data = SurveyCreate(
            survey_slug="test-n1-query",
            name="N+1 Query Test Survey",
            survey_flow=[
                {
                    "id": "q1",
                    "question": "Test question?",
                    "question_type": "free_text",
                    "required": True
                }
            ],
            is_active=True
        )
        survey = survey_crud.survey.create(db_session, obj_in=survey_data)

        # Create 5 submissions
        submissions = []
        for i in range(5):
            submission_data = SubmissionCreate(
                survey_id=survey.id,
                email=f"test{i}@company.com",
                phone_number="1234567890",
                region="UK",
                date_of_birth="1990-01-01",
                gender="Male"
            )
            submission = survey_crud.submission.create(db_session, obj_in=submission_data)
            submissions.append(submission)

            # Create 3 responses per submission
            for j in range(3):
                response_data = ResponseCreate(
                    submission_id=submission.id,
                    question=f"Question {j+1}",
                    question_type="free_text",
                    free_text_answer=f"Answer {j+1}"
                )
                survey_crud.response.create(db_session, obj_in=response_data)

        db_session.commit()
        return survey, submissions

    def test_get_multi_by_survey_eager_loads_responses(self, db_session: Session, setup_test_data):
        """Test that get_multi_by_survey eager loads responses"""
        survey, _ = setup_test_data

        reset_query_counter()

        # Get submissions with responses
        submissions = survey_crud.submission.get_multi_by_survey(
            db_session, survey_id=survey.id
        )

        # Access responses to trigger loading
        total_responses = 0
        for submission in submissions:
            total_responses += len(submission.responses)

        query_count = get_query_count()

        # Should only execute 2-3 queries max (1 for submissions, 1 for responses, maybe 1 for transaction)
        # NOT 1 + N queries (N = number of submissions)
        assert query_count <= 3, f"Expected <= 3 queries, got {query_count} (N+1 problem!)"
        assert total_responses == 15  # 5 submissions * 3 responses

    def test_get_multi_by_survey_with_media_eager_loads_all(self, db_session: Session, setup_test_data):
        """Test that get_multi_by_survey_with_media eager loads responses and media"""
        survey, _ = setup_test_data

        reset_query_counter()

        # Get submissions with responses and media
        submissions = survey_crud.submission.get_multi_by_survey_with_media(
            db_session, survey_id=survey.id
        )

        # Access responses and media_analysis to trigger loading
        total_responses = 0
        total_media = 0
        for submission in submissions:
            for response in submission.responses:
                total_responses += 1
                # Access media_analysis (even if empty)
                total_media += len(response.media_analysis)

        query_count = get_query_count()

        # Should only execute 3-4 queries max (1 for submissions, 1 for responses, 1 for media, maybe 1 for transaction)
        # NOT 1 + N + M queries
        assert query_count <= 4, f"Expected <= 4 queries, got {query_count} (N+1 problem!)"
        assert total_responses == 15

    def test_comparison_with_and_without_eager_loading(self, db_session: Session, setup_test_data):
        """Compare query counts with and without eager loading"""
        survey, _ = setup_test_data

        # Test WITHOUT eager loading (naive approach)
        reset_query_counter()
        naive_submissions = db_session.query(Submission).filter(
            Submission.survey_id == survey.id
        ).all()

        # Access responses (triggers N+1)
        for submission in naive_submissions:
            _ = len(submission.responses)

        naive_query_count = get_query_count()

        # Test WITH eager loading
        reset_query_counter()
        optimized_submissions = survey_crud.submission.get_multi_by_survey(
            db_session, survey_id=survey.id
        )

        # Access responses (already loaded)
        for submission in optimized_submissions:
            _ = len(submission.responses)

        optimized_query_count = get_query_count()

        # Optimized should use significantly fewer queries
        # Naive: ~6 queries (1 for submissions + 5 for responses)
        # Optimized: ~2 queries (1 for submissions + 1 for all responses)
        assert optimized_query_count < naive_query_count
        assert optimized_query_count <= 3
        print(f"\nNaive: {naive_query_count} queries, Optimized: {optimized_query_count} queries")
        print(f"Improvement: {naive_query_count / optimized_query_count:.1f}x faster")

    def test_get_multi_by_submission_eager_loads_media(self, db_session: Session, setup_test_data):
        """Test that get_multi_by_submission eager loads media analysis"""
        _, submissions = setup_test_data
        submission = submissions[0]

        reset_query_counter()

        # Get responses with media analysis eager loaded
        responses = survey_crud.response.get_multi_by_submission(
            db_session, submission_id=submission.id
        )

        # Access media_analysis
        for response in responses:
            _ = len(response.media_analysis)

        query_count = get_query_count()

        # Should only execute 2-3 queries max
        assert query_count <= 3, f"Expected <= 3 queries, got {query_count}"


class TestQueryPerformance:
    """Performance benchmarking tests"""

    @pytest.mark.slow
    def test_large_dataset_performance(self, db_session: Session):
        """Test performance with larger dataset (50 submissions)"""
        # Create survey
        survey_data = SurveyCreate(
            survey_slug="perf-test",
            name="Performance Test",
            survey_flow=[{"id": "q1", "question": "Q1?", "question_type": "free_text", "required": True}],
            is_active=True
        )
        survey = survey_crud.survey.create(db_session, obj_in=survey_data)

        # Create 50 submissions with 5 responses each
        for i in range(50):
            submission_data = SubmissionCreate(
                survey_id=survey.id,
                email=f"perf{i}@company.com",
                phone_number="1234567890",
                region="UK",
                date_of_birth="1990-01-01",
                gender="Male"
            )
            submission = survey_crud.submission.create(db_session, obj_in=submission_data)

            for j in range(5):
                response_data = ResponseCreate(
                    submission_id=submission.id,
                    question=f"Q{j}",
                    question_type="free_text",
                    free_text_answer=f"A{j}"
                )
                survey_crud.response.create(db_session, obj_in=response_data)

        db_session.commit()

        # Test query count
        reset_query_counter()
        submissions = survey_crud.submission.get_multi_by_survey_with_media(
            db_session, survey_id=survey.id
        )

        # Access all relationships
        for submission in submissions:
            for response in submission.responses:
                _ = len(response.media_analysis)

        query_count = get_query_count()

        # Even with 50 submissions and 250 responses, should still be ~3-4 queries
        assert query_count <= 5, f"Expected <= 5 queries for large dataset, got {query_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
