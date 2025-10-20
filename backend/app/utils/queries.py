"""Reusable database query helpers to follow DRY principle"""
from sqlalchemy import and_
from sqlalchemy.orm import Query, Session

from app.models import survey


def get_approved_submissions_query(db: Session, survey_id: int) -> Query:
    """
    Reusable query for completed and approved submissions

    This helper eliminates code duplication across reporting and analytics functions.

    Args:
        db: Database session
        survey_id: Survey ID to filter by

    Returns:
        SQLAlchemy Query object for approved submissions
    """
    return db.query(survey.Submission).filter(
        and_(
            survey.Submission.survey_id == survey_id,
            survey.Submission.is_completed == True,
            survey.Submission.is_approved == True
        )
    )


def get_approved_submission_ids_subquery(db: Session, survey_id: int):
    """
    Reusable subquery for approved submission IDs

    Used in joins and filters where only submission IDs are needed.

    Args:
        db: Database session
        survey_id: Survey ID to filter by

    Returns:
        SQLAlchemy subquery
    """
    return get_approved_submissions_query(db, survey_id).with_entities(
        survey.Submission.id
    ).subquery()


def get_completed_submissions_query(db: Session, survey_id: int) -> Query:
    """
    Query for all completed submissions (regardless of approval status)

    Args:
        db: Database session
        survey_id: Survey ID to filter by

    Returns:
        SQLAlchemy Query object
    """
    return db.query(survey.Submission).filter(
        and_(
            survey.Submission.survey_id == survey_id,
            survey.Submission.is_completed == True
        )
    )


def get_submission_counts(db: Session, survey_id: int) -> dict:
    """
    Get all submission counts for a survey in one query

    Returns counts for total, completed, approved, rejected, and pending submissions.

    Args:
        db: Database session
        survey_id: Survey ID

    Returns:
        Dictionary with count keys: total, completed, approved, rejected, pending
    """
    base_query = db.query(survey.Submission).filter(
        survey.Submission.survey_id == survey_id
    )

    completed_query = base_query.filter(
        survey.Submission.is_completed == True
    )

    return {
        'total': base_query.count(),
        'completed': completed_query.count(),
        'approved': completed_query.filter(
            survey.Submission.is_approved == True
        ).count(),
        'rejected': completed_query.filter(
            survey.Submission.is_approved == False
        ).count(),
        'pending': completed_query.filter(
            survey.Submission.is_approved.is_(None)
        ).count()
    }
