# Backend Restructure Plan

## 📋 Current Structure Analysis

### Problems Identified

1. **Flat Structure**: 25+ Python files in root directory
2. **No Clear Separation**: Models, schemas, CRUD, and services mixed together
3. **Poor Discoverability**: Hard to find related files
4. **Scaling Issues**: Will become worse as project grows
5. **Import Complexity**: Long import paths, unclear dependencies
6. **Domain Logic Scattered**: Survey, media, reporting, and settings logic not grouped

### Current Root Directory Files (25+ files)

```
backend/
├── main.py (846 lines) - API endpoints
├── database.py - Database configuration
├── dependencies.py - FastAPI dependencies
├── crud_base.py - Generic CRUD base class
│
├── models.py - User models
├── schemas.py - User schemas
├── crud.py - User CRUD operations
│
├── survey_models.py - Survey models
├── survey_schemas.py - Survey schemas
├── survey_crud.py - Survey CRUD operations
│
├── media_models.py - Media models
├── media_schemas.py - Media schemas
├── media_crud.py - Media CRUD operations
│
├── reporting_schemas.py - Reporting schemas
├── reporting_crud.py - Reporting CRUD operations
│
├── settings_models.py - Settings models
├── settings_schemas.py - Settings schemas
├── settings_crud.py - Settings CRUD operations
│
├── gcp_storage.py - GCP Storage integration
├── gcp_ai_analysis.py - GCP AI integration
├── gemini_labeling.py - Gemini AI labeling
├── secrets_manager.py - GCP Secrets Manager
│
├── run-migrations.py - Migration runner
│
├── services/ - Service layer (2 files)
├── utils/ - Utilities (4 files)
├── tests/ - Tests (7 files)
└── alembic/ - Database migrations
```

---

## 🎯 Proposed Structure

