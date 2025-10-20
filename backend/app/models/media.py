from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    description = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)  # For video audio transcription
    brands_detected = Column(Text, nullable=True)  # JSON string of detected brands/products
    reporting_labels = Column(Text, nullable=True)  # JSON string of Gemini-generated reporting labels
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship to response
    response = relationship("Response", back_populates="media_analysis")