"""
Survey routing logic utilities - Refactored version.
Evaluates routing conditions and determines next question based on answers.

This module has been refactored to:
1. Eliminate DRY violations
2. Improve performance (O(n+m) instead of O(n*m))
3. Add input validation
4. Follow SOLID principles
5. Improve maintainability
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


# Constants for routing actions
class RoutingActions:
    """Constants for routing action strings."""
    END_SURVEY = "end_survey"
    GOTO_QUESTION = "goto_question"
    CONTINUE = "continue"


def _validate_operator_value_compatibility(
    operator: ConditionOperator,
    value: Any
) -> None:
    """
    Validate that the expected value type matches the operator.
    Prevents DoS attacks with huge values and ensures type safety.

    Args:
        operator: The condition operator
        value: The expected value

    Raises:
        ValueError: If value type is incompatible with operator or exceeds limits
    """
    if operator in [ConditionOperator.CONTAINS_ANY, ConditionOperator.CONTAINS_ALL]:
        if not isinstance(value, list):
            raise ValueError(
                f"Operator {operator} requires a list value, got {type(value).__name__}"
            )
        if len(value) > 100:  # Prevent DoS
            raise ValueError(f"Value list too large: {len(value)} items (max 100)")

    elif operator in [ConditionOperator.GREATER_THAN, ConditionOperator.LESS_THAN]:
        try:
            float(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Operator {operator} requires a numeric value, got {value}"
            )

    elif operator in [ConditionOperator.EQUALS, ConditionOperator.NOT_EQUALS,
                      ConditionOperator.CONTAINS, ConditionOperator.NOT_CONTAINS]:
        if not isinstance(value, (str, int, float, bool, type(None))):
            raise ValueError(
                f"Operator {operator} requires a scalar value, got {type(value).__name__}"
            )
        if isinstance(value, str) and len(value) > 1000:  # Prevent DoS
            raise ValueError(f"Value string too large: {len(value)} chars (max 1000)")


def _compare_numeric(
    single_answer: Optional[str],
    free_text_answer: Optional[str],
    expected_value: Any,
    comparison_func: callable
) -> bool:
    """
    Helper function for numeric comparisons (DRY improvement).

    Args:
        single_answer: Single choice answer
        free_text_answer: Free text answer
        expected_value: Expected numeric value
        comparison_func: Function to perform comparison (e.g., lambda a, e: a > e)

    Returns:
        bool: Result of comparison, False if conversion fails
    """
    try:
        if single_answer is not None:
            actual_num = float(single_answer)
            expected_num = float(expected_value)
            return comparison_func(actual_num, expected_num)
        elif free_text_answer is not None:
            actual_num = float(free_text_answer)
            expected_num = float(expected_value)
            return comparison_func(actual_num, expected_num)
    except (ValueError, TypeError):
        return False
    return False


def evaluate_condition(
    condition: RoutingCondition,
    responses: Dict[str, Any]
) -> bool:
    """
    Evaluate a single routing condition against collected responses.

    The function checks whether a specific condition is satisfied based on
    the user's responses. It supports various operators for different question
    types (single choice, multiple choice, numeric comparisons, etc.).

    Args:
        condition: The routing condition to evaluate. Contains:
            - question_id (str): ID of the question to check
            - operator (ConditionOperator): The comparison operator
            - value (Any): The expected value to compare against

        responses: Dictionary mapping question IDs to response data.
            Format: {
                "question_123": {
                    "single_answer": "Yes",
                    "multiple_choice_answer": ["A", "B"],
                    "free_text_answer": "text here",
                    "photo_url": "https://...",
                    "video_url": "https://..."
                }
            }

    Returns:
        bool: True if the condition is satisfied, False otherwise.

    Examples:
        >>> condition = RoutingCondition(
        ...     question_id="q1",
        ...     operator=ConditionOperator.EQUALS,
        ...     value="Yes"
        ... )
        >>> responses = {"q1": {"single_answer": "Yes"}}
        >>> evaluate_condition(condition, responses)
        True

    Raises:
        ValueError: If operator and value types are incompatible
    """
    # Validate input
    _validate_operator_value_compatibility(condition.operator, condition.value)

    question_id = condition.question_id
    operator = condition.operator
    expected_value = condition.value

    # Check if question has been answered
    if question_id not in responses:
        return operator == ConditionOperator.IS_NOT_ANSWERED

    response_data = responses[question_id]

    # IS_ANSWERED / IS_NOT_ANSWERED operators
    if operator == ConditionOperator.IS_ANSWERED:
        return True
    elif operator == ConditionOperator.IS_NOT_ANSWERED:
        return False

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
        return True

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

    # GREATER_THAN operator (numeric comparison) - Using DRY helper
    elif operator == ConditionOperator.GREATER_THAN:
        return _compare_numeric(
            single_answer, free_text_answer, expected_value,
            lambda a, e: a > e
        )

    # LESS_THAN operator (numeric comparison) - Using DRY helper
    elif operator == ConditionOperator.LESS_THAN:
        return _compare_numeric(
            single_answer, free_text_answer, expected_value,
            lambda a, e: a < e
        )

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
        bool: True if all conditions in the rule are satisfied, False otherwise
    """
    # All conditions must be true (AND logic)
    return all(
        evaluate_condition(condition, responses)
        for condition in rule.conditions
    )


