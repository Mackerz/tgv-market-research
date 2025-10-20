#!/usr/bin/env python3
"""Script to update imports after restructuring"""

import os
import re
from pathlib import Path

# Define import mappings (old -> new)
IMPORT_MAPPINGS = [
    # Database
    (r"from database import", "from app.core.database import"),
    (r"import database", "from app.core import database"),

    # Models
    (r"import models(?![.])", "from app.models import user as models"),
    (r"from models import", "from app.models.user import"),
    (r"import survey_models", "from app.models import survey"),
    (r"from survey_models import", "from app.models.survey import"),
    (r"import media_models", "from app.models import media"),
    (r"from media_models import", "from app.models.media import"),
    (r"import settings_models", "from app.models import settings as settings_models"),
    (r"from settings_models import", "from app.models.settings import"),

    # Schemas
    (r"import schemas(?![.])", "from app.schemas import user as schemas"),
    (r"from schemas import", "from app.schemas.user import"),
    (r"import survey_schemas", "from app.schemas import survey as survey_schemas"),
    (r"from survey_schemas import", "from app.schemas.survey import"),
    (r"import media_schemas", "from app.schemas import media as media_schemas"),
    (r"from media_schemas import", "from app.schemas.media import"),
    (r"import reporting_schemas", "from app.schemas import reporting as reporting_schemas"),
    (r"from reporting_schemas import", "from app.schemas.reporting import"),
    (r"import settings_schemas", "from app.schemas import settings as settings_schemas"),
    (r"from settings_schemas import", "from app.schemas.settings import"),

    # CRUD
    (r"import crud(?![_.])", "from app.crud import user as crud"),
    (r"from crud import", "from app.crud.user import"),
    (r"import survey_crud", "from app.crud import survey as survey_crud"),
    (r"from survey_crud import", "from app.crud.survey import"),
    (r"import media_crud", "from app.crud import media as media_crud"),
    (r"from media_crud import", "from app.crud.media import"),
    (r"import reporting_crud", "from app.crud import reporting as reporting_crud"),
    (r"from reporting_crud import", "from app.crud.reporting import"),
    (r"import settings_crud", "from app.crud import settings as settings_crud"),
    (r"from settings_crud import", "from app.crud.settings import"),
    (r"from crud_base import", "from app.crud.base import"),

    # Services
    (r"from services\.media_analysis_service import", "from app.services.media_analysis import"),
    (r"from services\.media_proxy_service import", "from app.services.media_proxy import"),

    # Utils
    (r"from utils\.json_utils import", "from app.utils.json import"),
    (r"from utils\.logging_utils import", "from app.utils.logging import"),
    (r"from utils\.chart_utils import", "from app.utils.charts import"),
    (r"from utils\.query_helpers import", "from app.utils.queries import"),

    # Integrations
    (r"import gcp_storage", "from app.integrations.gcp import storage as gcp_storage"),
    (r"from gcp_storage import", "from app.integrations.gcp.storage import"),
    (r"import gcp_ai_analysis", "from app.integrations.gcp import vision as gcp_ai_analysis"),
    (r"from gcp_ai_analysis import", "from app.integrations.gcp.vision import"),
    (r"import gemini_labeling", "from app.integrations.gcp import gemini as gemini_labeling"),
    (r"from gemini_labeling import", "from app.integrations.gcp.gemini import"),
    (r"import secrets_manager", "from app.integrations.gcp import secrets as secrets_manager"),
    (r"from secrets_manager import", "from app.integrations.gcp.secrets import"),

    # Dependencies
    (r"from dependencies import", "from app.dependencies import"),
]

def update_file_imports(file_path: Path):
    """Update imports in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Apply all mappings
        for old_pattern, new_import in IMPORT_MAPPINGS:
            content = re.sub(old_pattern, new_import, content)

        # Only write if changed
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all Python files in app/ directory"""
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / "app"

    if not app_dir.exists():
        print(f"App directory not found: {app_dir}")
        return

    updated_count = 0
    for py_file in app_dir.rglob("*.py"):
        if py_file.name == "__pycache__":
            continue
        if update_file_imports(py_file):
            print(f"Updated: {py_file.relative_to(backend_dir)}")
            updated_count += 1

    print(f"\nTotal files updated: {updated_count}")

if __name__ == "__main__":
    main()
