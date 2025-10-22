# Survey Conditional Routing Guide

## Overview

This guide explains how to use conditional routing in surveys to create dynamic survey flows based on respondent answers. Conditional routing enables:

- **Skip Logic**: Route respondents to different questions based on their answers
- **Survey Termination**: End surveys early based on specific responses (attention checks, screening)
- **Conditional Branching**: Show different question paths based on complex conditions
- **Smart Workflows**: Create sophisticated survey flows that adapt to respondent input

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Routing Components](#routing-components)
3. [Condition Operators](#condition-operators)
4. [Routing Actions](#routing-actions)
5. [Examples](#examples)
6. [Best Practices](#best-practices)
7. [API Reference](#api-reference)

---

## How It Works

### Basic Flow

1. Respondent answers a question
2. System checks if the question has `routing_rules`
3. Each routing rule is evaluated in order
4. First matching rule determines the next action:
   - **goto_question**: Jump to a specific question
   - **end_survey**: Terminate survey early
   - **continue**: Proceed to next question in sequence
5. If no rules match, proceed to next question by default

### Architecture

```
Question with Routing Rules
├── Submit Answer → Backend API
├── Backend evaluates routing conditions
│   ├── Check condition #1
│   ├── Check condition #2
│   └── Check condition #N
├── Return routing action
└── Frontend navigates accordingly
```

---

## Routing Components

### Question Structure with Routing

```json
{
  "id": "question_id",
  "question": "Question text?",
  "question_type": "single",
  "required": true,
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
      "target_question_id": "target_question"
    }
  ]
}
```

### Routing Rule Structure

| Field | Type | Description |
|-------|------|-------------|
| `conditions` | Array | List of conditions (all must be true - AND logic) |
| `action` | String | Action to take: `goto_question`, `end_survey`, `continue` |
| `target_question_id` | String | Required if action is `goto_question` |

### Routing Condition Structure

| Field | Type | Description |
|-------|------|-------------|
| `question_id` | String | The question ID to check |
| `operator` | String | Comparison operator (see below) |
| `value` | String/Array/Number | Value to compare against |

---

## Condition Operators

### For Single Choice Questions

#### `equals`
Answer exactly matches the value.

```json
{
  "question_id": "gender",
  "operator": "equals",
  "value": "Male"
}
```

#### `not_equals`
Answer does not match the value.

```json
{
  "question_id": "gender",
  "operator": "not_equals",
  "value": "Prefer not to say"
}
```

### For Multiple Choice Questions

#### `contains`
Selected answers include the specific value.

```json
{
  "question_id": "products",
  "operator": "contains",
  "value": "Product A"
}
```

#### `not_contains`
Selected answers do not include the value.

```json
{
  "question_id": "products",
  "operator": "not_contains",
  "value": "None"
}
```

#### `contains_any`
Selected answers include at least one of the values (OR logic).

```json
{
  "question_id": "interests",
  "operator": "contains_any",
  "value": ["Sports", "Gaming", "Fitness"]
}
```

#### `contains_all`
Selected answers include all of the values (AND logic).

```json
{
  "question_id": "requirements",
  "operator": "contains_all",
  "value": ["Feature A", "Feature B"]
}
```

### For Numeric Comparisons

#### `greater_than`
Numeric value is greater than the threshold.

```json
{
  "question_id": "age",
  "operator": "greater_than",
  "value": 18
}
```

#### `less_than`
Numeric value is less than the threshold.

```json
{
  "question_id": "age",
  "operator": "less_than",
  "value": 65
}
```

### For Any Question Type

#### `is_answered`
Question has been answered.

```json
{
  "question_id": "email",
  "operator": "is_answered"
}
```

#### `is_not_answered`
Question has not been answered.

```json
{
  "question_id": "optional_feedback",
  "operator": "is_not_answered"
}
```

---

## Routing Actions

### `goto_question`
Jump to a specific question by ID.

```json
{
  "action": "goto_question",
  "target_question_id": "demographic_questions"
}
```

**Use cases:**
- Skip irrelevant questions
- Branch to different question paths
- Jump forward based on answers

### `end_survey`
Terminate the survey immediately and automatically mark submission as rejected.

```json
{
  "action": "end_survey"
}
```

**Behavior:**
- Survey ends immediately
- Submission marked as `is_completed = True`
- Submission marked as `is_approved = False` (rejected)
- User sees survey completion page

**Use cases:**
- Attention checks (screening out inattentive respondents)
- Qualification screening (respondent doesn't meet criteria)
- Early termination for disqualified respondents

### `continue`
Explicitly continue to next question in sequence.

```json
{
  "action": "continue"
}
```

**Use cases:**
- Default behavior when conditions are met
- Explicit control flow
- Documentation purposes

---

## Examples

### Example 1: Skip Logic Based on Single Choice

**Scenario:** If respondent has no children, skip questions about children.

```json
{
  "survey_flow": [
    {
      "id": "has_children",
      "question": "Do you have children?",
      "question_type": "single",
      "required": true,
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
          "target_question_id": "employment_status"
        }
      ]
    },
    {
      "id": "children_ages",
      "question": "What are the ages of your children?",
      "question_type": "multi",
      "required": true,
      "options": ["0-5", "6-12", "13-18", "18+"]
    },
    {
      "id": "employment_status",
      "question": "What is your employment status?",
      "question_type": "single",
      "required": true,
      "options": ["Employed", "Unemployed", "Retired"]
    }
  ]
}
```

### Example 2: Survey Termination (Attention Check)

**Scenario:** End survey if respondent selects fake option.

```json
{
  "id": "favorite_drink",
  "question": "Which of these drinks do you prefer?",
  "question_type": "single",
  "required": true,
  "options": [
    "Coffee",
    "Tea",
    "Water",
    "Soda",
    "Flibbertigibbet Juice"  // Fake option
  ],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "favorite_drink",
          "operator": "equals",
          "value": "Flibbertigibbet Juice"
        }
      ],
      "action": "end_survey"
    }
  ]
}
```

### Example 3: Multiple Conditions (AND Logic)

**Scenario:** Show follow-up question only if respondent is 18+ and interested in product.

```json
{
  "id": "product_interest",
  "question": "Are you interested in our new product?",
  "question_type": "single",
  "required": true,
  "options": ["Yes", "No"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "age",
          "operator": "less_than",
          "value": 18
        }
      ],
      "action": "end_survey"
    },
    {
      "conditions": [
        {
          "question_id": "product_interest",
          "operator": "equals",
          "value": "No"
        }
      ],
      "action": "goto_question",
      "target_question_id": "exit_survey"
    }
  ]
}
```

### Example 4: Multi-Select Routing

**Scenario:** Route based on selected products.

```json
{
  "id": "products_used",
  "question": "Which products do you use?",
  "question_type": "multi",
  "required": true,
  "options": ["Product A", "Product B", "Product C", "None"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "products_used",
          "operator": "contains",
          "value": "None"
        }
      ],
      "action": "end_survey"
    },
    {
      "conditions": [
        {
          "question_id": "products_used",
          "operator": "contains",
          "value": "Product A"
        }
      ],
      "action": "goto_question",
      "target_question_id": "product_a_details"
    }
  ]
}
```

### Example 5: Numeric Comparison

**Scenario:** Different question paths based on age.

```json
{
  "id": "age",
  "question": "How old are you?",
  "question_type": "single",
  "required": true,
  "options": ["Under 18", "18-34", "35-54", "55+"],
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "age",
          "operator": "equals",
          "value": "Under 18"
        }
      ],
      "action": "end_survey"
    }
  ]
}
```

---

## Best Practices

### 1. **Test Your Routing Logic**

Always test all possible paths through your survey:
- Test each routing condition
- Verify skip logic works correctly
- Ensure early termination works as expected
- Test with different answer combinations

### 2. **Keep It Simple**

- Avoid overly complex routing logic
- Use clear, descriptive question IDs
- Document your routing logic
- Consider the respondent experience

### 3. **Validate Target Questions**

Ensure all `target_question_id` values:
- Exist in the survey
- Are reachable
- Come after the current question (avoid loops)

### 4. **Use Attention Checks Wisely**

- Don't overuse attention checks
- Make them realistic but obvious
- Consider the respondent's perspective
- Balance quality control with respondent experience

### 5. **Order Matters**

Routing rules are evaluated in order:
- First matching rule wins
- Place specific conditions before general ones
- Consider rule priority carefully

### 6. **Handle Edge Cases**

- What if no conditions match? (Default: continue)
- What if target question doesn't exist? (Fallback: continue)
- What if routing creates a loop? (Avoid by design)

### 7. **Document Your Logic**

Add comments or documentation explaining:
- Why certain routing rules exist
- What each branch accomplishes
- Any business logic requirements

### 8. **Progressive Enhancement**

- Surveys without routing rules still work (sequential)
- Add routing incrementally
- Test after each addition
- Backwards compatible with existing surveys

---

## API Reference

### Get Next Question

**Endpoint:** `GET /api/submissions/{submission_id}/next-question`

**Query Parameters:**
- `current_question_id` (string, required): The ID of the current question

**Response:**

```json
{
  "action": "goto_question",
  "next_question_id": "question_5",
  "question_index": 4,
  "question": {
    "id": "question_5",
    "question": "What is your favorite color?",
    "question_type": "single",
    "required": true,
    "options": ["Red", "Blue", "Green"]
  }
}
```

**Response (Survey End):**

```json
{
  "action": "end_survey",
  "next_question_id": null,
  "question_index": null
}
```

### Create Survey with Routing

**Endpoint:** `POST /api/surveys/`

**Headers:**
- `X-API-Key`: Your API key
- `Content-Type`: application/json

**Body:**

```json
{
  "survey_slug": "my-survey",
  "name": "My Survey",
  "is_active": true,
  "survey_flow": [
    {
      "id": "q1",
      "question": "Question text",
      "question_type": "single",
      "required": true,
      "options": ["Option 1", "Option 2"],
      "routing_rules": [
        {
          "conditions": [
            {
              "question_id": "q1",
              "operator": "equals",
              "value": "Option 1"
            }
          ],
          "action": "goto_question",
          "target_question_id": "q3"
        }
      ]
    }
  ]
}
```

---

## Common Use Cases

### 1. **Demographic Screening**

Screen respondents based on age, location, or other demographics:

```json
{
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "country",
          "operator": "not_equals",
          "value": "United States"
        }
      ],
      "action": "end_survey"
    }
  ]
}
```

### 2. **Product Usage Funnels**

Ask follow-up questions only to relevant users:

```json
{
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "uses_product",
          "operator": "equals",
          "value": "No"
        }
      ],
      "action": "goto_question",
      "target_question_id": "why_not_using"
    }
  ]
}
```

### 3. **Satisfaction Follow-ups**

Ask for details only from dissatisfied customers:

```json
{
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "satisfaction",
          "operator": "equals",
          "value": "Dissatisfied"
        }
      ],
      "action": "goto_question",
      "target_question_id": "improvement_feedback"
    }
  ]
}
```

### 4. **Required Feature Validation**

Ensure respondents select specific required options:

```json
{
  "routing_rules": [
    {
      "conditions": [
        {
          "question_id": "required_features",
          "operator": "not_contains_all",
          "value": ["Feature A", "Feature B"]
        }
      ],
      "action": "end_survey"
    }
  ]
}
```

---

## Troubleshooting

### Routing Not Working

1. **Check question IDs**: Ensure `question_id` in conditions matches actual question IDs
2. **Verify operator**: Use correct operator for question type
3. **Check value format**: Strings for single choice, arrays for multi-choice
4. **Test conditions**: Verify conditions evaluate correctly
5. **Check browser console**: Look for JavaScript errors

### Unexpected Skips

1. **Review rule order**: Earlier rules take precedence
2. **Check condition logic**: Ensure AND logic is correct
3. **Verify target IDs**: Confirm target questions exist
4. **Test all paths**: Try different answer combinations

### Survey Ending Early

1. **Check for end_survey actions**: Review all routing rules
2. **Verify conditions**: Ensure conditions match intended logic
3. **Test with different answers**: Try various response patterns

---

## Example Script

Run the example script to create sample surveys with routing:

```bash
cd backend
poetry run python create_survey_with_routing_example.py
```

This creates two example surveys demonstrating routing features.

---

## Support

For questions or issues:
- Review this documentation
- Check the example surveys
- Examine the routing logic in `backend/app/utils/routing.py`
- Test with the example script

---

## Version History

- **v1.0** (2025-10-22): Initial release
  - Basic routing operators
  - Skip logic
  - Survey termination
  - Multi-condition support
