"""
Survey routing logic utilities.
Evaluates routing conditions and determines next question based on answers.
"""
from typing import Dict, List, Optional, Any, Union
from app.schemas.survey import (
    SurveyQuestion,
    RoutingRule,
    RoutingCondition,
    ConditionOperator,
    RoutingAction,
    Response
)


def evaluate_condition(
    condition: RoutingCondition,
    responses: Dict[str, Any]
) -> bool:
    """
    Evaluate a single routing condition against collected responses.

    Args:
        condition: The routing condition to evaluate
        responses: Dictionary mapping question_id -> answer data
                   Format: {
                       "question_id": {
                           "single_answer": "value",
                           "multiple_choice_answer": ["value1", "value2"],
                           "free_text_answer": "text"
                       }
                   }

    Returns:
        True if condition is satisfied, False otherwise
    """
    question_id = condition.question_id
    operator = condition.operator
    expected_value = condition.value

    # Check if question has been answered
    if question_id not in responses:
        return operator == ConditionOperator.IS_NOT_ANSWERED

    response_data = responses[question_id]

    # IS_ANSWERED / IS_NOT_ANSWERED operators
    if operator == ConditionOperator.IS_ANSWERED:
        return True  # Question exists in responses
    elif operator == ConditionOperator.IS_NOT_ANSWERED:
        return False  # Question exists in responses

    # Get the actual answer based on question type
    single_answer = response_data.get("single_answer")
    multiple_choice_answer = response_data.get("multiple_choice_answer")
    free_text_answer = response_data.get("free_text_answer")

    # EQUALS operator (for single choice)
    if operator == ConditionOperator.EQUALS:
        if single_answer is not None:
            return single_answer == expected_value
        return False

    # NOT_EQUALS operator (for single choice)
    elif operator == ConditionOperator.NOT_EQUALS:
        if single_answer is not None:
            return single_answer != expected_value
        return False

    # CONTAINS operator (for multi choice)
    elif operator == ConditionOperator.CONTAINS:
        if multiple_choice_answer is not None:
            return expected_value in multiple_choice_answer
        return False

    # NOT_CONTAINS operator (for multi choice)
    elif operator == ConditionOperator.NOT_CONTAINS:
        if multiple_choice_answer is not None:
            return expected_value not in multiple_choice_answer
        return True  # If no answer, it doesn't contain the value

    # CONTAINS_ANY operator (for multi choice - OR logic)
    elif operator == ConditionOperator.CONTAINS_ANY:
        if multiple_choice_answer is not None and isinstance(expected_value, list):
            return any(val in multiple_choice_answer for val in expected_value)
        return False

    # CONTAINS_ALL operator (for multi choice - AND logic)
    elif operator == ConditionOperator.CONTAINS_ALL:
        if multiple_choice_answer is not None and isinstance(expected_value, list):
            return all(val in multiple_choice_answer for val in expected_value)
        return False

    # GREATER_THAN operator (numeric comparison)
    elif operator == ConditionOperator.GREATER_THAN:
        try:
            if single_answer is not None:
                # Try to parse answer as number
                actual_num = float(single_answer)
                expected_num = float(expected_value)
                return actual_num > expected_num
            elif free_text_answer is not None:
                actual_num = float(free_text_answer)
                expected_num = float(expected_value)
                return actual_num > expected_num
        except (ValueError, TypeError):
            return False
        return False

    # LESS_THAN operator (numeric comparison)
    elif operator == ConditionOperator.LESS_THAN:
        try:
            if single_answer is not None:
                actual_num = float(single_answer)
                expected_num = float(expected_value)
                return actual_num < expected_num
            elif free_text_answer is not None:
                actual_num = float(free_text_answer)
                expected_num = float(expected_value)
                return actual_num < expected_num
        except (ValueError, TypeError):
            return False
        return False

    return False


def evaluate_routing_rule(
    rule: RoutingRule,
    responses: Dict[str, Any]
) -> bool:
    """
    Evaluate a routing rule by checking all its conditions (AND logic).

    Args:
        rule: The routing rule to evaluate
        responses: Dictionary mapping question_id -> answer data

    Returns:
        True if all conditions in the rule are satisfied, False otherwise
    """
    # All conditions must be true (AND logic)
    return all(
        evaluate_condition(condition, responses)
        for condition in rule.conditions
    )


