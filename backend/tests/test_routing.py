"""
Unit tests for survey routing logic.
Tests condition evaluation, routing rules, and next question determination.
"""
import pytest
from app.utils.routing_refactored import (
    evaluate_condition,
    evaluate_routing_rule,
    get_next_question_id,
    RoutingActions,
)
from app.schemas.survey import (
    SurveyQuestion,
    RoutingRule,
    RoutingCondition,
    ConditionOperator,
    RoutingAction,
)


class TestEvaluateCondition:
    """Test individual condition evaluation"""

    def test_equals_operator_true(self):
        """Test equals operator with matching value"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.EQUALS,
            value="Option A"
        )
        responses = {"q1": {"single_answer": "Option A"}}

        assert evaluate_condition(condition, responses) is True

    def test_equals_operator_false(self):
        """Test equals operator with non-matching value"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.EQUALS,
            value="Option A"
        )
        responses = {"q1": {"single_answer": "Option B"}}

        assert evaluate_condition(condition, responses) is False

    def test_not_equals_operator_true(self):
        """Test not_equals operator"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.NOT_EQUALS,
            value="Option A"
        )
        responses = {"q1": {"single_answer": "Option B"}}

        assert evaluate_condition(condition, responses) is True

    def test_contains_operator_true(self):
        """Test contains operator for multi-choice"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS,
            value="Option A"
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is True

    def test_contains_operator_false(self):
        """Test contains operator when value not in list"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS,
            value="Option C"
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is False

    def test_not_contains_operator_true(self):
        """Test not_contains operator"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.NOT_CONTAINS,
            value="Option C"
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is True

    def test_contains_any_operator_true(self):
        """Test contains_any operator (OR logic)"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS_ANY,
            value=["Option A", "Option C"]
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is True

    def test_contains_any_operator_false(self):
        """Test contains_any when none match"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS_ANY,
            value=["Option C", "Option D"]
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is False

    def test_contains_all_operator_true(self):
        """Test contains_all operator (AND logic)"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS_ALL,
            value=["Option A", "Option B"]
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B", "Option C"]}}

        assert evaluate_condition(condition, responses) is True

    def test_contains_all_operator_false(self):
        """Test contains_all when not all match"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.CONTAINS_ALL,
            value=["Option A", "Option C"]
        )
        responses = {"q1": {"multiple_choice_answer": ["Option A", "Option B"]}}

        assert evaluate_condition(condition, responses) is False

    def test_greater_than_operator_true(self):
        """Test greater_than operator with numeric values"""
        condition = RoutingCondition(
            question_id="age",
            operator=ConditionOperator.GREATER_THAN,
            value=18
        )
        responses = {"age": {"single_answer": "25"}}

        assert evaluate_condition(condition, responses) is True

    def test_greater_than_operator_false(self):
        """Test greater_than operator when value is less"""
        condition = RoutingCondition(
            question_id="age",
            operator=ConditionOperator.GREATER_THAN,
            value=18
        )
        responses = {"age": {"single_answer": "15"}}

        assert evaluate_condition(condition, responses) is False

    def test_less_than_operator_true(self):
        """Test less_than operator"""
        condition = RoutingCondition(
            question_id="age",
            operator=ConditionOperator.LESS_THAN,
            value=65
        )
        responses = {"age": {"single_answer": "30"}}

        assert evaluate_condition(condition, responses) is True

    def test_less_than_operator_false(self):
        """Test less_than operator when value is greater"""
        condition = RoutingCondition(
            question_id="age",
            operator=ConditionOperator.LESS_THAN,
            value=65
        )
        responses = {"age": {"single_answer": "70"}}

        assert evaluate_condition(condition, responses) is False

    def test_is_answered_operator_true(self):
        """Test is_answered operator"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.IS_ANSWERED
        )
        responses = {"q1": {"single_answer": "Option A"}}

        assert evaluate_condition(condition, responses) is True

    def test_is_answered_operator_false(self):
        """Test is_answered when question not answered"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.IS_ANSWERED
        )
        responses = {}

        assert evaluate_condition(condition, responses) is False

    def test_is_not_answered_operator_true(self):
        """Test is_not_answered operator"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.IS_NOT_ANSWERED
        )
        responses = {}

        assert evaluate_condition(condition, responses) is True

    def test_is_not_answered_operator_false(self):
        """Test is_not_answered when question is answered"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.IS_NOT_ANSWERED
        )
        responses = {"q1": {"single_answer": "Option A"}}

        assert evaluate_condition(condition, responses) is False

    def test_numeric_comparison_with_free_text(self):
        """Test numeric comparison with free text answer"""
        condition = RoutingCondition(
            question_id="num_children",
            operator=ConditionOperator.GREATER_THAN,
            value=0
        )
        responses = {"num_children": {"free_text_answer": "2"}}

        assert evaluate_condition(condition, responses) is True

    def test_invalid_numeric_comparison(self):
        """Test numeric comparison with non-numeric value"""
        condition = RoutingCondition(
            question_id="q1",
            operator=ConditionOperator.GREATER_THAN,
            value=18
        )
        responses = {"q1": {"single_answer": "invalid"}}

        assert evaluate_condition(condition, responses) is False


