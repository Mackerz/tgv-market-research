#!/usr/bin/env python3
"""Script to update test imports after restructuring"""

import re
from pathlib import Path

# Define import mappings for tests
TEST_IMPORT_MAPPINGS = [
    # Database
    (r"from database import", "from app.core.database import"),

    # Models
    (r"^import models$", "from app.models import user as models"),
    (r"^import survey_models$", "from app.models import survey as survey_models"),
    (r"^import media_models$", "from app.models import media as media_models"),
    (r"^import settings_models$", "from app.models import settings as settings_models"),

    # CRUD
    (r"^import survey_crud$", "from app.crud import survey as survey_crud"),
    (r"from crud_base import", "from app.crud.base import"),

    # Utils
    (r"from utils\.chart_utils import", "from app.utils.charts import"),
    (r"from utils\.json_utils import", "from app.utils.json import"),
    (r"from utils\.logging_utils import", "from app.utils.logging import"),
    (r"from utils\.query_helpers import", "from app.utils.queries import"),

    # Dependencies
    (r"from dependencies import", "from app.dependencies import"),
]

def update_file_imports(file_path: Path):
    """Update imports in a single test file"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        original_lines = lines[:]
        updated_lines = []

        for line in lines:
            updated_line = line
            for old_pattern, new_import in TEST_IMPORT_MAPPINGS:
                if re.match(old_pattern, line.strip()):
                    # For full line replacements
                    updated_line = new_import + "\n"
                    break
                else:
                    # For pattern replacements within line
                    updated_line = re.sub(old_pattern, new_import, updated_line)
            updated_lines.append(updated_line)

        # Only write if changed
        if updated_lines != original_lines:
            with open(file_path, 'w') as f:
                f.writelines(updated_lines)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all test files"""
    backend_dir = Path(__file__).parent.parent
    tests_dir = backend_dir / "tests"

    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return

    updated_count = 0
    for py_file in tests_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        if update_file_imports(py_file):
            print(f"Updated: {py_file.relative_to(backend_dir)}")
            updated_count += 1

    print(f"\nTotal test files updated: {updated_count}")

if __name__ == "__main__":
    main()