### New Organization (Domain-Driven Design)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization & main endpoints
│   ├── config.py                  # Configuration (from database.py + settings)
│   ├── dependencies.py            # FastAPI dependencies
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py            # Database session management
│   │   ├── security.py            # Authentication/authorization (if needed)
│   │   └── exceptions.py          # Custom exceptions
│   │
│   ├── models/                    # SQLAlchemy models (domain entities)
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   ├── user.py                # User models (from models.py)
│   │   ├── survey.py              # Survey models (from survey_models.py)
│   │   ├── submission.py          # Submission models (part of survey_models.py)
│   │   ├── media.py               # Media models (from media_models.py)
│   │   └── settings.py            # Settings models (from settings_models.py)
│   │
│   ├── schemas/                   # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── user.py                # User schemas (from schemas.py)
│   │   ├── survey.py              # Survey schemas (from survey_schemas.py)
│   │   ├── submission.py          # Submission schemas
│   │   ├── media.py               # Media schemas (from media_schemas.py)
│   │   ├── reporting.py           # Reporting schemas (from reporting_schemas.py)
│   │   └── settings.py            # Settings schemas (from settings_schemas.py)
│   │
│   ├── crud/                      # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                # Base CRUD (from crud_base.py)
│   │   ├── user.py                # User CRUD (from crud.py)
│   │   ├── survey.py              # Survey CRUD (from survey_crud.py)
│   │   ├── submission.py          # Submission CRUD
│   │   ├── media.py               # Media CRUD (from media_crud.py)
│   │   ├── reporting.py           # Reporting CRUD (from reporting_crud.py)
│   │   └── settings.py            # Settings CRUD (from settings_crud.py)
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── media_analysis.py      # Media analysis service
│   │   ├── media_proxy.py         # Media proxy service
│   │   ├── reporting.py           # Reporting service (extract from reporting_crud.py)
│   │   └── survey.py              # Survey service (orchestration logic)
│   │
│   ├── api/                       # API routes (split from main.py)
│   │   ├── __init__.py
│   │   ├── deps.py                # Route dependencies
│   │   ├── v1/                    # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Main v1 router
│   │   │   ├── users.py           # User endpoints
│   │   │   ├── surveys.py         # Survey endpoints
│   │   │   ├── submissions.py     # Submission endpoints
│   │   │   ├── media.py           # Media endpoints
│   │   │   ├── reporting.py       # Reporting endpoints
│   │   │   └── settings.py        # Settings endpoints
│   │   └── websockets.py          # WebSocket endpoints (if any)
│   │
│   ├── integrations/              # External service integrations
│   │   ├── __init__.py
│   │   ├── gcp/
│   │   │   ├── __init__.py
│   │   │   ├── storage.py         # GCP Storage (from gcp_storage.py)
│   │   │   ├── vision.py          # GCP Vision AI (from gcp_ai_analysis.py)
│   │   │   ├── video.py           # GCP Video Intelligence
│   │   │   ├── gemini.py          # Gemini AI (from gemini_labeling.py)
│   │   │   └── secrets.py         # Secrets Manager (from secrets_manager.py)
│   │   └── ...                    # Future integrations
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── json.py                # JSON utilities (from utils/json_utils.py)
│       ├── logging.py             # Logging utilities (from utils/logging_utils.py)
│       ├── charts.py              # Chart utilities (from utils/chart_utils.py)
│       └── queries.py             # Query helpers (from utils/query_helpers.py)
│
├── tests/                         # Tests (mirror app structure)
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_utils.py
│   │   ├── test_crud.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/
│       └── test_workflows.py
│
├── alembic/                       # Database migrations (unchanged)
│   ├── versions/
│   └── env.py
│
├── scripts/                       # Utility scripts
│   ├── __init__.py
│   └── run_migrations.py          # From run-migrations.py
│
├── pyproject.toml                 # Poetry configuration
├── poetry.lock                    # Poetry lock file
├── .env.example                   # Environment variables template
├── .gitignore
├── README.md
└── [documentation files]
```

---

## 📊 Restructuring Benefits

### 1. Clear Domain Separation

**Before**: All survey-related files scattered
```
backend/survey_models.py
backend/survey_schemas.py
backend/survey_crud.py
backend/main.py (survey endpoints mixed with others)
```

**After**: Survey domain grouped together
```
app/models/survey.py
app/schemas/survey.py
app/crud/survey.py
app/api/v1/surveys.py
app/services/survey.py (optional)
```

### 2. Scalability

- Easy to add new domains (e.g., `app/models/analytics.py`)
- Clear where new code belongs
- Prevents root directory bloat

### 3. Better Imports

**Before**:
```python
from survey_models import Survey
from survey_schemas import SurveyCreate
from survey_crud import create_survey
from gcp_storage import upload_to_gcs
```

**After**:
```python
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate
from app.crud.survey import create_survey
from app.integrations.gcp.storage import upload_to_gcs
```

### 4. Easier Testing

Tests can mirror the app structure:
```
tests/unit/models/test_survey.py
tests/unit/crud/test_survey.py
tests/integration/api/test_surveys.py
```

### 5. Better IDE Support

- Clear module boundaries
- Better autocomplete
- Easier navigation
- Clearer dependency tree

---

## 🔄 Migration Strategy

### Phase 1: Create New Structure (No Breaking Changes)

1. Create new directory structure
2. Create `__init__.py` files with proper exports
3. Keep old files in place initially

### Phase 2: Move Files Gradually (Domain by Domain)

**Domain Order** (least coupled to most coupled):
1. **Utils** → `app/utils/`
2. **Core** → `app/core/`
3. **Integrations** → `app/integrations/gcp/`
4. **Models** → `app/models/`
5. **Schemas** → `app/schemas/`
6. **CRUD** → `app/crud/`
7. **Services** → `app/services/`
8. **API Routes** → `app/api/v1/`

### Phase 3: Update Imports

1. Update imports in moved files
2. Create compatibility imports in old locations (temporary)
3. Update tests
4. Update documentation

### Phase 4: Split main.py

1. Extract route definitions to `app/api/v1/` modules
2. Keep app initialization in `app/main.py`
3. Update route imports

### Phase 5: Cleanup

1. Remove old files
2. Remove compatibility imports
3. Update all documentation
4. Run full test suite

---

## 📝 Detailed Migration Plan

### Step 1: Create app/ Directory Structure

```bash
mkdir -p app/{core,models,schemas,crud,services,api/v1,integrations/gcp,utils}
touch app/__init__.py
touch app/{core,models,schemas,crud,services,api,api/v1,integrations,integrations/gcp,utils}/__init__.py
```

### Step 2: Move Utils (Simplest, No Dependencies)

```bash
# Move and rename
mv utils/json_utils.py app/utils/json.py
mv utils/logging_utils.py app/utils/logging.py
mv utils/chart_utils.py app/utils/charts.py
mv utils/query_helpers.py app/utils/queries.py

