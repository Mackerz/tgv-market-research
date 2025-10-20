from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import json

class MediaBase(BaseModel):
    response_id: int
    description: Optional[str] = None
    transcript: Optional[str] = None
    brands_detected: Optional[str] = None  # JSON string
    reporting_labels: Optional[str] = None  # JSON string

class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    description: Optional[str] = None
    transcript: Optional[str] = None
    brands_detected: Optional[str] = None
    reporting_labels: Optional[str] = None

class Media(MediaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @property
    def brands_list(self) -> List[str]:
        """Parse brands_detected JSON string into list"""
        if not self.brands_detected:
            return []
        try:
            return json.loads(self.brands_detected)
        except:
            return []

    @property
    def labels_list(self) -> List[str]:
        """Parse reporting_labels JSON string into list"""
        if not self.reporting_labels:
            return []
        try:
            return json.loads(self.reporting_labels)
        except:
            return []

class MediaGalleryItem(BaseModel):
    id: int
    media_type: str  # 'photo' or 'video'
    media_url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    transcript: Optional[str] = None
    brands_detected: List[str] = []
    reporting_labels: List[str] = []
    submission_id: int
    submission_email: str
    submission_region: str
    submission_gender: str
    submission_age: int
    question: str
    responded_at: datetime

class MediaGalleryResponse(BaseModel):
    items: List[MediaGalleryItem]
    total_count: int
    photo_count: int
    video_count: int