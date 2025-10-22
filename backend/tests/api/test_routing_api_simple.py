"""
Simplified integration tests for survey routing API endpoints.
Tests the /next-question endpoint and auto-rejection on end_survey.
"""
import pytest
from fastapi.testclient import TestClient
from app.models.survey import Survey, Submission, Response


@pytest.fixture
def routing_survey(db_session):
    """Create a survey with routing rules for testing"""
    survey = Survey(
        survey_slug="routing-test",
        name="Routing Test Survey",
        survey_flow=[
            {
                "id": "q1",
                "question": "How often do you use the product?",
                "question_type": "single",
                "required": True,
                "options": ["Daily", "Weekly", "Rarely"],
                "routing_rules": [
                    {
                        "conditions": [
                            {
                                "question_id": "q1",
                                "operator": "equals",
                                "value": "Rarely"
                            }
                        ],
                        "action": "end_survey"
                    }
                ]
            },
            {
                "id": "q2",
                "question": "How satisfied are you?",
                "question_type": "single",
                "required": True,
                "options": ["Very", "Somewhat", "Not"]
            }
        ],
        is_active=True
    )
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    return survey


@pytest.fixture
def routing_submission(db_session, routing_survey):
    """Create a submission for the routing survey"""
    submission = Submission(
        survey_id=routing_survey.id,
        email="test@routing.com",
        phone_number="1234567890",
        region="US",
        date_of_birth="1990-01-01",
        gender="Male",
        is_completed=False,
        is_approved=None
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission


class TestRoutingAPI:
    """Test routing API endpoints"""

    def test_sequential_navigation(self, client, db_session, routing_survey, routing_submission):
        """Test normal sequential navigation without triggering routing"""
        # Add response that doesn't trigger routing
        response = Response(
            submission_id=routing_submission.id,
            question="How often do you use the product?",
            question_type="single",
            single_answer="Daily"
        )
        db_session.add(response)
        db_session.commit()

        # Get next question
        response = client.get(
            f"/api/submissions/{routing_submission.id}/next-question",
            params={"current_question_id": "q1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["next_question_id"] == "q2"
        assert data["question_index"] == 1

    def test_end_survey_with_rejection(self, client, db_session, routing_survey, routing_submission):
        """Test that end_survey automatically rejects submission"""
        # Add response that triggers end_survey
        response = Response(
            submission_id=routing_submission.id,
            question="How often do you use the product?",
            question_type="single",
            single_answer="Rarely"
        )
        db_session.add(response)
        db_session.commit()

        # Get next question
        response = client.get(
            f"/api/submissions/{routing_submission.id}/next-question",
            params={"current_question_id": "q1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "end_survey"
        assert data["next_question_id"] is None

        # Verify rejection
        db_session.refresh(routing_submission)
        assert routing_submission.is_completed is True
        assert routing_submission.is_approved is False

    def test_invalid_submission_id(self, client):
        """Test with non-existent submission"""
        response = client.get(
            "/api/submissions/99999/next-question",
            params={"current_question_id": "q1"}
        )

        assert response.status_code == 404

    def test_invalid_question_id(self, client, routing_submission):
        """Test with invalid question ID"""
        response = client.get(
            f"/api/submissions/{routing_submission.id}/next-question",
            params={"current_question_id": "invalid_id"}
        )

        assert response.status_code == 404


class TestSkipLogic:
    """Test skip logic (goto_question action)"""

    def test_goto_question(self, client, db_session):
        """Test jumping to a specific question"""
        # Create survey with skip logic
        survey = Survey(
            survey_slug="skip-test",
            name="Skip Logic Test",
            survey_flow=[
                {
                    "id": "q1",
                    "question": "Do you have children?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Yes", "No"],
                    "routing_rules": [
                        {
                            "conditions": [
                                {"question_id": "q1", "operator": "equals", "value": "No"}
                            ],
                            "action": "goto_question",
                            "target_question_id": "q4"
                        }
                    ]
                },
                {
                    "id": "q2",
                    "question": "Children ages?",
                    "question_type": "multi",
                    "required": True,
                    "options": ["0-5", "6-12"]
                },
                {
                    "id": "q3",
                    "question": "Children activities?",
                    "question_type": "free_text",
                    "required": True
                },
                {
                    "id": "q4",
                    "question": "Employment?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Yes", "No"]
                }
            ],
            is_active=True
        )
        db_session.add(survey)
        db_session.commit()
        db_session.refresh(survey)

        # Create submission
        submission = Submission(
            survey_id=survey.id,
            email="skip@test.com",
            phone_number="5555555555",
            region="UK",
            date_of_birth="1985-01-01",
            gender="Female",
            is_completed=False,
            is_approved=None
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        # Add response that triggers skip
        response = Response(
            submission_id=submission.id,
            question="Do you have children?",
            question_type="single",
            single_answer="No"
        )
        db_session.add(response)
        db_session.commit()

        # Get next question
        response = client.get(
            f"/api/submissions/{submission.id}/next-question",
            params={"current_question_id": "q1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "goto_question"
        assert data["next_question_id"] == "q4"
        assert data["question_index"] == 3


class TestMultiChoiceRouting:
    """Test routing with multi-choice questions"""

    def test_contains_operator(self, client, db_session):
        """Test routing with contains operator on multi-choice"""
        survey = Survey(
            survey_slug="multi-test",
            name="Multi-Choice Test",
            survey_flow=[
                {
                    "id": "q1",
                    "question": "Which products?",
                    "question_type": "multi",
                    "required": True,
                    "options": ["A", "B", "C", "None"],
                    "routing_rules": [
                        {
                            "conditions": [
                                {"question_id": "q1", "operator": "contains", "value": "None"}
                            ],
                            "action": "end_survey"
                        }
                    ]
                },
                {
                    "id": "q2",
                    "question": "Satisfaction?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Yes", "No"]
                }
            ],
            is_active=True
        )
        db_session.add(survey)
        db_session.commit()
        db_session.refresh(survey)

        submission = Submission(
            survey_id=survey.id,
            email="multi@test.com",
            phone_number="9999999999",
            region="US",
            date_of_birth="1990-01-01",
            gender="Male",
            is_completed=False,
            is_approved=None
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        # Select "None" which should end survey
        response = Response(
            submission_id=submission.id,
            question="Which products?",
            question_type="multi",
            multiple_choice_answer=["A", "None"]
        )
        db_session.add(response)
        db_session.commit()

        response = client.get(
            f"/api/submissions/{submission.id}/next-question",
            params={"current_question_id": "q1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "end_survey"

        # Verify rejection
        db_session.refresh(submission)
        assert submission.is_approved is False
        assert submission.is_completed is True
