from datetime import datetime

from pydantic import BaseModel, Field


# Label Mapping schemas
class LabelMappingBase(BaseModel):
    system_label: str = Field(..., description="Low-level system-generated label")


class LabelMappingCreate(LabelMappingBase):
    pass


class LabelMapping(LabelMappingBase):
    id: int
    reporting_label_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Reporting Label schemas
class ReportingLabelBase(BaseModel):
    label_name: str = Field(..., max_length=255, description="High-level reporting label name")
    description: str | None = Field(None, description="Optional description of this label")


class ReportingLabelCreate(ReportingLabelBase):
    survey_id: int
    is_ai_generated: bool = True
    system_labels: list[str] = Field(default_factory=list, description="Initial system labels to map")


class ReportingLabelUpdate(BaseModel):
    label_name: str | None = Field(None, max_length=255)
    description: str | None = None


class ReportingLabel(ReportingLabelBase):
    id: int
    survey_id: int
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime | None
    label_mappings: list[LabelMapping] = []

    class Config:
        from_attributes = True


# Response schemas for frontend
class SystemLabelWithCount(BaseModel):
    """System label with count of submissions using it"""
    label: str
    count: int
    sample_media_ids: list[int] = Field(default_factory=list, description="Sample media IDs for preview")


class TaxonomyOverview(BaseModel):
    """Overview of all labels and mappings for a survey"""
    reporting_labels: list[ReportingLabel]
    unmapped_system_labels: list[SystemLabelWithCount]
    total_media_items: int


class AddSystemLabelRequest(BaseModel):
    """Request to add a system label to a reporting label"""
    system_label: str


class RemoveSystemLabelRequest(BaseModel):
    """Request to remove a system label from a reporting label"""
    system_label: str


class GenerateTaxonomyRequest(BaseModel):
    """Request to generate taxonomy using Gemini"""
    survey_id: int
    max_categories: int = Field(default=6, ge=3, le=10, description="Maximum number of high-level categories")


class MediaPreview(BaseModel):
    """Preview of media with specific label"""
    id: int
    media_type: str
    media_url: str
    thumbnail_url: str | None
    description: str
    submission_id: int
    respondent_info: dict = Field(default_factory=dict)