def _find_question_index(question_id: str, all_questions: List[SurveyQuestion]) -> Optional[int]:
    """
    Find the index of a question by its ID.

    DRY helper to eliminate repeated search logic.

    Args:
        question_id: ID of the question to find
        all_questions: List of all questions in the survey

    Returns:
        int: Index of the question, or None if not found
    """
    return next(
        (i for i, q in enumerate(all_questions) if q.id == question_id),
        None
    )


def _build_question_index_map(all_questions: List[SurveyQuestion]) -> Dict[str, int]:
    """
    Build a dictionary mapping question IDs to their indices for O(1) lookup.

    Performance improvement: O(n) to build, then O(1) lookups instead of O(n) searches.

    Args:
        all_questions: List of all questions in the survey

    Returns:
        Dict mapping question_id -> index
    """
    return {q.id: i for i, q in enumerate(all_questions)}


def _get_next_sequential_question(
    current_question: SurveyQuestion,
    all_questions: List[SurveyQuestion],
    question_index_map: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Get the next question in sequential order (DRY helper).

    This function was duplicated 4 times in the original code.

    Args:
        current_question: The current question
        all_questions: List of all questions
        question_index_map: Optional pre-built index map for performance

    Returns:
        Dict with routing information
    """
    if question_index_map:
        current_index = question_index_map.get(current_question.id)
    else:
        current_index = _find_question_index(current_question.id, all_questions)

    if current_index is None or current_index >= len(all_questions) - 1:
        return {
            "action": RoutingActions.END_SURVEY,
            "next_question_id": None,
            "question_index": None
        }

    next_question = all_questions[current_index + 1]
    return {
        "action": RoutingActions.CONTINUE,
        "next_question_id": next_question.id,
        "question_index": current_index + 1
    }


def _find_matching_rule(
    rules: List[RoutingRule],
    responses: Dict[str, Any]
) -> Optional[RoutingRule]:
    """
    Find the first rule that matches current responses (SRP improvement).

    Args:
        rules: List of routing rules to evaluate
        responses: Dictionary mapping question_id -> answer data

    Returns:
        The first matching rule, or None if no rules match
    """
    for rule in rules:
        if evaluate_routing_rule(rule, responses):
            return rule
    return None


def _execute_routing_action(
    rule: RoutingRule,
    current_question: SurveyQuestion,
    all_questions: List[SurveyQuestion],
    question_index_map: Dict[str, int]
) -> Dict[str, Any]:
    """
    Execute the action specified by a routing rule (SRP improvement).

    Args:
        rule: The routing rule to execute
        current_question: The current question
        all_questions: List of all questions
        question_index_map: Pre-built index map for performance

    Returns:
        Dict with routing information
    """
    if rule.action == RoutingAction.END_SURVEY:
        return {
            "action": RoutingActions.END_SURVEY,
            "next_question_id": None,
            "question_index": None
        }

    elif rule.action == RoutingAction.GOTO_QUESTION:
        target_index = question_index_map.get(rule.target_question_id)

        if target_index is None:
            # Target not found, fallback to sequential
            return _get_next_sequential_question(current_question, all_questions, question_index_map)

        return {
            "action": RoutingActions.GOTO_QUESTION,
            "next_question_id": rule.target_question_id,
            "question_index": target_index
        }

    elif rule.action == RoutingAction.CONTINUE:
        return _get_next_sequential_question(current_question, all_questions, question_index_map)

    # Unknown action, fallback to sequential
    return _get_next_sequential_question(current_question, all_questions, question_index_map)


def get_next_question_id(
    current_question: SurveyQuestion,
    all_questions: List[SurveyQuestion],
    responses: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determine the next question ID based on routing rules.

    Refactored to follow SRP - delegates to helper functions.
    Performance improved with O(1) index lookups.

    Args:
        current_question: The question that was just answered
        all_questions: All questions in the survey (in order)
        responses: Dictionary mapping question_id -> answer data format:
            {
                "question_id": {
                    "single_answer": str,
                    "multiple_choice_answer": List[str],
                    "free_text_answer": str,
                    "photo_url": str,
                    "video_url": str
                }
            }

    Returns:
        Dictionary with routing information:
        {
            "action": "goto_question" | "end_survey" | "continue",
            "next_question_id": str (if action is goto_question or continue),
            "question_index": int (if action is goto_question or continue)
        }
    """
    # Build question index map for O(1) lookups (performance improvement)
    question_index_map = _build_question_index_map(all_questions)

    # If no routing rules, continue sequentially
    if not current_question.routing_rules:
        return _get_next_sequential_question(current_question, all_questions, question_index_map)

    # Find first matching rule
    matched_rule = _find_matching_rule(current_question.routing_rules, responses)

    # If no rules matched, continue sequentially
    if not matched_rule:
        return _get_next_sequential_question(current_question, all_questions, question_index_map)

    # Execute the matched rule's action
    return _execute_routing_action(matched_rule, current_question, all_questions, question_index_map)


def build_response_dict(
    responses: List[Response],
    survey_questions: List[SurveyQuestion]
) -> Dict[str, Any]:
    """
    Convert list of Response objects to dictionary format for routing evaluation.
    Maps responses by question ID (not question text) for security and performance.

    PERFORMANCE IMPROVEMENT: O(n+m) instead of O(n*m)
    - Builds question map first: O(m)
    - Maps responses: O(n)
    - Total: O(n+m) vs original O(n*m)

    For 50 questions and 50 responses: 100 operations vs 2,500 operations (96% improvement)

    Args:
        responses: List of Response objects from database
        survey_questions: List of SurveyQuestion objects from survey flow

    Returns:
        Dictionary mapping question_id -> answer data
    """
    # Build question lookup map: O(m) - Performance improvement
    question_map = {q.question: q for q in survey_questions}

    # Map responses: O(n) instead of O(n*m)
    response_dict = {}

    for response in responses:
        # If response has question_id, use it directly (best performance)
        if hasattr(response, 'question_id') and response.question_id:
            response_dict[response.question_id] = {
                "single_answer": response.single_answer,
                "multiple_choice_answer": response.multiple_choice_answer,
                "free_text_answer": response.free_text_answer,
                "photo_url": response.photo_url,
                "video_url": response.video_url
            }
        else:
            # Fallback to question text lookup (for backward compatibility)
            # This is O(1) lookup now instead of O(m) search
            matching_question = question_map.get(response.question)

            if matching_question:
                response_dict[matching_question.id] = {
                    "single_answer": response.single_answer,
                    "multiple_choice_answer": response.multiple_choice_answer,
                    "free_text_answer": response.free_text_answer,
                    "photo_url": response.photo_url,
                    "video_url": response.video_url
                }

    return response_dict