class TestEvaluateRoutingRule:
    """Test routing rule evaluation with multiple conditions"""

    def test_single_condition_true(self):
        """Test rule with single matching condition"""
        rule = RoutingRule(
            conditions=[
                RoutingCondition(
                    question_id="q1",
                    operator=ConditionOperator.EQUALS,
                    value="Yes"
                )
            ],
            action=RoutingAction.GOTO_QUESTION,
            target_question_id="q3"
        )
        responses = {"q1": {"single_answer": "Yes"}}

        assert evaluate_routing_rule(rule, responses) is True

    def test_single_condition_false(self):
        """Test rule with single non-matching condition"""
        rule = RoutingRule(
            conditions=[
                RoutingCondition(
                    question_id="q1",
                    operator=ConditionOperator.EQUALS,
                    value="Yes"
                )
            ],
            action=RoutingAction.GOTO_QUESTION,
            target_question_id="q3"
        )
        responses = {"q1": {"single_answer": "No"}}

        assert evaluate_routing_rule(rule, responses) is False

    def test_multiple_conditions_all_true(self):
        """Test rule with multiple conditions (AND logic) - all true"""
        rule = RoutingRule(
            conditions=[
                RoutingCondition(
                    question_id="age",
                    operator=ConditionOperator.GREATER_THAN,
                    value=18
                ),
                RoutingCondition(
                    question_id="region",
                    operator=ConditionOperator.EQUALS,
                    value="US"
                )
            ],
            action=RoutingAction.GOTO_QUESTION,
            target_question_id="q5"
        )
        responses = {
            "age": {"single_answer": "25"},
            "region": {"single_answer": "US"}
        }

        assert evaluate_routing_rule(rule, responses) is True

    def test_multiple_conditions_one_false(self):
        """Test rule with multiple conditions - one false"""
        rule = RoutingRule(
            conditions=[
                RoutingCondition(
                    question_id="age",
                    operator=ConditionOperator.GREATER_THAN,
                    value=18
                ),
                RoutingCondition(
                    question_id="region",
                    operator=ConditionOperator.EQUALS,
                    value="US"
                )
            ],
            action=RoutingAction.GOTO_QUESTION,
            target_question_id="q5"
        )
        responses = {
            "age": {"single_answer": "25"},
            "region": {"single_answer": "UK"}  # This doesn't match
        }

        assert evaluate_routing_rule(rule, responses) is False


