from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enums for validation
class QuestionType(str, Enum):
    FREE_TEXT = "free_text"
    SINGLE = "single"
    MULTI = "multi"
    PHOTO = "photo"
    VIDEO = "video"

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    PREFER_NOT_TO_SAY = "I'd rather not say"

class Region(str, Enum):
    UK = "UK"
    US = "US"
    CA = "CA"  # Canada
    AU = "AU"  # Australia
    DE = "DE"  # Germany
    FR = "FR"  # France
    ES = "ES"  # Spain
    IT = "IT"  # Italy
    NL = "NL"  # Netherlands
    SE = "SE"  # Sweden
    NO = "NO"  # Norway
    DK = "DK"  # Denmark
    FI = "FI"  # Finland

# Survey Flow Question Schema
class SurveyQuestion(BaseModel):
    id: str
    question: str
    question_type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None  # For single/multi choice questions

    @field_validator('options')
    @classmethod
    def validate_options(cls, v, info):
        question_type = info.data.get('question_type')
        if question_type in [QuestionType.SINGLE, QuestionType.MULTI] and not v:
            raise ValueError('Options are required for single and multi choice questions')
        return v

# Survey Schemas
class SurveyBase(BaseModel):
    survey_slug: str
    name: str
    survey_flow: List[SurveyQuestion]
    is_active: bool = True

    @field_validator('survey_slug')
    @classmethod
    def validate_survey_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Survey slug can only contain letters, numbers, hyphens, and underscores')
        return v

class SurveyCreate(SurveyBase):
    pass

class SurveyUpdate(BaseModel):
    name: Optional[str] = None
    survey_flow: Optional[List[SurveyQuestion]] = None
    is_active: Optional[bool] = None

class Survey(SurveyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Submission Schemas
class SubmissionPersonalInfo(BaseModel):
    email: EmailStr
    phone_number: str
    region: Region
    date_of_birth: str  # YYYY-MM-DD format
    gender: Gender

    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date of birth must be in YYYY-MM-DD format')
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # Remove any non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 7-15 digits')
        return v

class SubmissionBase(SubmissionPersonalInfo):
    survey_id: int

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    is_approved: Optional[bool] = None
    is_completed: Optional[bool] = None

class Submission(SubmissionBase):
    id: int
    submitted_at: datetime
    is_approved: bool
    is_completed: bool
    age: Optional[int] = None
    calculated_age: Optional[int] = None

    class Config:
        from_attributes = True

# Response Schemas
class ResponseBase(BaseModel):
    submission_id: int
    question: str
    question_type: QuestionType

class ResponseAnswer(BaseModel):
    single_answer: Optional[str] = None
    free_text_answer: Optional[str] = None
    multiple_choice_answer: Optional[List[str]] = None
    photo_url: Optional[str] = None
    video_url: Optional[str] = None
    video_thumbnail_url: Optional[str] = None

    @field_validator('single_answer', 'free_text_answer')
    @classmethod
    def validate_text_answers(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError('Text answers cannot be empty')
        return v

    @field_validator('multiple_choice_answer')
    @classmethod
    def validate_multiple_choice(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('Multiple choice answer must contain at least one selection')
        return v

class ResponseCreateRequest(ResponseAnswer):
    question: str
    question_type: QuestionType

class ResponseCreate(ResponseBase, ResponseAnswer):
    pass

class ResponseUpdate(ResponseAnswer):
    pass

class Response(ResponseBase, ResponseAnswer):
    id: int
    responded_at: datetime

    class Config:
        from_attributes = True

# Combined schemas for frontend
class SurveyWithSubmissions(Survey):
    submissions: List[Submission] = []

class SubmissionWithResponses(Submission):
    responses: List[Response] = []
    survey: Survey

# File upload schema
class FileUploadResponse(BaseModel):
    file_url: str
    file_id: str
    thumbnail_url: Optional[str] = None

# Survey progress schema for frontend
class SurveyProgress(BaseModel):
    current_question: int
    total_questions: int
    submission_id: int
    is_completed: bool