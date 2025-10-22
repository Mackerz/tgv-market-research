"""
Integration tests for survey routing API endpoints.
Tests the /next-question endpoint and auto-rejection on end_survey.
"""
import pytest
from fastapi.testclient import TestClient
from app.models.survey import Survey, Submission, Response


@pytest.fixture
def sample_survey_with_routing(db_session):
    """Create a survey with routing rules"""
    survey = Survey(
        survey_slug="routing-test-survey",
        name="Routing Test Survey",
        survey_flow=[
            {
                "id": "q1_screening",
                "question": "How often do you use the product?",
                "question_type": "single",
                "required": True,
                "options": ["Daily", "Weekly", "Monthly", "Rarely"],
                "routing_rules": [
                    {
                        "conditions": [
                            {
                                "question_id": "q1_screening",
                                "operator": "equals",
                                "value": "Rarely"
                            }
                        ],
                        "action": "end_survey"
                    }
                ]
            },
            {
                "id": "q2_satisfaction",
                "question": "How satisfied are you?",
                "question_type": "single",
                "required": True,
                "options": ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied"]
            },
            {
                "id": "q3_features",
                "question": "Which features do you use?",
                "question_type": "multi",
                "required": True,
                "options": ["Feature A", "Feature B", "Feature C"]
            }
        ],
        is_active=True
    )
    db_session.add(survey)
    db_session.commit()
    db_session.refresh(survey)
    return survey