# Update app/utils/__init__.py with exports
```

### Step 3: Move Core Infrastructure

```bash
mv database.py app/core/database.py
mv crud_base.py app/crud/base.py
mv dependencies.py app/dependencies.py  # Or app/api/deps.py
```

### Step 4: Move Models (Domain by Domain)

```bash
# User domain
mv models.py app/models/user.py

# Survey domain
mv survey_models.py app/models/survey.py

# Media domain
mv media_models.py app/models/media.py

# Settings domain
mv settings_models.py app/models/settings.py
```

### Step 5: Move Schemas

```bash
mv schemas.py app/schemas/user.py
mv survey_schemas.py app/schemas/survey.py
mv media_schemas.py app/schemas/media.py
mv reporting_schemas.py app/schemas/reporting.py
mv settings_schemas.py app/schemas/settings.py
```

### Step 6: Move CRUD

```bash
mv crud.py app/crud/user.py
mv survey_crud.py app/crud/survey.py
mv media_crud.py app/crud/media.py
mv reporting_crud.py app/crud/reporting.py
mv settings_crud.py app/crud/settings.py
```

### Step 7: Move Services

```bash
mv services/media_analysis_service.py app/services/media_analysis.py
mv services/media_proxy_service.py app/services/media_proxy.py
```

### Step 8: Move Integrations

```bash
mv gcp_storage.py app/integrations/gcp/storage.py
mv gcp_ai_analysis.py app/integrations/gcp/vision.py
mv gemini_labeling.py app/integrations/gcp/gemini.py
mv secrets_manager.py app/integrations/gcp/secrets.py
```

### Step 9: Split main.py into API Routes

Create separate route files:
- `app/api/v1/users.py`
- `app/api/v1/surveys.py`
- `app/api/v1/submissions.py`
- `app/api/v1/media.py`
- `app/api/v1/reporting.py`
- `app/api/v1/settings.py`

Keep in `app/main.py`:
- FastAPI app initialization
- Middleware configuration
- CORS setup
- Route registration

### Step 10: Move Scripts

```bash
mkdir scripts
mv run-migrations.py scripts/run_migrations.py
```

---

## 🔧 Import Update Examples

### Before (Flat Structure)

```python
# In main.py
from survey_models import Survey
from survey_schemas import SurveyCreate, SurveyResponse
from survey_crud import create_survey, get_survey_by_slug
from gcp_storage import upload_to_gcs
from utils.json_utils import safe_json_parse
```

### After (Structured)

```python
# In app/api/v1/surveys.py
from app.models.survey import Survey
from app.schemas.survey import SurveyCreate, SurveyResponse
from app.crud.survey import create_survey, get_survey_by_slug
from app.integrations.gcp.storage import upload_to_gcs
from app.utils.json import safe_json_parse
```

### Compatibility Layer (Temporary)

Create temporary files in old locations:

```python
# survey_models.py (temporary compatibility)
from app.models.survey import *

