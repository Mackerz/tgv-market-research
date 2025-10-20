from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.db_types import JSONType, BigIntegerType

class ReportSettings(Base):
    __tablename__ = "report_settings"

    id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True)
    survey_id = Column(BigIntegerType, ForeignKey("surveys.id"), unique=True, nullable=False)

    # Age ranges stored as JSON array of objects: [{"min": 0, "max": 18, "label": "0-18"}, ...]
    age_ranges = Column(JSONType, nullable=False, default=[
        {"min": 0, "max": 18, "label": "0-18"},
        {"min": 18, "max": 25, "label": "18-25"},
        {"min": 25, "max": 40, "label": "25-40"},
        {"min": 40, "max": 60, "label": "40-60"},
        {"min": 60, "max": None, "label": "60+"}
    ])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    survey = relationship("Survey", back_populates="report_settings")
    question_display_names = relationship("QuestionDisplayName", back_populates="report_settings")

class QuestionDisplayName(Base):
    __tablename__ = "question_display_names"

    id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True)
    report_settings_id = Column(BigIntegerType, ForeignKey("report_settings.id"), nullable=False)

    # Store the question text from the survey flow
    question_text = Column(Text, nullable=False)

    # Custom display name for reports (if empty, use original question text)
    display_name = Column(Text, nullable=True)

    # Question ID from survey flow for reference
    question_id = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    report_settings = relationship("ReportSettings", back_populates="question_display_names")