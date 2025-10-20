from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Age Range Schema
class AgeRange(BaseModel):
    min: int
    max: Optional[int] = None  # None means no upper limit (e.g., "60+")
    label: str

    @field_validator('min')
    @classmethod
    def validate_min_age(cls, v):
        if v < 0:
            raise ValueError('Minimum age cannot be negative')
        return v

    @field_validator('max')
    @classmethod
    def validate_max_age(cls, v):
        if v is not None and v < 0:
            raise ValueError('Maximum age cannot be negative')
        return v

    def model_post_init(self, __context):
        if self.max is not None and self.max <= self.min:
            raise ValueError('Maximum age must be greater than minimum age')

# Question Display Name Schemas
class QuestionDisplayNameBase(BaseModel):
    question_text: str
    question_id: str
    display_name: Optional[str] = None

class QuestionDisplayNameCreate(QuestionDisplayNameBase):
    pass

class QuestionDisplayNameUpdate(BaseModel):
    display_name: Optional[str] = None

class QuestionDisplayName(QuestionDisplayNameBase):
    id: int
    report_settings_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Report Settings Schemas
class ReportSettingsBase(BaseModel):
    age_ranges: List[AgeRange]

    @field_validator('age_ranges')
    @classmethod
    def validate_age_ranges(cls, v):
        if not v:
            raise ValueError('At least one age range is required')

        # Check for overlapping ranges
        sorted_ranges = sorted(v, key=lambda x: x.min)
        for i in range(len(sorted_ranges) - 1):
            current = sorted_ranges[i]
            next_range = sorted_ranges[i + 1]

            current_max = current.max if current.max is not None else float('inf')
            if current_max > next_range.min:
                raise ValueError(f'Age ranges overlap: {current.label} and {next_range.label}')

        return v

class ReportSettingsCreate(ReportSettingsBase):
    survey_id: int

class ReportSettingsUpdate(BaseModel):
    age_ranges: Optional[List[AgeRange]] = None

class ReportSettings(ReportSettingsBase):
    id: int
    survey_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    question_display_names: List[QuestionDisplayName] = []

    class Config:
        from_attributes = True

# Combined Settings Schema for Frontend
class ReportSettingsWithQuestions(ReportSettings):
    available_questions: List[Dict[str, str]] = []  # Questions from survey flow

# Bulk update schema for question display names
class BulkQuestionDisplayNameUpdate(BaseModel):
    question_updates: List[Dict[str, Union[str, int]]]  # [{"question_id": "q1", "display_name": "Short Name"}, ...]