import warnings
warnings.warn(
    "Importing from survey_models is deprecated. Use app.models.survey instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## ✅ Testing Strategy

### During Migration

1. **Keep tests passing**: Run `poetry run pytest` after each move
2. **Update test imports**: Update imports as files move
3. **Add integration tests**: Ensure cross-domain functionality works
4. **Test import paths**: Verify both old and new imports work (temporarily)

### After Migration

1. **Full test suite**: All 170+ tests should pass
2. **Import cleanup**: Remove old compatibility imports
3. **Documentation**: Update all documentation with new structure
4. **Manual testing**: Test key workflows in development

---

## 📊 Estimated Impact

### Files to Move/Update

| Category | Files | Lines | Complexity |
|----------|-------|-------|------------|
| Utils | 4 | ~200 | Low |
| Core | 3 | ~250 | Low |
| Models | 5 | ~350 | Medium |
| Schemas | 5 | ~650 | Medium |
| CRUD | 6 | ~1,200 | Medium |
| Services | 2 | ~400 | Medium |
| Integrations | 4 | ~1,100 | Medium |
| API Routes | 1 (split into 6+) | ~850 | High |
| Tests | 7 | ~2,500 | Medium |
| **Total** | **37** | **~7,500** | **Medium-High** |

### Time Estimate

- **Phase 1** (Structure): 30 minutes
- **Phase 2** (Move files): 2-3 hours
- **Phase 3** (Update imports): 3-4 hours
- **Phase 4** (Split main.py): 2-3 hours
- **Phase 5** (Testing & cleanup): 2-3 hours

**Total**: 9-13 hours (1-2 days of focused work)

---

## 🚨 Risks & Mitigation

### Risk 1: Breaking Imports

**Mitigation**:
- Create compatibility layer during transition
- Update imports incrementally
- Run tests frequently

### Risk 2: Circular Imports

**Mitigation**:
- Follow dependency hierarchy (utils → models → crud → services → api)
- Use `TYPE_CHECKING` for type hints
- Consider dependency injection

### Risk 3: Alembic Migration Issues

**Mitigation**:
- Update `alembic/env.py` to import from new locations
- Test migrations in development first
- Keep model imports in single place initially

### Risk 4: Lost Productivity During Migration

**Mitigation**:
- Do migration in separate branch
- Create detailed migration checklist
- Communicate timeline to team
- Deploy after thorough testing

---

## 🎯 Success Criteria

- [ ] All files organized into logical domain groups
- [ ] No files in backend root (except config files)
- [ ] All 170+ tests passing
- [ ] All imports updated to new structure
- [ ] No circular import issues
- [ ] Application runs successfully
- [ ] Alembic migrations work
- [ ] Documentation updated
- [ ] Team trained on new structure

---

## 📚 Additional Benefits

### 1. API Versioning Ready

```python
app/api/
├── v1/  # Current API
└── v2/  # Future API version
```

### 2. Feature Flags Support

```python
app/core/
└── feature_flags.py
```

### 3. Background Tasks

```python
app/tasks/
├── __init__.py
├── celery.py
└── media_processing.py
```

### 4. Testing Improvements

```python
tests/
├── unit/       # Fast, isolated tests
├── integration/  # Cross-component tests
└── e2e/        # Full workflow tests
```

---

## 🔄 Alternative: Gradual Approach

If full restructure is too risky, consider gradual approach:

### Step 1: Create app/ and Move New Code Only

- Keep old structure as-is
- All **new** code goes into proper structure
- Refactor old code opportunistically

### Step 2: Move One Domain at a Time

- Week 1: Move Survey domain
- Week 2: Move Media domain
- Week 3: Move Reporting domain
- etc.

### Step 3: Split main.py Last

- Keep monolithic main.py until everything else is moved
- Split routes once confidence is high

---

## 💡 Recommendations

### Recommended Approach: Full Restructure

**Why**:
- Clean break, no confusion about "old vs new"
- All benefits realized immediately
- Easier to enforce new patterns
- Tests provide safety net

**When**:
- Allocate 1-2 days of focused time
- During low-traffic period
- After current features are complete
- Before next major feature

### Alternative: Gradual Migration

**Why**:
- Less risky
- Can continue development
- Learn from each domain migration

**When**:
- Can't allocate focused time
- Active development continues
- Team needs to adapt gradually

---

## ✨ Summary

The backend has a flat structure with 25+ files in the root directory. Reorganizing into a domain-driven structure will:

- ✅ Improve discoverability and navigation
- ✅ Enable better scaling as project grows
- ✅ Provide clearer separation of concerns
- ✅ Make testing and maintenance easier
- ✅ Follow FastAPI and Python best practices
- ✅ Prepare for future features (API versioning, background tasks, etc.)

**Recommended**: Full restructure with 1-2 days of focused work, leveraging the comprehensive test suite (170+ tests) as a safety net.

---

**Next Steps**:
1. Review this plan
2. Choose approach (full vs gradual)
3. Create feature branch: `restructure-backend`
4. Begin migration following the detailed steps
5. Run tests after each phase
6. Deploy after full test suite passes

