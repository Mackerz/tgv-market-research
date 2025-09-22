from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class ChartData(BaseModel):
    labels: List[str]
    data: List[int]
    backgroundColor: Optional[List[str]] = None

class DemographicData(BaseModel):
    age_ranges: ChartData
    regions: ChartData
    genders: ChartData

class QuestionResponseData(BaseModel):
    question_id: str
    question_text: str
    display_name: Optional[str] = None
    question_type: str
    chart_data: ChartData

class ReportingData(BaseModel):
    total_submissions: int
    completed_approved_submissions: int
    survey_name: str
    survey_slug: str
    generated_at: datetime

    demographics: DemographicData
    question_responses: List[QuestionResponseData]