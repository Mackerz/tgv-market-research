# Quick Reference Guide - Refactored Backend

## 🚀 Quick Start for Developers

### Setup (Poetry)

```bash
# Install dependencies
poetry install

# Activate environment
poetry shell

# Run tests
poetry run pytest

# Run application
poetry run uvicorn main:app --reload
```

See `POETRY_SETUP.md` for detailed Poetry guide.

### Import Cheat Sheet

```python
# JSON utilities
from utils.json_utils import safe_json_parse, safe_json_dumps

# Logging
from utils.logging_utils import get_context_logger

# Chart colors
from utils.chart_utils import ChartColorPalette

# Query helpers
from utils.query_helpers import (
    get_approved_submissions_query,
    get_approved_submission_ids_subquery,
    get_submission_counts
)

# Services
from services.media_analysis_service import create_media_analysis_service
from services.media_proxy_service import get_media_proxy_service

# Dependencies
from dependencies import get_survey_or_404, get_submission_or_404, get_response_or_404

# CRUD Base
from crud_base import CRUDBase
```

---

## 📦 Common Patterns

### 1. Safe JSON Parsing

```python
# OLD WAY ❌
try:
    data = json.loads(json_string) if json_string else []
except json.JSONDecodeError:
    data = []

# NEW WAY ✅
data = safe_json_parse(json_string, default=[])
```

### 2. Database Queries for Approved Submissions

```python
# OLD WAY ❌
submissions = db.query(Submission).filter(
    and_(
        Submission.survey_id == survey_id,
        Submission.is_completed == True,
        Submission.is_approved == True
    )
).all()

# NEW WAY ✅
submissions = get_approved_submissions_query(db, survey_id).all()

# For subquery
approved_ids = get_approved_submission_ids_subquery(db, survey_id)

# For counts
counts = get_submission_counts(db, survey_id)
# Returns: {'total': 100, 'completed': 80, 'approved': 60, 'rejected': 10, 'pending': 10}
```

### 3. Chart Colors

```python
# OLD WAY ❌
colors = ['#FF6384', '#36A2EB', '#FFCE56', ...]
chart = ChartData(backgroundColor=colors[:len(data)])

# NEW WAY ✅
chart = ChartData(backgroundColor=ChartColorPalette.get_colors(len(data)))
```

### 4. FastAPI Endpoints with Survey Lookup

```python
# OLD WAY ❌
@app.get("/api/reports/{survey_slug}/data")
def get_data(survey_slug: str, db: Session = Depends(get_db)):
    survey = survey_crud.get_survey_by_slug(db, survey_slug)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    # ... logic ...

# NEW WAY ✅
@app.get("/api/reports/{survey_slug}/data")
def get_data(survey = Depends(get_survey_or_404), db: Session = Depends(get_db)):
    # survey is already validated
    # ... logic ...
```

### 5. Media Analysis

```python
# OLD WAY ❌ (in main.py, 71 lines)
def analyze_media_content(response_id, media_type, media_url):
    db = next(get_db())
    try:
        if media_type == "photo":
            # lots of logic...
        elif media_type == "video":
            # lots of logic...
    except Exception as e:
        # error handling...
    finally:
        db.close()

# NEW WAY ✅
from services.media_analysis_service import create_media_analysis_service

def analyze_media_content(response_id, media_type, media_url):
    db = next(get_db())
    try:
        service = create_media_analysis_service(db)
        service.analyze_media(response_id, media_type, media_url)
    finally:
        db.close()
```

### 6. Logging

```python
# OLD WAY ❌
logger.info(f"🔄 Starting analysis for response {response_id}")
logger.error(f"❌ Analysis failed: {str(e)}")
logger.error(f"❌ Error type: {type(e).__name__}")

# NEW WAY ✅
logger = get_context_logger(__name__)
logger.info_start("analysis", response_id=response_id)
logger.error_failed("analysis", e, response_id=response_id)
```

---

## 🔧 Creating New CRUD Operations

### Using the Base Class