class TestGetNextQuestionId:
    """Test next question determination based on routing rules"""

    def test_no_routing_rules_sequential(self):
        """Test sequential navigation without routing rules"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["Yes", "No"]
            ),
            SurveyQuestion(
                id="q2",
                question="Question 2",
                question_type="single",
                required=True,
                options=["A", "B"]
            ),
            SurveyQuestion(
                id="q3",
                question="Question 3",
                question_type="single",
                required=True,
                options=["X", "Y"]
            )
        ]

        current_question = questions[0]
        responses = {}

        result = get_next_question_id(current_question, questions, responses)

        assert result["action"] == "continue"
        assert result["next_question_id"] == "q2"
        assert result["question_index"] == 1

    def test_no_routing_rules_last_question(self):
        """Test sequential navigation on last question"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["Yes", "No"]
            )
        ]

        current_question = questions[0]
        responses = {}

        result = get_next_question_id(current_question, questions, responses)

        assert result["action"] == "end_survey"
        assert result["next_question_id"] is None

    def test_routing_rule_goto_question(self):
        """Test routing rule that jumps to specific question"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Do you have children?",
                question_type="single",
                required=True,
                options=["Yes", "No"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="No"
                            )
                        ],
                        action=RoutingAction.GOTO_QUESTION,
                        target_question_id="q4"
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="Children ages?",
                question_type="multi",
                required=True,
                options=["0-5", "6-12", "13-18"]
            ),
            SurveyQuestion(
                id="q3",
                question="Children activities?",
                question_type="free_text",
                required=True
            ),
            SurveyQuestion(
                id="q4",
                question="Employment status?",
                question_type="single",
                required=True,
                options=["Employed", "Unemployed"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "No"}}

        result = get_next_question_id(current_question, questions, responses)

        assert result["action"] == "goto_question"
        assert result["next_question_id"] == "q4"
        assert result["question_index"] == 3

    def test_routing_rule_end_survey(self):
        """Test routing rule that ends survey early"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Which product?",
                question_type="single",
                required=True,
                options=["Product A", "Product B", "None"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="None"
                            )
                        ],
                        action=RoutingAction.END_SURVEY
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="How satisfied?",
                question_type="single",
                required=True,
                options=["Very", "Somewhat", "Not"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "None"}}

        result = get_next_question_id(current_question, questions, responses)

        assert result["action"] == "end_survey"
        assert result["next_question_id"] is None

    def test_routing_rule_continue_action(self):
        """Test routing rule with explicit continue action"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["A", "B"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="A"
                            )
                        ],
                        action=RoutingAction.CONTINUE
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="Question 2",
                question_type="single",
                required=True,
                options=["X", "Y"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "A"}}

        result = get_next_question_id(current_question, questions, responses)

        assert result["action"] == "continue"
        assert result["next_question_id"] == "q2"
        assert result["question_index"] == 1

    def test_routing_rule_no_match_default_behavior(self):
        """Test default behavior when no routing rules match"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["A", "B", "C"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="A"
                            )
                        ],
                        action=RoutingAction.END_SURVEY
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="Question 2",
                question_type="single",
                required=True,
                options=["X", "Y"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "B"}}  # Doesn't match routing rule

        result = get_next_question_id(current_question, questions, responses)

        # Should continue to next question by default
        assert result["action"] == "continue"
        assert result["next_question_id"] == "q2"

    def test_routing_rule_first_match_wins(self):
        """Test that first matching rule is applied"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["A", "B"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="A"
                            )
                        ],
                        action=RoutingAction.END_SURVEY
                    ),
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="A"
                            )
                        ],
                        action=RoutingAction.GOTO_QUESTION,
                        target_question_id="q3"
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="Question 2",
                question_type="single",
                required=True,
                options=["X", "Y"]
            ),
            SurveyQuestion(
                id="q3",
                question="Question 3",
                question_type="single",
                required=True,
                options=["M", "N"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "A"}}

        result = get_next_question_id(current_question, questions, responses)

        # First rule (end_survey) should win
        assert result["action"] == "end_survey"

    def test_routing_rule_invalid_target_fallback(self):
        """Test fallback behavior when target question doesn't exist"""
        questions = [
            SurveyQuestion(
                id="q1",
                question="Question 1",
                question_type="single",
                required=True,
                options=["A", "B"],
                routing_rules=[
                    RoutingRule(
                        conditions=[
                            RoutingCondition(
                                question_id="q1",
                                operator=ConditionOperator.EQUALS,
                                value="A"
                            )
                        ],
                        action=RoutingAction.GOTO_QUESTION,
                        target_question_id="q99"  # Doesn't exist
                    )
                ]
            ),
            SurveyQuestion(
                id="q2",
                question="Question 2",
                question_type="single",
                required=True,
                options=["X", "Y"]
            )
        ]

        current_question = questions[0]
        responses = {"q1": {"single_answer": "A"}}

        result = get_next_question_id(current_question, questions, responses)

        # Should fallback to next sequential question
        assert result["action"] == "continue"
        assert result["next_question_id"] == "q2"
