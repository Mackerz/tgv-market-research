# Survey Routing - Quick Reference Card

## Basic Structure

```json
{
  "id": "question_id",
  "question": "Your question text?",
  "question_type": "single",
  "options": ["Option 1", "Option 2"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "question_id",
          "operator": "equals",
          "value": "Option 1"
        }
      ],
      "action": "goto_question",
      "target_question_id": "target_id"
    }
  ]
}
```

## Operators Cheat Sheet

### Single Choice
```json
{ "operator": "equals", "value": "Option A" }
{ "operator": "not_equals", "value": "Option B" }
```

### Multiple Choice
```json
{ "operator": "contains", "value": "Option A" }
{ "operator": "not_contains", "value": "None" }
{ "operator": "contains_any", "value": ["A", "B"] }
{ "operator": "contains_all", "value": ["A", "B"] }
```

### Numeric
```json
{ "operator": "greater_than", "value": 18 }
{ "operator": "less_than", "value": 65 }
```

### Existence
```json
{ "operator": "is_answered" }
{ "operator": "is_not_answered" }
```

## Actions Cheat Sheet

### Skip to Question
```json
{
  "action": "goto_question",
  "target_question_id": "question_5"
}
```

### End Survey
```json
{
  "action": "end_survey"
}
```

### Continue (Default)
```json
{
  "action": "continue"
}
```

## Common Patterns

### 1. Skip Logic
```json
{
  "routing_rules": [
    {
      "conditions": [
        { "question_id": "has_kids", "operator": "equals", "value": "No" }
      ],
      "action": "goto_question",
      "target_question_id": "next_section"
    }
  ]
}
```

### 2. Attention Check
```json
{
  "routing_rules": [
    {
      "conditions": [
        { "question_id": "color", "operator": "equals", "value": "FakeColor" }
      ],
      "action": "end_survey"
    }
  ]
}
```

### 3. Screening Question
```json
{
  "routing_rules": [
    {
      "conditions": [
        { "question_id": "age", "operator": "less_than", "value": 18 }
      ],
      "action": "end_survey"
    }
  ]
}
```

### 4. Multi-Select Screening
```json
{
  "routing_rules": [
    {
      "conditions": [
        { "question_id": "products", "operator": "contains", "value": "None" }
      ],
      "action": "end_survey"
    }
  ]
}
```

### 5. Multiple Conditions (AND)
```json
{
  "routing_rules": [
    {
      "conditions": [
        { "question_id": "age", "operator": "greater_than", "value": 18 },
        { "question_id": "region", "operator": "equals", "value": "US" }
      ],
      "action": "goto_question",
      "target_question_id": "us_adult_questions"
    }
  ]
}
```

## Testing Script

```bash
cd backend
poetry run python create_survey_with_routing_example.py
```

## API Endpoint

```
GET /api/submissions/{submission_id}/next-question?current_question_id={id}
```

## Key Points

- ✅ First matching rule wins
- ✅ Conditions use AND logic (all must be true)
- ✅ Default action: continue to next question
- ✅ No database migration needed
- ✅ Backwards compatible
- ✅ Works with all question types

## Documentation

- **Full Guide**: `SURVEY_ROUTING_GUIDE.md`
- **Summary**: `ROUTING_IMPLEMENTATION_SUMMARY.md`
- **Examples**: `backend/create_survey_with_routing_example.py`