@pytest.fixture
def sample_submission_with_routing(db_session, sample_survey_with_routing):
    """Create a submission for routing test survey"""
    submission = Submission(
        survey_id=sample_survey_with_routing.id,
        email="routing_test@example.com",
        phone_number="9876543210",
        region="US",
        date_of_birth="1990-05-15",
        gender="Male",
        is_completed=False,
        is_approved=None
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission


class TestNextQuestionEndpoint:
    """Test the /next-question endpoint"""

    def test_next_question_sequential_no_routing(self, client, db_session, sample_survey_with_routing, sample_submission_with_routing):
        """Test sequential navigation when no routing rules match"""
        # Create response for first question (not triggering routing rule)
        response = Response(
            submission_id=sample_submission_with_routing.id,
            question="How often do you use the product?",
            question_type="single",
            single_answer="Daily"
        )
        db_session.add(response)
        db_session.commit()

        # Call next-question endpoint
        response = client.get(
            f"/api/submissions/{sample_submission_with_routing.id}/next-question",
            params={"current_question_id": "q1_screening"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should continue to next question
        assert data["action"] in ["continue", "goto_question"]
        assert data["next_question_id"] == "q2_satisfaction"
        assert data["question_index"] == 1
        assert "question" in data

    def test_next_question_end_survey_with_rejection(self, db_session, sample_survey_with_routing, sample_submission_with_routing):
        """Test end_survey action with automatic rejection"""
        # Create response that triggers end_survey routing rule
        response = Response(
            submission_id=sample_submission_with_routing.id,
            question="How often do you use the product?",
            question_type="single",
            single_answer="Rarely"  # This triggers end_survey
        )
        db_session.add(response)
        db_session.commit()

        # Override get_db dependency
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        # Call next-question endpoint
        response = client.get(
            f"/api/submissions/{sample_submission_with_routing.id}/next-question",
            params={"current_question_id": "q1_screening"}
        )

        # Clean up override
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        # Should end survey
        assert data["action"] == "end_survey"
        assert data["next_question_id"] is None
        assert data["question_index"] is None

        # Verify submission was marked as rejected
        db_session.refresh(sample_submission_with_routing)
        assert sample_submission_with_routing.is_completed is True
        assert sample_submission_with_routing.is_approved is False

    def test_next_question_goto_question_action(self, db_session):
        """Test goto_question routing action"""
        # Create survey with skip logic
        survey = Survey(
            survey_slug="skip-logic-test",
            name="Skip Logic Test",
            survey_flow=[
                {
                    "id": "q1_has_children",
                    "question": "Do you have children?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Yes", "No"],
                    "routing_rules": [
                        {
                            "conditions": [
                                {
                                    "question_id": "q1_has_children",
                                    "operator": "equals",
                                    "value": "No"
                                }
                            ],
                            "action": "goto_question",
                            "target_question_id": "q4_employment"
                        }
                    ]
                },
                {
                    "id": "q2_children_ages",
                    "question": "What are their ages?",
                    "question_type": "multi",
                    "required": True,
                    "options": ["0-5", "6-12", "13-18"]
                },
                {
                    "id": "q3_children_activities",
                    "question": "What activities do they enjoy?",
                    "question_type": "free_text",
                    "required": True
                },
                {
                    "id": "q4_employment",
                    "question": "Are you employed?",
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
            email="skip_test@example.com",
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

        # Create response that triggers skip
        response = Response(
            submission_id=submission.id,
            question="Do you have children?",
            question_type="single",
            single_answer="No"
        )
        db_session.add(response)
        db_session.commit()

        # Override get_db dependency
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        # Call next-question endpoint
        response = client.get(
            f"/api/submissions/{submission.id}/next-question",
            params={"current_question_id": "q1_has_children"}
        )

        # Clean up override
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        # Should skip to q4
        assert data["action"] == "goto_question"
        assert data["next_question_id"] == "q4_employment"
        assert data["question_index"] == 3

    def test_next_question_invalid_submission(self, db_session):
        """Test next-question with invalid submission ID"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        response = client.get(
            "/api/submissions/99999/next-question",
            params={"current_question_id": "q1"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 404

    def test_next_question_invalid_question_id(self, db_session, sample_survey_with_routing, sample_submission_with_routing):
        """Test next-question with invalid question ID"""
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        response = client.get(
            f"/api/submissions/{sample_submission_with_routing.id}/next-question",
            params={"current_question_id": "invalid_question_id"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 404


class TestRoutingWithMultipleConditions:
    """Test routing with multiple conditions (AND logic)"""

    def test_multiple_conditions_all_match(self, db_session):
        """Test routing when all conditions match"""
        # Create survey with multiple conditions
        survey = Survey(
            survey_slug="multi-condition-test",
            name="Multi-Condition Test",
            survey_flow=[
                {
                    "id": "q1_age",
                    "question": "How old are you?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Under 18", "18-34", "35-54", "55+"]
                },
                {
                    "id": "q2_region",
                    "question": "Where do you live?",
                    "question_type": "single",
                    "required": True,
                    "options": ["US", "UK", "Other"],
                    "routing_rules": [
                        {
                            "conditions": [
                                {
                                    "question_id": "q1_age",
                                    "operator": "equals",
                                    "value": "Under 18"
                                },
                                {
                                    "question_id": "q2_region",
                                    "operator": "not_equals",
                                    "value": "US"
                                }
                            ],
                            "action": "end_survey"
                        }
                    ]
                },
                {
                    "id": "q3_final",
                    "question": "Final question",
                    "question_type": "single",
                    "required": True,
                    "options": ["A", "B"]
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
            email="multi_cond@example.com",
            phone_number="1234567890",
            region="UK",
            date_of_birth="2010-01-01",
            gender="Male",
            is_completed=False,
            is_approved=None
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        # Create responses that match all conditions
        response1 = Response(
            submission_id=submission.id,
            question="How old are you?",
            question_type="single",
            single_answer="Under 18"
        )
        response2 = Response(
            submission_id=submission.id,
            question="Where do you live?",
            question_type="single",
            single_answer="UK"  # Not US
        )
        db_session.add(response1)
        db_session.add(response2)
        db_session.commit()

        # Override get_db dependency
        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        # Call next-question endpoint
        response = client.get(
            f"/api/submissions/{submission.id}/next-question",
            params={"current_question_id": "q2_region"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        # Both conditions match - should end survey
        assert data["action"] == "end_survey"

        # Verify rejection
        db_session.refresh(submission)
        assert submission.is_approved is False


class TestRoutingWithMultiChoice:
    """Test routing with multi-choice questions"""

    def test_contains_operator_with_multi_choice(self, db_session):
        """Test routing with contains operator on multi-choice"""
        survey = Survey(
            survey_slug="multi-choice-routing",
            name="Multi-Choice Routing",
            survey_flow=[
                {
                    "id": "q1_products",
                    "question": "Which products do you use?",
                    "question_type": "multi",
                    "required": True,
                    "options": ["Product A", "Product B", "Product C", "None"],
                    "routing_rules": [
                        {
                            "conditions": [
                                {
                                    "question_id": "q1_products",
                                    "operator": "contains",
                                    "value": "None"
                                }
                            ],
                            "action": "end_survey"
                        }
                    ]
                },
                {
                    "id": "q2_satisfaction",
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

        submission = Submission(
            survey_id=survey.id,
            email="multi_choice@example.com",
            phone_number="9999999999",
            region="US",
            date_of_birth="1990-01-01",
            gender="Female",
            is_completed=False,
            is_approved=None
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        # Select "None" along with other options
        response = Response(
            submission_id=submission.id,
            question="Which products do you use?",
            question_type="multi",
            multiple_choice_answer=["Product A", "None"]
        )
        db_session.add(response)
        db_session.commit()

        def override_get_db():
            try:
                yield db_session
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db

        response = client.get(
            f"/api/submissions/{submission.id}/next-question",
            params={"current_question_id": "q1_products"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()

        # Should end survey because "None" was selected
        assert data["action"] == "end_survey"

        # Verify rejection
        db_session.refresh(submission)
        assert submission.is_approved is False
        assert submission.is_completed is True
