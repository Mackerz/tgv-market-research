# Survey Conditional Routing - Implementation Summary

## What Was Implemented

I've successfully implemented a comprehensive conditional routing system for your survey platform. This allows surveys to dynamically adapt based on respondent answers.

## Key Features

### 1. **Skip Logic**
- Route respondents to different questions based on their answers
- Example: "How many children do you have?" → If 0, skip to different section

### 2. **Survey Termination**
- End surveys early based on specific responses
- Automatically marks submission as **rejected** (`is_approved = False`)
- Example: Attention checks, screening questions
- If fake option selected → End survey and reject submission

### 3. **Multi-Condition Logic**
- Complex routing rules with multiple conditions (AND logic)
- Support for various operators (equals, contains, greater_than, etc.)

### 4. **Question Types Supported**
- ✅ Single choice (radio buttons)
- ✅ Multiple choice (checkboxes)
- ✅ Free text (with numeric comparisons)
- ✅ Photo questions
- ✅ Video questions

## Files Modified/Created

### Backend Changes

#### New Files
- **`backend/app/utils/routing.py`** (NEW)
  - Core routing evaluation logic
  - Condition evaluation functions
  - Next question determination

- **`backend/create_survey_with_routing_example.py`** (NEW)
  - Example script demonstrating routing
  - Two complete example surveys

#### Modified Files
- **`backend/app/schemas/survey.py`**
  - Added `ConditionOperator` enum (10 operators)
  - Added `RoutingAction` enum (goto_question, end_survey, continue)
  - Added `RoutingCondition` schema
  - Added `RoutingRule` schema
  - Added `routing_rules` field to `SurveyQuestion`

- **`backend/app/api/v1/submissions.py`**
  - Added `/api/submissions/{submission_id}/next-question` endpoint
  - Returns routing information based on current question and answers

### Frontend Changes

#### Modified Files
- **`frontend/src/types/survey.ts`**
  - Added routing type definitions
  - `RoutingCondition`, `RoutingRule`, `NextQuestionResponse` types

- **`frontend/src/lib/api/services/surveys.ts`**
  - Added `getNextQuestion()` service method

- **`frontend/src/hooks/useSurvey.ts`**
  - Updated `nextQuestion()` to use routing logic
  - Handles dynamic navigation based on routing rules

- **`frontend/src/components/survey/QuestionComponent.tsx`**
  - Updated to call routing API after answer submission
  - Handles survey termination and dynamic navigation

### Documentation

- **`SURVEY_ROUTING_GUIDE.md`** (NEW)
  - Comprehensive guide (2,500+ words)
  - All operators explained with examples
  - Best practices and troubleshooting
  - API reference

- **`ROUTING_IMPLEMENTATION_SUMMARY.md`** (NEW, this file)
  - Quick implementation overview

## How It Works

### Flow Diagram

```
User answers question
       ↓
Submit response to backend
       ↓
Check if question has routing_rules?
       ↓
   ┌───YES────┐
   ↓          ↓
Evaluate    Continue to
conditions   next question
   ↓          (default)
Match found?
   ↓
┌──YES─┐──NO──┐
↓              ↓
Execute    Continue to
action     next question
   ↓
goto_question / end_survey / continue
```

### Condition Operators

| Operator | Use Case | Example |
|----------|----------|---------|
| `equals` | Single choice match | `"gender" equals "Male"` |
| `not_equals` | Single choice exclusion | `"region" not_equals "US"` |
| `contains` | Multi-choice includes | `"products" contains "Product A"` |
| `not_contains` | Multi-choice excludes | `"interests" not_contains "None"` |
| `contains_any` | Multi-choice OR logic | `"features" contains_any ["A", "B"]` |
| `contains_all` | Multi-choice AND logic | `"requirements" contains_all ["A", "B"]` |
| `greater_than` | Numeric comparison | `"age" greater_than 18` |
| `less_than` | Numeric comparison | `"age" less_than 65` |
| `is_answered` | Question was answered | `"email" is_answered` |
| `is_not_answered` | Question not answered | `"optional" is_not_answered` |

## Example Usage

### Simple Skip Logic

```json
{
  "id": "has_children",
  "question": "Do you have children?",
  "question_type": "single",
  "options": ["Yes", "No"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "has_children",
          "operator": "equals",
          "value": "No"
        }
      ],
      "action": "goto_question",
      "target_question_id": "next_section"
    }
  ]
}
```

