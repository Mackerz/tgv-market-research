import json

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.media import Media
from app.models.survey import Response
from app.models.taxonomy import LabelMapping, ReportingLabel
from app.schemas.taxonomy import ReportingLabelCreate, ReportingLabelUpdate, SystemLabelWithCount


class ReportingLabelCRUD:
    """CRUD operations for ReportingLabel"""

    def __init__(self, db: Session):
        self.db = db

    def get(self, reporting_label_id: int) -> ReportingLabel | None:
        """Get a reporting label by ID"""
        return (
            self.db.query(ReportingLabel)
            .options(joinedload(ReportingLabel.label_mappings))
            .filter(ReportingLabel.id == reporting_label_id)
            .first()
        )

    def get_by_survey(self, survey_id: int) -> list[ReportingLabel]:
        """Get all reporting labels for a survey"""
        return (
            self.db.query(ReportingLabel)
            .options(joinedload(ReportingLabel.label_mappings))
            .filter(ReportingLabel.survey_id == survey_id)
            .order_by(ReportingLabel.label_name)
            .all()
        )

    def create(self, label_data: ReportingLabelCreate) -> ReportingLabel:
        """Create a new reporting label with system label mappings"""
        # Create the reporting label
        db_label = ReportingLabel(
            survey_id=label_data.survey_id,
            label_name=label_data.label_name,
            description=label_data.description,
            is_ai_generated=label_data.is_ai_generated,
        )
        self.db.add(db_label)
        self.db.flush()  # Flush to get the ID

        # Create mappings for system labels
        for system_label in label_data.system_labels:
            mapping = LabelMapping(
                reporting_label_id=db_label.id,
                system_label=system_label,
            )
            self.db.add(mapping)

        self.db.commit()
        self.db.refresh(db_label)
        return db_label

    def update(
        self, reporting_label_id: int, label_data: ReportingLabelUpdate
    ) -> ReportingLabel | None:
        """Update a reporting label"""
        db_label = self.get(reporting_label_id)
        if not db_label:
            return None

        if label_data.label_name is not None:
            db_label.label_name = label_data.label_name
        if label_data.description is not None:
            db_label.description = label_data.description

        self.db.commit()
        self.db.refresh(db_label)
        return db_label

    def delete(self, reporting_label_id: int) -> bool:
        """Delete a reporting label (only if it has no mappings)"""
        db_label = self.get(reporting_label_id)
        if not db_label:
            return False

        # Check if there are any mappings
        if db_label.label_mappings:
            return False

        self.db.delete(db_label)
        self.db.commit()
        return True

    def add_system_label(self, reporting_label_id: int, system_label: str) -> bool:
        """Add a system label mapping to a reporting label"""
        # Check if label exists
        db_label = self.get(reporting_label_id)
        if not db_label:
            return False

        # Check if mapping already exists
        existing = (
            self.db.query(LabelMapping)
            .filter(
                and_(
                    LabelMapping.reporting_label_id == reporting_label_id,
                    LabelMapping.system_label == system_label,
                )
            )
            .first()
        )
        if existing:
            return True  # Already exists, consider success

        # Remove this system label from any other reporting label
        self.db.query(LabelMapping).filter(
            LabelMapping.system_label == system_label
        ).delete()

        # Add new mapping
        mapping = LabelMapping(
            reporting_label_id=reporting_label_id,
            system_label=system_label,
        )
        self.db.add(mapping)
        self.db.commit()
        return True

    def remove_system_label(self, reporting_label_id: int, system_label: str) -> bool:
        """Remove a system label mapping from a reporting label"""
        deleted = (
            self.db.query(LabelMapping)
            .filter(
                and_(
                    LabelMapping.reporting_label_id == reporting_label_id,
                    LabelMapping.system_label == system_label,
                )
            )
            .delete()
        )
        self.db.commit()
        return deleted > 0

    def get_unmapped_system_labels(self, survey_id: int) -> list[SystemLabelWithCount]:
        """Get all system labels that are not mapped to any reporting label"""
        # Get all mapped system labels
        mapped_labels = (
            self.db.query(LabelMapping.system_label)
            .join(ReportingLabel)
            .filter(ReportingLabel.survey_id == survey_id)
            .all()
        )
        mapped_label_set = {label[0] for label in mapped_labels}

        # Get all media for this survey
        media_items = (
            self.db.query(Media)
            .join(Response)
            .join(Response.submission)
            .filter(Response.submission.has(survey_id=survey_id))
            .all()
        )

        # Count occurrences of each system label
        label_counts: dict[str, dict] = {}
        for media in media_items:
            if media.reporting_labels:
                try:
                    labels = json.loads(media.reporting_labels)
                    for label in labels:
                        if label not in mapped_label_set:
                            if label not in label_counts:
                                label_counts[label] = {
                                    "count": 0,
                                    "media_ids": [],
                                }
                            label_counts[label]["count"] += 1
                            if len(label_counts[label]["media_ids"]) < 5:
                                label_counts[label]["media_ids"].append(media.id)
                except json.JSONDecodeError:
                    continue

        # Convert to list of SystemLabelWithCount
        result = [
            SystemLabelWithCount(
                label=label,
                count=data["count"],
                sample_media_ids=data["media_ids"],
            )
            for label, data in label_counts.items()
        ]

        # Sort by count descending
        result.sort(key=lambda x: x.count, reverse=True)
        return result

    def get_media_by_system_label(
        self, survey_id: int, system_label: str, limit: int = 10
    ) -> list[Media]:
        """Get media items that have a specific system label with eager loading"""
        media_items = (
            self.db.query(Media)
            .join(Response)
            .join(Response.submission)
            .options(
                joinedload(Media.response).joinedload(Response.submission)
            )
            .filter(
                and_(
                    Response.submission.has(survey_id=survey_id),
                    Media.reporting_labels.contains(f'"{system_label}"'),
                )
            )
            .limit(limit)
            .all()
        )
        return media_items


def get_reporting_label_crud(db: Session) -> ReportingLabelCRUD:
    """Factory function to get CRUD instance"""
    return ReportingLabelCRUD(db)
