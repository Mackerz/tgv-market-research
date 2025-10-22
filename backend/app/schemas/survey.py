from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from app.utils.validation import validate_email_for_pydantic

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

class ConditionOperator(str, Enum):
    EQUALS = "equals"  # Single choice equals specific value
    NOT_EQUALS = "not_equals"  # Single choice does not equal value
    CONTAINS = "contains"  # Multi choice contains specific option
    NOT_CONTAINS = "not_contains"  # Multi choice does not contain option
    CONTAINS_ANY = "contains_any"  # Multi choice contains any of the values
    CONTAINS_ALL = "contains_all"  # Multi choice contains all of the values
    GREATER_THAN = "greater_than"  # Numeric comparison (for parsed values)
    LESS_THAN = "less_than"  # Numeric comparison
    IS_ANSWERED = "is_answered"  # Question was answered
    IS_NOT_ANSWERED = "is_not_answered"  # Question was not answered

class RoutingAction(str, Enum):
    GOTO_QUESTION = "goto_question"  # Go to specific question by ID
    END_SURVEY = "end_survey"  # End survey early
    CONTINUE = "continue"  # Continue to next question in sequence

# Routing condition schema
class RoutingCondition(BaseModel):
    question_id: str  # The question ID to check the answer of
    operator: ConditionOperator
    value: Optional[Union[str, List[str], int, float]] = None  # The value(s) to compare against

    class Config:
        use_enum_values = True

# Routing rule schema
class RoutingRule(BaseModel):
    conditions: List[RoutingCondition]  # All conditions must be true (AND logic)
    action: RoutingAction
    target_question_id: Optional[str] = None  # Required if action is goto_question

    @field_validator('target_question_id')
    @classmethod
    def validate_target_question_id(cls, v, info):
        action = info.data.get('action')
        if action == RoutingAction.GOTO_QUESTION and not v:
            raise ValueError('target_question_id is required when action is goto_question')
        return v

    class Config:
        use_enum_values = True

# Media type for questions
class QuestionMediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"

# Media item for questions
class QuestionMedia(BaseModel):
    url: str  # GCP bucket URL
    type: QuestionMediaType  # photo or video
    caption: Optional[str] = None  # Optional caption for the media

    class Config:
        use_enum_values = True

# Survey Flow Question Schema
class SurveyQuestion(BaseModel):
    id: str
    question: str
    question_type: QuestionType
    required: bool = True
    options: Optional[List[str]] = None  # For single/multi choice questions
    routing_rules: Optional[List[RoutingRule]] = None  # Conditional routing logic
    media: Optional[List[QuestionMedia]] = None  # List of photos/videos to display with question

    # DEPRECATED: Legacy single media support (kept for backward compatibility)
    media_url: Optional[str] = None  # Use 'media' array instead
    media_type: Optional[QuestionMediaType] = None  # Use 'media' array instead

    @field_validator('options')
    @classmethod
    def validate_options(cls, v, info):
        question_type = info.data.get('question_type')
        if question_type in [QuestionType.SINGLE, QuestionType.MULTI] and not v:
            raise ValueError('Options are required for single and multi choice questions')
        return v

    @field_validator('routing_rules')
    @classmethod
    def validate_routing_rules(cls, v, info):
        if v is None:
            return v

        # Ensure at most one END_SURVEY rule exists
        end_survey_count = sum(1 for rule in v if rule.action == RoutingAction.END_SURVEY)
        if end_survey_count > 1:
            raise ValueError('Only one END_SURVEY routing rule is allowed per question')

        return v

    @field_validator('media_type')
    @classmethod
    def validate_media_type(cls, v, info):
        media_url = info.data.get('media_url')
        # Legacy validation: If media_url is provided, media_type must also be provided
        if media_url and not v:
            raise ValueError('media_type is required when media_url is provided')
        return v

    @field_validator('media')
    @classmethod
    def validate_media(cls, v, info):
        if v is None:
            return v

        # Ensure media array is not empty
        if len(v) == 0:
            raise ValueError('media array cannot be empty; omit field instead')

        return v

# Survey Schemas
class SurveyBase(BaseModel):
    survey_slug: str
    name: str
    client: Optional[str] = None
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
    client: Optional[str] = None
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

    @field_validator('email')
    @classmethod
    def validate_email_extended(cls, v):
        """Enhanced email validation with disposable domain blocking"""
        return validate_email_for_pydantic(v)

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
    is_approved: Optional[bool] = None  # None=pending, True=approved, False=rejected
    is_completed: bool
    age: Optional[int] = None
    calculated_age: Optional[int] = None

    class Config:
        from_attributes = True

# Response Schemas
class ResponseBase(BaseModel):
    submission_id: int
    question_id: Optional[str] = None  # Question ID from survey_flow (for efficient routing)
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
    question_id: Optional[str] = None  # Optional for backward compatibility
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