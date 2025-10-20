"""Unit tests for FastAPI dependencies"""
import pytest
from fastapi import HTTPException
from app.dependencies import
from app.crud import survey as survey_crud


class TestGetSurveyOr404:
    """Tests for get_survey_or_404 dependency"""

    def test_returns_survey_when_found(self, db_session, sample_survey):
        """Should return survey when it exists"""
        survey = get_survey_or_404(sample_survey.survey_slug, db_session)

        assert survey is not None
        assert survey.id == sample_survey.id
        assert survey.survey_slug == sample_survey.survey_slug

    def test_raises_404_when_not_found(self, db_session):
        """Should raise HTTPException 404 when survey not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_survey_or_404("nonexistent-survey", db_session)

        assert exc_info.value.status_code == 404
        assert "Survey not found" in str(exc_info.value.detail)

    def test_returns_correct_survey_by_slug(self, db_session, sample_survey):
        """Should return correct survey matching slug"""
        # Create another survey
from app.models import survey as survey_models
        other_survey = survey_models.Survey(
            survey_slug="other-survey-456",
            name="Other Survey",
            survey_flow=[],
            is_active=True
        )
        db_session.add(other_survey)
        db_session.commit()

        # Get specific survey
        survey = get_survey_or_404(sample_survey.survey_slug, db_session)

        assert survey.id == sample_survey.id
        assert survey.survey_slug == sample_survey.survey_slug

    def test_works_with_inactive_survey(self, db_session):
        """Should return inactive surveys (doesn't filter by active status)"""
from app.models import survey as survey_models
        inactive_survey = survey_models.Survey(
            survey_slug="inactive-survey",
            name="Inactive Survey",
            survey_flow=[],
            is_active=False
        )
        db_session.add(inactive_survey)
        db_session.commit()

        survey = get_survey_or_404("inactive-survey", db_session)
        assert survey is not None
        assert survey.is_active is False


class TestGetSubmissionOr404:
    """Tests for get_submission_or_404 dependency"""

    def test_returns_submission_when_found(self, db_session, sample_submission):
        """Should return submission when it exists"""
        submission = get_submission_or_404(sample_submission.id, db_session)

        assert submission is not None
        assert submission.id == sample_submission.id
        assert submission.email == sample_submission.email

    def test_raises_404_when_not_found(self, db_session):
        """Should raise HTTPException 404 when submission not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_submission_or_404(99999, db_session)

        assert exc_info.value.status_code == 404
        assert "Submission not found" in str(exc_info.value.detail)

    def test_returns_correct_submission_by_id(self, db_session, multiple_submissions):
        """Should return correct submission matching ID"""
        target_submission = multiple_submissions[0]

        submission = get_submission_or_404(target_submission.id, db_session)

        assert submission.id == target_submission.id
        assert submission.email == target_submission.email

    def test_works_with_incomplete_submission(self, db_session, multiple_submissions):
        """Should return incomplete submissions (doesn't filter by completion status)"""
        # The 4th submission is incomplete
        incomplete_sub = multiple_submissions[3]

        submission = get_submission_or_404(incomplete_sub.id, db_session)
        assert submission is not None
        assert submission.is_completed is False


class TestGetResponseOr404:
    """Tests for get_response_or_404 dependency"""

    def test_returns_response_when_found(self, db_session, sample_response):
        """Should return response when it exists"""
        response = get_response_or_404(sample_response.id, db_session)

        assert response is not None
        assert response.id == sample_response.id
        assert response.question == sample_response.question

    def test_raises_404_when_not_found(self, db_session):
        """Should raise HTTPException 404 when response not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_response_or_404(99999, db_session)

        assert exc_info.value.status_code == 404
        assert "Response not found" in str(exc_info.value.detail)

    def test_returns_correct_response_by_id(self, db_session, sample_response):
        """Should return correct response matching ID"""
        # Create another response
from app.models import survey as survey_models
        other_response = survey_models.Response(
            submission_id=sample_response.submission_id,
            question="Another question?",
            question_type="single",
            single_answer="Another answer"
        )
        db_session.add(other_response)
        db_session.commit()

        # Get specific response
        response = get_response_or_404(sample_response.id, db_session)

        assert response.id == sample_response.id
        assert response.question == sample_response.question


class TestDependenciesIntegration:
    """Integration tests for dependencies working together"""

    def test_dependencies_chain(self, db_session, sample_survey, sample_submission, sample_response):
        """Should work when chaining dependency lookups"""
        # Get survey
        survey = get_survey_or_404(sample_survey.survey_slug, db_session)

        # Get submission for that survey
        submission = get_submission_or_404(sample_submission.id, db_session)
        assert submission.survey_id == survey.id

        # Get response for that submission
        response = get_response_or_404(sample_response.id, db_session)
        assert response.submission_id == submission.id

    def test_realistic_endpoint_scenario(self, db_session, sample_survey, sample_submission):
        """Should simulate realistic endpoint usage"""
        # Endpoint: /api/reports/{survey_slug}/submissions/{submission_id}

        # Step 1: Validate survey exists
        survey = get_survey_or_404(sample_survey.survey_slug, db_session)

        # Step 2: Validate submission exists
        submission = get_submission_or_404(sample_submission.id, db_session)

        # Step 3: Verify submission belongs to survey
        assert submission.survey_id == survey.id

    def test_error_handling_in_chain(self, db_session, sample_survey):
        """Should properly handle errors in dependency chain"""
        # Survey exists
        survey = get_survey_or_404(sample_survey.survey_slug, db_session)
        assert survey is not None

        # But submission doesn't exist
        with pytest.raises(HTTPException) as exc_info:
            get_submission_or_404(99999, db_session)

        assert exc_info.value.status_code == 404

    def test_multiple_sequential_lookups(self, db_session, multiple_submissions):
        """Should handle multiple sequential lookups efficiently"""
        # Look up multiple submissions
        for submission in multiple_submissions:
            retrieved = get_submission_or_404(submission.id, db_session)
            assert retrieved.id == submission.id

    def test_dependency_doesnt_cache(self, db_session, sample_survey):
        """Dependencies should fetch fresh data each time"""
        # First call
        survey1 = get_survey_or_404(sample_survey.survey_slug, db_session)

        # Update survey
        survey1.name = "Updated Name"
        db_session.commit()

        # Second call should get updated data
        survey2 = get_survey_or_404(sample_survey.survey_slug, db_session)
        assert survey2.name == "Updated Name"


class TestDependencyErrorMessages:
    """Tests for clear error messages"""

    def test_survey_not_found_message(self, db_session):
        """Should provide clear error message for survey not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_survey_or_404("missing-survey", db_session)

        assert "Survey not found" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 404

    def test_submission_not_found_message(self, db_session):
        """Should provide clear error message for submission not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_submission_or_404(12345, db_session)

        assert "Submission not found" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 404

    def test_response_not_found_message(self, db_session):
        """Should provide clear error message for response not found"""
        with pytest.raises(HTTPException) as exc_info:
            get_response_or_404(67890, db_session)

        assert "Response not found" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 404
