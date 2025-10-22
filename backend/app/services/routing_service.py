"""
Routing Service Layer
Provides high-level routing operations with proper separation of concerns.
Follows Dependency Inversion Principle.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.survey import SurveyQuestion, SubmissionUpdate
from app.utils.routing_refactored import (
    get_next_question_id,
    build_response_dict,
    RoutingActions
)
from app.crud import survey as survey_crud

logger = logging.getLogger(__name__)


class RoutingService:
    """
    Service layer for survey routing logic.

    Provides a clean abstraction over routing operations,
    handling database access, caching, and business logic.
    """

    def __init__(self, db: Session):
        """
        Initialize routing service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_next_question_for_submission(
        self,
        submission_id: int,
        current_question_id: str
    ) -> Dict[str, Any]:
        """
        Get next question for a submission based on routing logic.

        This method:
        1. Validates submission and question existence
        2. Retrieves survey and responses
        3. Evaluates routing rules
        4. Handles end_survey action (marks as rejected)
        5. Returns routing information with question data

        Args:
            submission_id: ID of the submission
            current_question_id: ID of the current question

        Returns:
            Dictionary with routing information:
            {
                "action": "goto_question" | "end_survey" | "continue",
                "next_question_id": str (if not end_survey),
                "question_index": int (if not end_survey),
                "question": {...} (full question object if not end_survey)
            }

        Raises:
            HTTPException: If submission/survey/question not found or invalid
        """
        # Get submission
        submission = survey_crud.get_submission(self.db, submission_id)
        if not submission:
            logger.warning(f"Submission not found: {submission_id}")
            raise HTTPException(status_code=404, detail="Submission not found")

        # Get survey
        survey = survey_crud.get_survey(self.db, submission.survey_id)
        if not survey:
            logger.error(
                f"Survey not found for submission {submission_id}: "
                f"survey_id={submission.survey_id}"
            )
            raise HTTPException(status_code=404, detail="Survey not found")

        # Parse questions
        try:
            survey_questions = [SurveyQuestion(**q) for q in survey.survey_flow]
        except Exception as e:
            logger.error(f"Failed to parse survey questions for survey {survey.id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Survey structure is invalid"
            )

        # Validate that current_question_id belongs to this survey
        current_question = next(
            (q for q in survey_questions if q.id == current_question_id),
            None
        )

        if not current_question:
            logger.warning(
                f"Invalid question_id '{current_question_id}' for survey {survey.id}. "
                f"Valid IDs: {[q.id for q in survey_questions]}"
            )
            raise HTTPException(
                status_code=400,
                detail="Invalid question ID for this survey"
            )

        # Get responses
        responses = survey_crud.get_responses_by_submission(self.db, submission_id)

        # Build response dictionary (using improved O(n+m) algorithm)
        response_dict = build_response_dict(responses, survey_questions)

        # Get routing information
        routing_info = get_next_question_id(current_question, survey_questions, response_dict)

        # Handle end survey action
        if routing_info["action"] == RoutingActions.END_SURVEY:
            self._mark_submission_rejected(submission_id)
            logger.info(
                f"Submission {submission_id} ended early via routing rule. "
                f"Question: {current_question_id}"
            )
        else:
            # Add full question object
            next_question_index = routing_info["question_index"]
            next_question = survey_questions[next_question_index]
            routing_info["question"] = next_question.dict()

        return routing_info

    def _mark_submission_rejected(self, submission_id: int) -> None:
        """
        Mark submission as rejected when ending early via routing.

        Args:
            submission_id: ID of the submission to reject
        """
        try:
            survey_crud.update_submission(
                self.db,
                submission_id=submission_id,
                submission_data=SubmissionUpdate(
                    is_completed=True,
                    is_approved=False
                )
            )
            logger.info(f"Submission {submission_id} marked as rejected (routing end_survey)")
        except Exception as e:
            logger.error(f"Failed to mark submission {submission_id} as rejected: {e}")
            # Don't raise - rejection is a side effect, routing info should still be returned

    def validate_question_belongs_to_survey(
        self,
        question_id: str,
        survey_questions: list
    ) -> bool:
        """
        Validate that a question ID belongs to a survey.

        Security check to prevent question ID enumeration attacks.

        Args:
            question_id: The question ID to validate
            survey_questions: List of questions in the survey

        Returns:
            True if question belongs to survey, False otherwise
        """
        return any(q.id == question_id for q in survey_questions)