```python
from crud_base import CRUDBase
from models import MyModel
from schemas import MyModelCreate, MyModelUpdate

class MyModelCRUD(CRUDBase[MyModel, MyModelCreate, MyModelUpdate]):
    # Inherit all common operations: get, get_multi, create, update, delete

    # Add custom operations
    def get_by_custom_field(self, db: Session, field_value: str):
        return db.query(self.model).filter(
            self.model.custom_field == field_value
        ).first()

# Usage
my_crud = MyModelCRUD(MyModel)
item = my_crud.get(db, id=1)
items = my_crud.get_multi(db, skip=0, limit=100)
new_item = my_crud.create(db, obj_in=create_schema)
updated = my_crud.update(db, db_obj=item, obj_in=update_schema)
deleted = my_crud.delete(db, id=1)
```

---

## 📝 Code Review Checklist

Before submitting code, check:

- [ ] **JSON Parsing**: Using `safe_json_parse()` instead of manual try/except?
- [ ] **Query Logic**: Using query helpers for approved submissions?
- [ ] **Chart Colors**: Using `ChartColorPalette` instead of hardcoded arrays?
- [ ] **Dependencies**: Using FastAPI dependencies for common lookups?
- [ ] **Logging**: Using `ContextLogger` for consistent logging?
- [ ] **Services**: Business logic in service classes, not endpoints?
- [ ] **CRUD**: Using `CRUDBase` for common operations?
- [ ] **DRY**: No duplicate code patterns?
- [ ] **SRP**: Each function/class has single responsibility?

---

## 🐛 Common Mistakes to Avoid

### ❌ Don't Do This

```python
# Hardcoding colors
colors = ['#FF6384', '#36A2EB']

# Manual JSON parsing
try:
    data = json.loads(string)
except:
    data = []

# Duplicate query logic
submissions = db.query(Submission).filter(
    and_(Submission.is_completed == True, Submission.is_approved == True)
).all()

# Repeating survey lookup
survey = survey_crud.get_survey_by_slug(db, survey_slug)
if not survey:
    raise HTTPException(404)

# Business logic in endpoints
@app.post("/api/analyze")
def endpoint():
    # 50 lines of analysis logic...
```

### ✅ Do This Instead

```python
# Use color palette
colors = ChartColorPalette.get_colors(len(data))

# Use safe JSON utility
data = safe_json_parse(string, [])

# Use query helper
submissions = get_approved_submissions_query(db, survey_id).all()

# Use dependency
def endpoint(survey = Depends(get_survey_or_404)):
    pass

# Business logic in service
service = create_media_analysis_service(db)
service.analyze_media(response_id, media_type, media_url)
```

---

## 🎯 When to Use What

| Task | Use This |
|------|----------|
| Parse JSON from database | `safe_json_parse()` |
| Convert object to JSON | `safe_json_dumps()` |
| Get approved submissions | `get_approved_submissions_query()` |
| Get submission counts | `get_submission_counts()` |
| Validate survey exists | `Depends(get_survey_or_404)` |
| Analyze media | `MediaAnalysisService` |
| Proxy media files | `MediaProxyService` |
| Chart colors | `ChartColorPalette` |
| Logging | `get_context_logger()` |
| Common CRUD | `CRUDBase` |

---

## 💡 Tips

1. **Always use utilities**: They handle edge cases you might forget
2. **Prefer dependencies**: Cleaner endpoint signatures, automatic validation
3. **Services for business logic**: Keep endpoints thin, services fat
4. **Centralized patterns**: Change once, affect everywhere
5. **Type hints**: Utilities are fully typed for IDE support

---

## 🆘 Need Help?

1. Check `REFACTORING_SUMMARY.md` for detailed explanations
2. Look at updated files for examples:
   - `reporting_crud.py` - Query helpers, chart colors, JSON utils
   - `main.py` - Dependencies, services
   - `media_crud.py` - JSON utilities
3. Review service implementations in `services/` directory

---

## 📞 Questions?

Common questions:

**Q: Do I need to update all old code immediately?**
A: No, but new code should use the new patterns. Refactor old code opportunistically.

**Q: What if I need custom behavior?**
A: Extend the base classes or utilities. They're designed to be extended.

**Q: Are there performance impacts?**
A: No, utilities add negligible overhead. Query helpers are actually MORE efficient.

**Q: Can I still use the old patterns?**
A: Yes, but the new patterns are preferred for consistency and maintainability.