### Attention Check (Survey Termination with Rejection)

```json
{
  "id": "favorite_color",
  "question": "What is your favorite color?",
  "question_type": "single",
  "options": ["Red", "Blue", "Green", "Flibbertigibbet"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "favorite_color",
          "operator": "equals",
          "value": "Flibbertigibbet"
        }
      ],
      "action": "end_survey"
    }
  ]
}
```

**Result:** Survey ends immediately and submission is marked as rejected (`is_approved = False`).

## Testing

### Run Example Script

```bash
cd backend
poetry run python create_survey_with_routing_example.py
```

This creates two example surveys:
1. **family-lifestyle-routing** - Demonstrates skip logic
2. **product-feedback-advanced** - Demonstrates complex routing

### Test the Surveys

1. Start the backend: `cd backend && make dev`
2. Start the frontend: `cd frontend && npm run dev`
3. Visit: `http://localhost:3000/survey/family-lifestyle-routing`
4. Try different answer combinations to see routing in action

## Key Benefits

### For Survey Creators
✅ More sophisticated survey flows
✅ Better data quality through attention checks
✅ Reduced respondent burden (skip irrelevant questions)
✅ Flexible branching logic
✅ No code changes needed - just JSON configuration

### For Respondents
✅ Shorter, more relevant surveys
✅ Better user experience
✅ Less time wasted on irrelevant questions
✅ Natural conversation flow

### Technical Benefits
✅ Backwards compatible (existing surveys work unchanged)
✅ No database migration needed (JSON field)
✅ Type-safe with Pydantic validation
✅ Evaluated server-side (secure)
✅ Frontend/backend separation maintained

## API Endpoints

### Get Next Question
```
GET /api/submissions/{submission_id}/next-question?current_question_id={id}
```

**Response:**
```json
{
  "action": "goto_question",
  "next_question_id": "question_5",
  "question_index": 4,
  "question": { ... }
}
```

or

```json
{
  "action": "end_survey",
  "next_question_id": null,
  "question_index": null
}
```

## Migration Path

### For Existing Surveys
- No changes needed
- Existing surveys continue to work sequentially
- Add `routing_rules` when ready

### For New Surveys
1. Design survey flow
2. Identify branching points
3. Add `routing_rules` to questions
4. Test all paths
5. Deploy

## Common Patterns

### Pattern 1: Skip Section
Skip entire sections based on a screening question.

### Pattern 2: Attention Check
End survey if fake option selected.

### Pattern 3: Follow-up Questions
Ask details only to specific respondents.

### Pattern 4: Qualification Screening
Filter respondents based on demographics.

### Pattern 5: Product Usage Funnels
Different paths for users/non-users.

## Best Practices

1. **Test Thoroughly**: Try all answer combinations
2. **Keep It Simple**: Avoid overly complex logic
3. **Document Your Logic**: Explain why rules exist
4. **Validate Targets**: Ensure target questions exist
5. **Order Matters**: First matching rule wins
6. **Handle Edge Cases**: What if no rules match?
7. **User Experience First**: Consider respondent perspective
8. **Progressive Enhancement**: Add routing incrementally

## Troubleshooting

### Routing Not Working?
- Check question IDs match
- Verify operator is correct for question type
- Check value format (string vs array)
- Look at browser console for errors

### Survey Ending Early?
- Review all `end_survey` actions
- Check condition logic
- Test with different answers

### Unexpected Skips?
- Review rule order (first match wins)
- Verify condition logic
- Check target question IDs

## Next Steps

1. **Read the Guide**: See `SURVEY_ROUTING_GUIDE.md` for detailed documentation
2. **Run Examples**: Test the example surveys
3. **Create Your First Routed Survey**: Use the patterns provided
4. **Test Thoroughly**: Try all answer paths
5. **Deploy**: Roll out to production

## Support

- **Documentation**: `SURVEY_ROUTING_GUIDE.md`
- **Examples**: `backend/create_survey_with_routing_example.py`
- **Code**: `backend/app/utils/routing.py`

## Version Info

- **Implemented**: October 22, 2025
- **Backend**: Python/FastAPI
- **Frontend**: Next.js/TypeScript
- **Database**: PostgreSQL (no schema changes needed)

---

**Status**: ✅ Fully Implemented and Ready to Use

The conditional routing system is production-ready and backwards compatible with existing surveys. No database migrations required - just start using `routing_rules` in your survey flow!
