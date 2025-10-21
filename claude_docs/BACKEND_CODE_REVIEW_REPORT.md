# Backend Code Review Report: DRY & SOLID Principles Analysis

**Date:** 2025-10-21
**Reviewer:** Claude Code
**Project:** TMG Market Research Backend (Python/FastAPI)
**Focus:** DRY Principle Violations and SOLID Principles Compliance

---

## Executive Summary

The backend codebase demonstrates **good overall architecture** with several notable strengths:
- Excellent use of dependency injection and reusable dependencies
- Strong base CRUD pattern implementation
- Good separation of concerns with service layer
- Proper use of utility functions for common operations

However, there are several areas requiring attention, particularly around **code duplication** and **adherence to SOLID principles**.

**Total Issues Found:** 24
- Critical: 2
- High: 8
- Medium: 10
- Low: 4

---

## Table of Contents

1. [DRY Principle Violations](#dry-principle-violations)
2. [SOLID Principle Violations](#solid-principle-violations)
3. [Summary and Recommendations](#summary-and-recommendations)

---

## DRY Principle Violations

### 1. Duplicate `analyze_media_content` Background Task Function

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py` (lines 22-41)
**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/submissions.py` (lines 23-42)

**Severity:** Critical

**Description:**
The exact same background task function `analyze_media_content` is duplicated in two different API endpoint files. This is a clear violation of DRY as any changes to the logic need to be made in two places.

**Current Code (Both Files):**
```python
def analyze_media_content(response_id: int, media_type: str, media_url: str):
    """Background task to analyze photo or video content using GCP AI services"""
    from app.core.database import get_db
    from app.services.media_analysis import create_media_analysis_service

    # Get database session
    db = next(get_db())

    try:
        # Use MediaAnalysisService for cleaner separation of concerns
        service = create_media_analysis_service(db)
        service.analyze_media(response_id, media_type, media_url)
    except Exception as e:
        logger.error(f"❌ Background AI analysis failed for response {response_id}: {str(e)}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    finally:
        db.close()
```

**Recommendation:**
Move this function to a shared location such as `app/services/media_analysis.py` or create a new `app/tasks/media.py` module and import it in both endpoint files.

**Refactoring Example:**
```python
# In app/tasks/media.py
from app.core.database import get_db
from app.services.media_analysis import create_media_analysis_service
import logging

logger = logging.getLogger(__name__)

def analyze_media_content_task(response_id: int, media_type: str, media_url: str):
    """Background task to analyze photo or video content"""
    db = next(get_db())
    try:
        service = create_media_analysis_service(db)
        service.analyze_media(response_id, media_type, media_url)
    except Exception as e:
        logger.error(f"Background AI analysis failed for response {response_id}: {str(e)}",
                    exc_info=True)
    finally:
        db.close()

# In both API files:
from app.tasks.media import analyze_media_content_task
# Use: background_tasks.add_task(analyze_media_content_task, ...)
```

---

### 2. Repeated Media Trigger Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py` (lines 113-127)
**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/submissions.py` (lines 117-125)

**Severity:** High

**Description:**
The logic for triggering media analysis based on question type is duplicated in two locations. The pattern of checking `question_type` and calling `background_tasks.add_task` is repeated.

**Current Pattern (Similar in Both Files):**
```python
# In media.py
if response.question_type == "photo" and response.photo_url:
    logger.info(f"🔄 Manually triggering photo analysis for response {response_id}")
    background_tasks.add_task(analyze_media_content, response_id, "photo", response.photo_url)
    return {"message": f"Photo analysis triggered for response {response_id}"}
elif response.question_type == "video" and response.video_url:
    logger.info(f"🔄 Manually triggering video analysis for response {response_id}")
    background_tasks.add_task(analyze_media_content, response_id, "video", response.video_url)
    return {"message": f"Video analysis triggered for response {response_id}"}

# Similar logic in submissions.py lines 117-125
```

**Recommendation:**
Extract this logic into a helper function or method in the service layer.

**Refactoring Example:**
```python
# In app/services/media_analysis.py
def queue_media_analysis_if_applicable(
    response: Response,
    background_tasks: BackgroundTasks
) -> bool:
    """
    Queue media analysis if response has media content

    Returns:
        True if analysis was queued, False otherwise
    """
    if response.question_type == "photo" and response.photo_url:
        logger.info(f"Queueing photo analysis for response {response.id}")
        background_tasks.add_task(
            analyze_media_content_task,
            response.id,
            "photo",
            response.photo_url
        )
        return True
    elif response.question_type == "video" and response.video_url:
        logger.info(f"Queueing video analysis for response {response.id}")
        background_tasks.add_task(
            analyze_media_content_task,
            response.id,
            "video",
            response.video_url
        )
        return True
    return False
```

---

### 3. Repeated Survey Flow Question Processing

**File:** `/home/mackers/tmg/marketResearch/backend/app/crud/reporting.py` (lines 92-103)
**File:** `/home/mackers/tmg/marketResearch/backend/app/crud/settings.py` (lines 94-122)

**Severity:** High

**Description:**
Both files iterate through `survey.survey_flow` to extract question information. The pattern of extracting `question_id`, `question_text`, and `question_type` from the flow is duplicated.

**Recommendation:**
Create a utility function for processing survey flow questions.

**Refactoring Example:**
```python
# In app/utils/survey_helpers.py
from typing import List, Dict, Any

def extract_questions_from_flow(
    survey_flow: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Extract question metadata from survey flow

    Returns list of dicts with id, question, question_type
    """
    questions = []
    for question_data in survey_flow:
        question_id = question_data.get('id')
        if not question_id:
            continue

        questions.append({
            'id': question_id,
            'question': question_data.get('question', ''),
            'question_type': question_data.get('question_type', 'unknown')
        })
    return questions
```

---

### 4. Duplicate GCS URL Handling Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/services/media_proxy.py` (lines 84-93)
**File:** Multiple GCP integration files

**Severity:** Medium

**Description:**
GCS URL parsing and validation logic appears in multiple places. The pattern of checking for `gs://` prefix and splitting bucket/path is repeated.

**Recommendation:**
Create a centralized GCS URL utility class.

**Refactoring Example:**
```python
# In app/integrations/gcp/utils.py
from typing import Tuple
from fastapi import HTTPException

class GCSUrlHelper:
    """Utility for handling GCS URLs"""

    @staticmethod
    def parse_url(gcs_url: str) -> Tuple[str, str]:
        """
        Parse GCS URL into bucket and path

        Args:
            gcs_url: URL in format gs://bucket/path

        Returns:
            Tuple of (bucket_name, blob_path)

        Raises:
            ValueError: If URL format is invalid
        """
        if not gcs_url.startswith('gs://'):
            raise ValueError("Invalid GCS URL: must start with gs://")

        url_parts = gcs_url.replace('gs://', '').split('/', 1)
        if len(url_parts) != 2:
            raise ValueError("Invalid GCS URL format: missing path")

        return url_parts[0], url_parts[1]

    @staticmethod
    def is_gcs_url(url: str) -> bool:
        """Check if URL is a valid GCS URL"""
        return url.startswith('gs://') and len(url.split('/', 1)) == 2
```

---

### 5. Repeated Content Type Detection Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/services/media_proxy.py` (lines 114-131)
**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/storage.py` (lines 146-160)

**Severity:** Medium

**Description:**
Both files contain nearly identical dictionaries mapping file extensions to MIME types. This is classic DRY violation.

**Current Code (Both Files):**
```python
# In media_proxy.py
content_types = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.mov': 'video/quicktime'
}

# In storage.py - almost identical
content_types = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'mp4': 'video/mp4',
    'avi': 'video/avi',
    'mov': 'video/quicktime',
    'wmv': 'video/x-ms-wmv',
    'webm': 'video/webm'
}
```

**Recommendation:**
Centralize content type mapping in a constants or utility module.

**Refactoring Example:**
```python
# In app/utils/media_types.py
from enum import Enum
from typing import Optional

class MediaType:
    """Centralized media type mappings"""

    CONTENT_TYPES = {
        # Images
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'bmp': 'image/bmp',

        # Videos
        'mp4': 'video/mp4',
        'avi': 'video/avi',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'webm': 'video/webm',
        'mkv': 'video/x-matroska'
    }

    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv'}

    @classmethod
    def get_content_type(cls, filename_or_ext: str) -> str:
        """Get MIME type from filename or extension"""
        ext = filename_or_ext.lower().lstrip('.')
        return cls.CONTENT_TYPES.get(ext, 'application/octet-stream')

    @classmethod
    def is_image(cls, filename: str) -> bool:
        """Check if filename is an image"""
        return any(filename.lower().endswith(ext) for ext in cls.IMAGE_EXTENSIONS)

    @classmethod
    def is_video(cls, filename: str) -> bool:
        """Check if filename is a video"""
        return any(filename.lower().endswith(ext) for ext in cls.VIDEO_EXTENSIONS)
```

---

### 6. Repeated File Extension Validation Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/storage.py` (lines 162-174)

**Severity:** Medium

**Description:**
The methods `_is_image_file` and `_is_video_file` contain repeated logic patterns that could be consolidated.

**Recommendation:**
Use the centralized `MediaType` utility suggested above.

---

### 7. Duplicate Label Parsing Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py` (lines 84-89)
**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/reporting.py` (lines 118-119)
**File:** `/home/mackers/tmg/marketResearch/backend/app/crud/reporting.py` (lines 186-197)
**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/gemini.py` (lines 333-337)

**Severity:** High

**Description:**
JSON parsing of `brands_detected` and `reporting_labels` is repeated across multiple files. While `safe_json_parse` utility exists and is used in some places, the pattern is still duplicated.

**Current Pattern:**
```python
# Pattern repeated in multiple files
try:
    brands = json.loads(media.brands_detected)
    brands_detected.update(brands)
except:
    pass

# Better approach used elsewhere:
brands_list = safe_json_parse(media.brands_detected, [])
```

**Recommendation:**
Ensure all JSON parsing uses the `safe_json_parse` utility consistently. Consider adding a method to the Media model itself.

**Refactoring Example:**
```python
# In app/models/media.py
from app.utils.json import safe_json_parse

class Media(Base):
    # ... existing fields ...

    @property
    def brands_list(self) -> List[str]:
        """Get brands as a list"""
        return safe_json_parse(self.brands_detected, [])

    @property
    def labels_list(self) -> List[str]:
        """Get reporting labels as a list"""
        return safe_json_parse(self.reporting_labels, [])
```

---

### 8. Repeated Error Logging Patterns

**Severity:** Medium

**Description:**
Error logging patterns are repeated throughout the codebase with similar structures:

```python
logger.error(f"❌ Error message: {str(e)}")
logger.error(f"❌ Error type: {type(e).__name__}")
import traceback
logger.error(f"❌ Traceback: {traceback.format_exc()}")
```

**Files:**
- `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py` (lines 36-38)
- `/home/mackers/tmg/marketResearch/backend/app/api/v1/submissions.py` (lines 36-39)
- Multiple other locations

**Recommendation:**
The logging utility already exists (`app/utils/logging.py`) with `error_failed` method. Ensure consistent usage across all modules.

---

### 9. Duplicate Simulated Response Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/gemini.py` (lines 73-81, 196-224)
**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/vision.py` (lines 54-55, 139-144)

**Severity:** Low

**Description:**
Simulated responses for development mode are scattered across integration files with similar patterns.

**Recommendation:**
Consider creating a centralized mock/simulation module for development mode responses.

---

### 10. Repeated Query Pattern for Approved Submissions

**Severity:** Low (Already Partially Addressed)

**Description:**
While `app/utils/queries.py` provides excellent helper functions like `get_approved_submissions_query`, there may still be places where this pattern is not used consistently.

**Recommendation:**
Audit all files to ensure the query helpers are used instead of inline query construction.

---

## SOLID Principle Violations

### Single Responsibility Principle (SRP) Violations

#### 1. `GCPAIAnalyzer` Class Has Multiple Responsibilities

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/vision.py`
**Lines:** 12-252

**Severity:** High

**Description:**
The `GCPAIAnalyzer` class handles:
1. Client initialization (lines 13-41)
2. Image analysis (lines 42-126)
3. Video analysis (lines 127-242)
4. Result formatting (embedded in analysis methods)
5. Error handling and logging

This violates SRP as the class has multiple reasons to change:
- Changes to Vision API
- Changes to Video API
- Changes to initialization logic
- Changes to result formatting

**Recommendation:**
Split into separate classes:

```python
# app/integrations/gcp/vision/client.py
class VisionClientManager:
    """Manages Vision API client initialization"""
    def __init__(self):
        self.enabled = os.getenv("GCP_AI_ENABLED", "false").lower() == "true"
        self.client = self._initialize_client()

    def _initialize_client(self):
        # Initialization logic
        pass

# app/integrations/gcp/vision/image_analyzer.py
class ImageAnalyzer:
    """Handles image analysis using Vision API"""
    def __init__(self, client: vision.ImageAnnotatorClient):
        self.client = client

    def analyze(self, gcs_uri: str) -> ImageAnalysisResult:
        # Image analysis logic
        pass

# app/integrations/gcp/vision/video_analyzer.py
class VideoAnalyzer:
    """Handles video analysis using Video Intelligence API"""
    def __init__(self, client: videointelligence.VideoIntelligenceServiceClient):
        self.client = client

    def analyze(self, gcs_uri: str) -> VideoAnalysisResult:
        # Video analysis logic
        pass

# app/integrations/gcp/vision/formatter.py
class AnalysisResultFormatter:
    """Formats API results into usable descriptions"""
    @staticmethod
    def format_image_result(response) -> str:
        # Formatting logic
        pass

    @staticmethod
    def format_video_result(result) -> Tuple[str, str, List[str]]:
        # Formatting logic
        pass
```

---

#### 2. `GeminiLabelGenerator` Handles Too Many Concerns

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/gemini.py`
**Lines:** 10-311

**Severity:** High

**Description:**
This class manages:
1. Client initialization and configuration (lines 11-58)
2. Label generation (lines 60-159)
3. Label summarization (lines 161-183)
4. Survey-wide label summarization (lines 185-310)
5. Database queries for survey data (lines 319-389)

The class mixes business logic, data access, and external API integration.

**Recommendation:**
Separate concerns:

```python
# app/integrations/gcp/gemini/client.py
class GeminiClient:
    """Manages Gemini API client"""
    def __init__(self):
        # Client initialization only
        pass

    def generate_content(self, prompt: str) -> str:
        # API call wrapper
        pass

# app/services/label_generator.py
class LabelGeneratorService:
    """Business logic for label generation"""
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    def generate_labels(self, description: str, transcript: str = None,
                       brands: List[str] = None) -> List[str]:
        # Label generation logic
        pass

# app/services/label_summarizer.py
class LabelSummarizerService:
    """Business logic for label summarization"""
    def __init__(self, gemini_client: GeminiClient, db: Session):
        self.client = gemini_client
        self.db = db

    def summarize_survey_labels(self, survey_id: int) -> Dict:
        # Summarization logic
        pass

# Keep database queries in CRUD layer
# app/crud/label.py
class CRUDLabel:
    """Database operations for labels"""
    def get_survey_labels(self, db: Session, survey_id: int) -> List[str]:
        # Query logic
        pass
```

---

#### 3. `GCPStorageManager` Mixes Multiple File Types

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/storage.py`
**Lines:** 10-201

**Severity:** Medium

**Description:**
The class handles:
1. Client initialization
2. Photo uploads and validation
3. Video uploads and validation
4. Generic file operations
5. Image processing (future)
6. Content type detection

**Recommendation:**
Split by file type and concern:

```python
# app/integrations/gcp/storage/base.py
class GCSStorageBase:
    """Base class for GCS operations"""
    def __init__(self):
        self.client = self._init_client()

    def upload_file(self, file: UploadFile, bucket: Bucket,
                   storage_path: str) -> str:
        # Generic upload logic
        pass

# app/integrations/gcp/storage/photo.py
class PhotoStorage(GCSStorageBase):
    """Handles photo-specific storage operations"""
    def upload(self, file: UploadFile, survey_slug: str,
              file_id: str) -> str:
        # Photo-specific logic
        pass

# app/integrations/gcp/storage/video.py
class VideoStorage(GCSStorageBase):
    """Handles video-specific storage operations"""
    def upload(self, file: UploadFile, survey_slug: str,
              file_id: str) -> Tuple[str, Optional[str]]:
        # Video-specific logic
        pass
```

---

#### 4. API Endpoints Handle Too Much Business Logic

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py`
**Lines:** 62-98 (get_survey_media_summary)

**Severity:** Medium

**Description:**
The endpoint `get_survey_media_summary` contains business logic for aggregating media analyses:

```python
def get_survey_media_summary(survey_id: int, db: Session = Depends(get_db)):
    """Get a summary of all media analyses for a survey"""
    import json

    # Get all submissions for the survey
    submissions = survey_crud.get_submissions_by_survey(db, survey_id)

    total_analyses = 0
    photo_analyses = 0
    video_analyses = 0
    brands_detected = set()

    for submission in submissions:
        for response in submission.responses:
            if response.media_analysis:
                for media in response.media_analysis:
                    total_analyses += 1
                    # ... business logic ...
```

**Recommendation:**
Move this logic to a service or CRUD layer:

```python
# In app/crud/media.py or app/services/media_analytics.py
class MediaAnalyticsService:
    """Service for media analytics and summaries"""

    def get_survey_summary(self, db: Session, survey_id: int) -> Dict:
        """Generate media summary for a survey"""
        submissions = survey_crud.get_submissions_by_survey(db, survey_id)
        # ... aggregation logic ...
        return summary_dict

# In API endpoint:
@router.get("/surveys/{survey_id}/media-summary")
def get_survey_media_summary(survey_id: int, db: Session = Depends(get_db)):
    """Get a summary of all media analyses for a survey"""
    service = MediaAnalyticsService()
    return service.get_survey_summary(db, survey_id)
```

---

### Open/Closed Principle (OCP) Violations

#### 5. Hard-Coded Media Type Handling

**File:** `/home/mackers/tmg/marketResearch/backend/app/services/media_analysis.py`
**Lines:** 54-60

**Severity:** Medium

**Description:**
The `analyze_media` method uses if/elif chains to handle different media types:

```python
if media_type == "photo":
    result = self._analyze_photo(response_id, media_url)
elif media_type == "video":
    result = self._analyze_video(response_id, media_url)
else:
    raise ValueError(f"Invalid media type: {media_type}")
```

Adding new media types requires modifying this method, violating OCP.

**Recommendation:**
Use a strategy pattern or registry:

```python
# app/services/media_analysis/strategies.py
from abc import ABC, abstractmethod

class MediaAnalysisStrategy(ABC):
    """Abstract base for media analysis strategies"""

    @abstractmethod
    def analyze(self, response_id: int, media_url: str):
        pass

class PhotoAnalysisStrategy(MediaAnalysisStrategy):
    def analyze(self, response_id: int, media_url: str):
        # Photo analysis logic
        pass

class VideoAnalysisStrategy(MediaAnalysisStrategy):
    def analyze(self, response_id: int, media_url: str):
        # Video analysis logic
        pass

# In MediaAnalysisService
class MediaAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self._strategies = {
            'photo': PhotoAnalysisStrategy(db),
            'video': VideoAnalysisStrategy(db)
        }

    def register_strategy(self, media_type: str, strategy: MediaAnalysisStrategy):
        """Allow registration of new strategies without modifying service"""
        self._strategies[media_type] = strategy

    def analyze_media(self, response_id: int, media_type: str, media_url: str):
        strategy = self._strategies.get(media_type)
        if not strategy:
            raise ValueError(f"No strategy for media type: {media_type}")
        return strategy.analyze(response_id, media_url)
```

---

#### 6. Hard-Coded Question Type Processing

**File:** `/home/mackers/tmg/marketResearch/backend/app/crud/reporting.py`
**Lines:** 79-151

**Severity:** Medium

**Description:**
The `get_question_response_data` function has hard-coded logic for 'single' and 'multi' question types. Adding new question types requires modifying this function.

**Recommendation:**
Implement a strategy pattern for question type processors:

```python
# app/services/reporting/question_processors.py
from abc import ABC, abstractmethod

class QuestionProcessor(ABC):
    @abstractmethod
    def process(self, db: Session, question: Dict,
                approved_submission_ids) -> Optional[ChartData]:
        pass

class SingleChoiceProcessor(QuestionProcessor):
    def process(self, db: Session, question: Dict,
                approved_submission_ids) -> Optional[ChartData]:
        # Single choice processing logic
        pass

class MultiChoiceProcessor(QuestionProcessor):
    def process(self, db: Session, question: Dict,
                approved_submission_ids) -> Optional[ChartData]:
        # Multi choice processing logic
        pass

# Factory or registry
class QuestionProcessorFactory:
    _processors = {
        'single': SingleChoiceProcessor(),
        'multi': MultiChoiceProcessor()
    }

    @classmethod
    def register(cls, question_type: str, processor: QuestionProcessor):
        cls._processors[question_type] = processor

    @classmethod
    def get_processor(cls, question_type: str) -> Optional[QuestionProcessor]:
        return cls._processors.get(question_type)
```

---

### Liskov Substitution Principle (LSP) Violations

#### 7. No Major LSP Violations Found

**Severity:** N/A

**Description:**
The codebase doesn't have complex inheritance hierarchies that would typically lead to LSP violations. The use of `CRUDBase` generic class is well-designed and adheres to LSP.

**Note:**
Good practice observed in `/home/mackers/tmg/marketResearch/backend/app/crud/base.py` - the generic CRUD base class can be substituted with any of its subclasses without breaking functionality.

---

### Interface Segregation Principle (ISP) Violations

#### 8. `CRUDBase` May Provide Unnecessary Methods

**File:** `/home/mackers/tmg/marketResearch/backend/app/crud/base.py`
**Lines:** 11-160

**Severity:** Low

**Description:**
The `CRUDBase` class provides all CRUD operations to all models, even if some models don't need certain operations. For example, the `exists` method (lines 148-159) may not be needed by all CRUD classes.

**Recommendation:**
Consider splitting into more focused base classes:

```python
# app/crud/base.py
class CRUDReadBase(Generic[ModelType]):
    """Base class for read operations"""
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        pass

    def get_multi(self, db: Session, *, skip: int = 0,
                  limit: int = 100) -> List[ModelType]:
        pass

class CRUDWriteBase(Generic[ModelType, CreateSchemaType]):
    """Base class for write operations"""
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        pass

class CRUDUpdateBase(Generic[ModelType, UpdateSchemaType]):
    """Base class for update operations"""
    def update(self, db: Session, *, db_obj: ModelType,
              obj_in: UpdateSchemaType) -> ModelType:
        pass

class CRUDDeleteBase(Generic[ModelType]):
    """Base class for delete operations"""
    def delete(self, db: Session, *, id: Any) -> bool:
        pass

# Compose as needed
class CRUDBase(CRUDReadBase, CRUDWriteBase, CRUDUpdateBase, CRUDDeleteBase):
    """Full CRUD operations"""
    pass

# For read-only models
class CRUDReadOnly(CRUDReadBase):
    """Read-only CRUD operations"""
    pass
```

---

#### 9. `MediaProxyService` Has Too Many Public Methods

**File:** `/home/mackers/tmg/marketResearch/backend/app/services/media_proxy.py`
**Lines:** 12-261

**Severity:** Low

**Description:**
The service exposes many methods that might not all be needed by clients. Some methods like `_parse_gcs_url`, `_get_content_type`, etc., are internal but could be part of separate utility classes.

**Recommendation:**
Keep the service interface minimal and extract utilities to separate classes as shown in earlier recommendations (MediaType utility).

---

### Dependency Inversion Principle (DIP) Violations

#### 10. Direct Dependency on Concrete GCP Clients

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/vision.py`
**Lines:** Multiple locations

**Severity:** High

**Description:**
The code directly depends on concrete GCP SDK classes (`vision.ImageAnnotatorClient`, `videointelligence.VideoIntelligenceServiceClient`) making it difficult to:
- Test without real GCP credentials
- Swap implementations
- Mock for development

**Current Code:**
```python
class GCPAIAnalyzer:
    def __init__(self):
        # Direct dependency on concrete class
        self.vision_client = vision.ImageAnnotatorClient()
        self.video_client = videointelligence.VideoIntelligenceServiceClient()
```

**Recommendation:**
Introduce abstractions:

```python
# app/integrations/gcp/vision/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

class ImageAnalyzer(ABC):
    """Abstract interface for image analysis"""

    @abstractmethod
    def analyze_image(self, gcs_uri: str) -> Optional[str]:
        """Analyze an image and return description"""
        pass

class VideoAnalyzer(ABC):
    """Abstract interface for video analysis"""

    @abstractmethod
    def analyze_video(self, gcs_uri: str) -> Tuple[Optional[str],
                                                    Optional[str],
                                                    Optional[List[str]]]:
        """Analyze a video and return (description, transcript, brands)"""
        pass

# app/integrations/gcp/vision/impl.py
class GCPImageAnalyzer(ImageAnalyzer):
    """GCP Vision API implementation"""
    def __init__(self, client: vision.ImageAnnotatorClient):
        self.client = client

    def analyze_image(self, gcs_uri: str) -> Optional[str]:
        # Implementation using GCP
        pass

class MockImageAnalyzer(ImageAnalyzer):
    """Mock implementation for testing"""
    def analyze_image(self, gcs_uri: str) -> Optional[str]:
        return "Mock image description"

# app/services/media_analysis.py
class MediaAnalysisService:
    def __init__(self, db: Session,
                 image_analyzer: ImageAnalyzer,
                 video_analyzer: VideoAnalyzer):
        self.db = db
        self.image_analyzer = image_analyzer
        self.video_analyzer = video_analyzer

    # Now can easily inject mock analyzers for testing
```

---

#### 11. Tight Coupling to Specific Database Implementation

**File:** Multiple files using `Session` from SQLAlchemy

**Severity:** Low

**Description:**
While using SQLAlchemy's `Session` directly is common, it creates tight coupling to this specific ORM.

**Recommendation:**
For a project of this size, this is acceptable. However, for larger projects, consider a repository pattern:

```python
# app/repositories/base.py
from abc import ABC, abstractmethod

class Repository(ABC):
    """Abstract repository interface"""

    @abstractmethod
    def get(self, id: Any):
        pass

    @abstractmethod
    def save(self, entity):
        pass

# app/repositories/sqlalchemy_impl.py
class SQLAlchemyRepository(Repository):
    """SQLAlchemy implementation"""
    def __init__(self, model, session: Session):
        self.model = model
        self.session = session

    def get(self, id: Any):
        return self.session.query(self.model).filter(self.model.id == id).first()

    def save(self, entity):
        self.session.add(entity)
        self.session.commit()
```

**Note:** This is a lower priority given the codebase size and the use of `get_db()` dependency injection which already provides good abstraction.

---

#### 12. Service Classes Instantiate Their Dependencies

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py`
**Lines:** 152-153

**Severity:** Medium

**Description:**
Services are created inside endpoints:

```python
service = get_media_proxy_service()  # Gets global singleton
return service.proxy_media(gcs_url, request)
```

While singleton pattern is used, this still creates tight coupling and makes testing harder.

**Recommendation:**
Use FastAPI dependency injection:

```python
# app/dependencies.py
def get_media_proxy_service() -> MediaProxyService:
    """Dependency for media proxy service"""
    return MediaProxyService()

# In endpoint
@router.api_route("/media/proxy", methods=["GET", "HEAD"])
async def proxy_media(
    gcs_url: str,
    request: Request,
    proxy_service: MediaProxyService = Depends(get_media_proxy_service)
):
    """Proxy GCS media files"""
    return proxy_service.proxy_media(gcs_url, request)
```

---

## Additional Code Quality Issues

### 13. Inconsistent Use of Type Hints

**Severity:** Medium

**Description:**
Some functions lack type hints or have incomplete type hints:

**Files with issues:**
- `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/gemini.py` (lines 161-183, missing return type)
- `/home/mackers/tmg/marketResearch/backend/app/crud/settings.py` (line 170, returns `Optional[Dict[str, Any]]` could be more specific)

**Recommendation:**
Ensure all public functions have complete type hints for better IDE support and documentation.

---

### 14. Bare Exception Clauses

**File:** `/home/mackers/tmg/marketResearch/backend/app/api/v1/media.py`
**Lines:** 88-89

**Severity:** Low

**Description:**
```python
try:
    brands = json.loads(media.brands_detected)
    brands_detected.update(brands)
except:  # Bare except
    pass
```

**Recommendation:**
Catch specific exceptions:
```python
except (json.JSONDecodeError, TypeError, AttributeError) as e:
    logger.warning(f"Failed to parse brands: {e}")
    pass
```

---

### 15. Magic Strings and Numbers

**Severity:** Low

**Description:**
Various files contain magic strings like:
- Question types: "photo", "video", "single", "multi"
- Media types in multiple locations
- HTTP status codes

**Recommendation:**
Use constants or enums:

```python
# app/constants.py
from enum import Enum

class QuestionType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    SINGLE = "single"
    MULTI = "multi"
    FREE_TEXT = "free_text"

class MediaType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"

class ApprovalStatus(str, Enum):
    PENDING = None
    APPROVED = True
    REJECTED = False
```

---

### 16. Logging Anti-Patterns

**File:** `/home/mackers/tmg/marketResearch/backend/app/integrations/gcp/gemini.py`
**Lines:** Multiple

**Severity:** Low

**Description:**
Using emoji in log messages makes them harder to parse programmatically and may cause issues with some log aggregation systems:

```python
logger.info("✅ Gemini AI services initialized successfully")
logger.error("❌ Gemini initialization failed")
```

**Recommendation:**
Use structured logging without emoji, or make emoji optional:

```python
logger.info("Gemini AI services initialized successfully", extra={'status': 'success'})
logger.error("Gemini initialization failed", extra={'status': 'error'}, exc_info=True)
```

---

## Summary and Recommendations

### Critical Priority (Address Immediately)

1. **Eliminate duplicate `analyze_media_content` function** (Issue #1)
   - Move to shared module
   - Impact: Prevents bugs from inconsistent implementations

2. **Refactor `GCPAIAnalyzer` class** (Issue #1 under SRP)
   - Split into separate analyzers
   - Impact: Improves testability and maintainability

### High Priority (Address Soon)

3. **Extract repeated media trigger logic** (Issue #2)
   - Create service method
   - Impact: Reduces code duplication

4. **Refactor `GeminiLabelGenerator`** (Issue #2 under SRP)
   - Separate concerns (client, business logic, data access)
   - Impact: Improves testability and follows SRP

5. **Introduce abstractions for GCP clients** (Issue #10 under DIP)
   - Create interfaces for image/video analyzers
   - Impact: Makes code testable without real GCP credentials

6. **Centralize content type detection** (Issue #5)
   - Create MediaType utility
   - Impact: Single source of truth for media types

7. **Extract survey flow processing** (Issue #3)
   - Create utility function
   - Impact: Reduces duplication in reporting

8. **Consolidate label parsing** (Issue #7)
   - Use model properties
   - Impact: Cleaner code, easier to maintain

### Medium Priority (Plan for Refactoring)

9. **Implement strategy pattern for media types** (Issue #5 under OCP)
   - Makes system extensible for new media types

10. **Split `GCPStorageManager`** (Issue #3 under SRP)
    - Separate photo and video storage logic

11. **Move business logic out of API endpoints** (Issue #4 under SRP)
    - Create service layer methods

12. **Centralize GCS URL handling** (Issue #4)
    - Create utility class

13. **Add comprehensive type hints** (Issue #13)
    - Improves IDE support and documentation

14. **Use dependency injection for services** (Issue #12 under DIP)
    - Improves testability

### Low Priority (Consider for Future Improvements)

15. **Refactor `CRUDBase` for ISP** (Issue #8 under ISP)
    - Split into more focused interfaces

16. **Consolidate simulated responses** (Issue #9)
    - Create mock module

17. **Use constants/enums for magic strings** (Issue #15)
    - Improves type safety

18. **Fix bare exception clauses** (Issue #14)
    - Catch specific exceptions

19. **Improve logging practices** (Issue #16)
    - Use structured logging

### Code Quality Metrics

**DRY Violations:**
- Critical: 2
- High: 3
- Medium: 4
- Low: 1

**SOLID Violations:**
- High: 4
- Medium: 4
- Low: 3

### Strengths of Current Codebase

1. **Excellent dependency injection pattern** using FastAPI's `Depends()`
2. **Well-designed CRUD base class** following generic programming
3. **Good separation** between API, CRUD, models, and services (mostly)
4. **Utility functions** for common operations (queries, JSON parsing, etc.)
5. **Type hints** are used in most places
6. **Consistent error handling** patterns in most areas
7. **Good logging practices** (despite emoji usage)

### Recommended Next Steps

1. **Week 1**: Address Critical issues #1-2
2. **Week 2-3**: Address High priority issues #3-8
3. **Week 4-5**: Plan and execute Medium priority refactoring
4. **Ongoing**: Implement Low priority improvements during regular development

### Testing Recommendations

After refactoring:

1. **Unit tests** for all new utility classes and strategies
2. **Mock implementations** for GCP services to enable offline testing
3. **Integration tests** for API endpoints
4. **Refactoring tests** - ensure behavior remains unchanged

---

## Conclusion

The codebase demonstrates **good architecture fundamentals** with room for improvement in code reuse and SOLID adherence. The primary issues are:

1. **Code duplication** that can lead to maintenance issues
2. **Classes with too many responsibilities** making them hard to test and maintain
3. **Tight coupling to concrete implementations** reducing testability
4. **Business logic in API endpoints** rather than service layer

Addressing these issues will result in:
- More maintainable codebase
- Better testability
- Easier to extend with new features
- Reduced bug risk from inconsistent implementations
- Clearer separation of concerns

The recommended refactoring can be done incrementally without disrupting current functionality.

---

**Report Generated By:** Claude Code
**Date:** 2025-10-21
**Codebase Version:** Based on main branch (commit: 0b0e09a)