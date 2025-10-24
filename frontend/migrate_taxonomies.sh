#!/bin/bash
# Migrate TaxonomiesTab to use taxonomyService

FILE="src/components/report/TaxonomiesTab.tsx"

# Backup
cp "$FILE" "${FILE}.bak"

# Replace fetchMediaPreviews
perl -i -0pe 's/const fetchMediaPreviews = async \(systemLabel: string\) => \{\n    try \{\n      const response = await fetch\(\n        `\$\{API_URL\}\/api\/surveys\/\$\{surveyId\}\/system-labels\/\$\{encodeURIComponent\(systemLabel\)\}\/media\?limit=5`,\n        \{ credentials: .include. \}\n      \);[\s\S]*?const data = await response\.json\(\);[\s\S]*?setMediaPreviews\(data\);/const fetchMediaPreviews = async (systemLabel: string) => {\n    try {\n      const data = await taxonomyService.getMediaPreviews(surveyId, systemLabel, 5);\n      setMediaPreviews(data);/g' "$FILE"

# Replace addSystemLabel
perl -i -0pe 's/const addSystemLabel = async \(reportingLabelId: number, systemLabel: string\) => \{\n    try \{\n      const response = await fetch\(`\$\{API_URL\}\/api\/reporting-labels\/\$\{reportingLabelId\}\/system-labels`,[\s\S]*?method: .POST.,[\s\S]*?body: JSON\.stringify\(\{ system_label: systemLabel \}\),[\s\S]*?\}\);[\s\S]*?if \(response\.ok\) \{/const addSystemLabel = async (reportingLabelId: number, systemLabel: string) => {\n    try {\n      await taxonomyService.addSystemLabel(reportingLabelId, systemLabel);/g' "$FILE"

# Replace removeSystemLabel
perl -i -0pe 's/const removeSystemLabel = async \(reportingLabelId: number, systemLabel: string\) => \{\n    try \{\n      const response = await fetch\(`\$\{API_URL\}\/api\/reporting-labels\/\$\{reportingLabelId\}\/system-labels`,[\s\S]*?method: .DELETE.,[\s\S]*?body: JSON\.stringify\(\{ system_label: systemLabel \}\),[\s\S]*?\}\);[\s\S]*?if \(response\.ok\) \{/const removeSystemLabel = async (reportingLabelId: number, systemLabel: string) => {\n    try {\n      await taxonomyService.removeSystemLabel(reportingLabelId, systemLabel);/g' "$FILE"

# Replace updateReportingLabel
perl -i -0pe 's/const updateReportingLabel = async \(labelId: number\) => \{\n    try \{\n      const updateData: ReportingLabelUpdate = \{[\s\S]*?\};[\s\S]*?const response = await fetch\(`\$\{API_URL\}\/api\/reporting-labels\/\$\{labelId\}`,[\s\S]*?method: .PUT.,[\s\S]*?body: JSON\.stringify\(updateData\),[\s\S]*?\}\);[\s\S]*?if \(response\.ok\) \{/const updateReportingLabel = async (labelId: number) => {\n    try {\n      const updateData: ReportingLabelUpdate = {\n        label_name: editName,\n        description: editDescription || undefined,\n      };\n      await taxonomyService.updateReportingLabel(labelId, updateData);/g' "$FILE"

# Replace createReportingLabel
perl -i -0pe 's/const createReportingLabel = async \(\) => \{\n    try \{\n      const createData: ReportingLabelCreate = \{[\s\S]*?\};[\s\S]*?const response = await fetch\(`\$\{API_URL\}\/api\/reporting-labels`,[\s\S]*?method: .POST.,[\s\S]*?body: JSON\.stringify\(createData\),[\s\S]*?\}\);[\s\S]*?if \(response\.ok\) \{/const createReportingLabel = async () => {\n    try {\n      const createData: ReportingLabelCreate = {\n        survey_id: surveyId,\n        label_name: newLabelName,\n        description: newLabelDescription || undefined,\n        is_ai_generated: false,\n        system_labels: [],\n      };\n      await taxonomyService.createReportingLabel(createData);/g' "$FILE"

# Replace deleteReportingLabel
perl -i -0pe 's/const deleteReportingLabel = async \(labelId: number\) => \{[\s\S]*?try \{\n      const response = await fetch\(`\$\{API_URL\}\/api\/reporting-labels\/\$\{labelId\}`,[\s\S]*?method: .DELETE.,[\s\S]*?credentials: .include.,[\s\S]*?\}\);[\s\S]*?if \(response\.ok\) \{/const deleteReportingLabel = async (labelId: number) => {\n    if (!confirm(\x27Delete this reporting label? This is only possible if no system labels are mapped to it.\x27)) {\n      return;\n    }\n    try {\n      await taxonomyService.deleteReportingLabel(labelId);/g' "$FILE"

echo "Migration complete. Backup saved to ${FILE}.bak"