def get_next_question_id(
    current_question: SurveyQuestion,
    all_questions: List[SurveyQuestion],
    responses: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Determine the next question ID based on routing rules.

    Args:
        current_question: The question that was just answered
        all_questions: All questions in the survey (in order)
        responses: Dictionary mapping question_id -> answer data

    Returns:
        Dictionary with routing information:
        {
            "action": "goto_question" | "end_survey" | "continue",
            "next_question_id": str (if action is goto_question or continue),
            "question_index": int (if action is goto_question or continue)
        }
        Returns None if survey should end
    """
    # If no routing rules, continue to next question in sequence
    if not current_question.routing_rules:
        current_index = next(
            (i for i, q in enumerate(all_questions) if q.id == current_question.id),
            None
        )

        if current_index is None or current_index >= len(all_questions) - 1:
            # Last question or question not found
            return {"action": "end_survey", "next_question_id": None, "question_index": None}

        next_question = all_questions[current_index + 1]
        return {
            "action": "continue",
            "next_question_id": next_question.id,
            "question_index": current_index + 1
        }

    # Evaluate routing rules in order
    for rule in current_question.routing_rules:
        if evaluate_routing_rule(rule, responses):
            # Rule matched!
            if rule.action == RoutingAction.END_SURVEY:
                return {"action": "end_survey", "next_question_id": None, "question_index": None}

            elif rule.action == RoutingAction.GOTO_QUESTION:
                # Find the target question index
                target_index = next(
                    (i for i, q in enumerate(all_questions) if q.id == rule.target_question_id),
                    None
                )

                if target_index is None:
                    # Target question not found, continue to next in sequence
                    current_index = next(
                        (i for i, q in enumerate(all_questions) if q.id == current_question.id),
                        None
                    )
                    if current_index is not None and current_index < len(all_questions) - 1:
                        next_question = all_questions[current_index + 1]
                        return {
                            "action": "continue",
                            "next_question_id": next_question.id,
                            "question_index": current_index + 1
                        }
                    return {"action": "end_survey", "next_question_id": None, "question_index": None}

                return {
                    "action": "goto_question",
                    "next_question_id": rule.target_question_id,
                    "question_index": target_index
                }

            elif rule.action == RoutingAction.CONTINUE:
                # Explicit continue - go to next question in sequence
                current_index = next(
                    (i for i, q in enumerate(all_questions) if q.id == current_question.id),
                    None
                )

                if current_index is None or current_index >= len(all_questions) - 1:
                    return {"action": "end_survey", "next_question_id": None, "question_index": None}

                next_question = all_questions[current_index + 1]
                return {
                    "action": "continue",
                    "next_question_id": next_question.id,
                    "question_index": current_index + 1
                }

    # No rules matched, continue to next question in sequence (default behavior)
    current_index = next(
        (i for i, q in enumerate(all_questions) if q.id == current_question.id),
        None
    )

    if current_index is None or current_index >= len(all_questions) - 1:
        return {"action": "end_survey", "next_question_id": None, "question_index": None}

    next_question = all_questions[current_index + 1]
    return {
        "action": "continue",
        "next_question_id": next_question.id,
        "question_index": current_index + 1
    }


def build_response_dict(responses: List[Response]) -> Dict[str, Any]:
    """
    Convert list of Response objects to dictionary format for routing evaluation.

    Args:
        responses: List of Response objects from database

    Returns:
        Dictionary mapping question_id -> answer data
    """
    response_dict = {}

    for response in responses:
        # Extract question_id from the question text
        # Note: We'll need to match responses to question IDs
        # For now, we'll use a simple approach assuming question text is unique
        response_dict[response.question] = {
            "single_answer": response.single_answer,
            "multiple_choice_answer": response.multiple_choice_answer,
            "free_text_answer": response.free_text_answer,
            "photo_url": response.photo_url,
            "video_url": response.video_url
        }

    return response_dict
