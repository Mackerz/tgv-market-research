#!/bin/bash
# Script to replace console statements with logger

cd src

# List of files to update
files=(
  "app/report/page.tsx"
  "contexts/AuthContext.tsx"
  "app/page.tsx"
  "app/login/page.tsx"
  "app/survey/create/page.tsx"
  "app/survey/[slug]/page.tsx"
  "hooks/useSurvey.ts"
  "lib/api/client.ts"
  "components/survey/QuestionComponent.tsx"
  "components/survey/PersonalInfoForm.tsx"
  "components/survey/questions/MediaUploadQuestion.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing: $file"

    # Check if logger import already exists
    if ! grep -q "from '@/lib/logger'" "$file"; then
      # Add import after first import line
      sed -i "1,/^import/s/^\(import.*;\)$/\1\nimport { logger } from '@\/lib\/logger';/" "$file"
    fi

    # Replace console statements (simple patterns)
    sed -i "s/console\.error(/logger.error(/g" "$file"
    sed -i "s/console\.log(/logger.debug(/g" "$file"
    sed -i "s/console\.warn(/logger.warn(/g" "$file"
    sed -i "s/console\.info(/logger.info(/g" "$file"
  fi
done

echo "Done!"
