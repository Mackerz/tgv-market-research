"""
Example script to create a survey with conditional routing logic.

This demonstrates:
1. Skip logic based on answer values
2. Early survey termination (attention checks)
3. Conditional branching based on multiple conditions

Usage:
    poetry run python create_survey_with_routing_example.py
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")


def create_survey_with_routing():
    """
    Create a survey demonstrating conditional routing.

    Survey Flow:
    1. "How many children do you have?"
       - If 0 → Skip to question 4 (favorite hobby)
       - If 1+ → Continue to question 2 (ages of children)

    2. "What are the ages of your children?"
       - Always continues to question 3

    3. "What activities do your children enjoy?"
       - Always continues to question 4

    4. "What is your favorite hobby?"
       - If "I don't have hobbies" selected → End survey (attention check)
       - Otherwise → Continue to question 5

    5. "How satisfied are you with our service?"
       - Final question
    """

    survey_data = {
        "survey_slug": "family-lifestyle-routing",
        "name": "Family & Lifestyle Survey (with Routing)",
        "client": "Market Research Demo",
        "is_active": True,
        "survey_flow": [
            # Question 1: Number of children (routing based on answer)
            {
                "id": "num_children",
                "question": "How many children do you have?",
                "question_type": "single",
                "required": True,
                "options": ["0", "1", "2", "3", "4", "5 or more"],
                "routing_rules": [
                    {
                        "conditions": [
                            {
                                "question_id": "num_children",
                                "operator": "equals",
                                "value": "0"
                            }
                        ],
                        "action": "goto_question",
                        "target_question_id": "favorite_hobby"
                    }
                    # If not 0, continue to next question (default behavior)
                ]
            },

            # Question 2: Ages of children (only shown if children > 0)
            {
                "id": "children_ages",
                "question": "What are the ages of your children? (You can select multiple)",
                "question_type": "multi",
                "required": True,
                "options": [
                    "0-2 years",
                    "3-5 years",
                    "6-12 years",
                    "13-17 years",
                    "18+ years"
                ]
            },

            # Question 3: Children's activities
            {
                "id": "children_activities",
                "question": "What activities do your children enjoy?",
                "question_type": "free_text",
                "required": True
            },

            # Question 4: Favorite hobby (with attention check)
            {
                "id": "favorite_hobby",
                "question": "What is your favorite hobby?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Reading",
                    "Sports",
                    "Cooking",
                    "Traveling",
                    "Gaming",
                    "Gardening",
                    "I don't have hobbies"  # Attention check - ends survey
                ],
                "routing_rules": [
                    {
                        "conditions": [
                            {
                                "question_id": "favorite_hobby",
                                "operator": "equals",
                                "value": "I don't have hobbies"
                            }
                        ],
                        "action": "end_survey"
                    }
                ]
            },

            # Question 5: Satisfaction (final question)
            {
                "id": "satisfaction",
                "question": "How satisfied are you with our service?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very satisfied",
                    "Satisfied",
                    "Neutral",
                    "Dissatisfied",
                    "Very dissatisfied"
                ]
            }
        ]
    }

    # Create survey
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/surveys/",
        json=survey_data,
        headers=headers
    )

    if response.status_code == 200:
        print("✅ Survey created successfully!")
        print(f"Survey Slug: {survey_data['survey_slug']}")
        print(f"Survey Name: {survey_data['name']}")
        print(f"\n📋 Routing Logic:")
        print("  • Question 1: If '0 children' → Skip to Question 4")
        print("  • Question 4: If 'I don't have hobbies' → End survey")
        print(f"\n🌐 Access survey at: {API_BASE_URL}/survey/{survey_data['survey_slug']}")
    else:
        print(f"❌ Error creating survey: {response.status_code}")
        print(response.text)


def create_advanced_routing_survey():
    """
    Create a more advanced survey with complex routing logic.

    Demonstrates:
    - Multiple condition routing (AND logic)
    - Contains/contains_any operators for multi-choice
    - Numeric comparison operators
    """

    survey_data = {
        "survey_slug": "product-feedback-advanced",
        "name": "Product Feedback Survey (Advanced Routing)",
        "client": "Product Team",
        "is_active": True,
        "survey_flow": [
            # Question 1: Product usage
            {
                "id": "product_usage",
                "question": "Which of our products do you use? (Select all that apply)",
                "question_type": "multi",
                "required": True,
                "options": [
                    "Product A",
                    "Product B",
                    "Product C",
                    "I don't use any products"
                ],
                "routing_rules": [
                    {
                        "conditions": [
                            {
                                "question_id": "product_usage",
                                "operator": "contains",
                                "value": "I don't use any products"
                            }
                        ],
                        "action": "end_survey"
                    }
                ]
            },

            # Question 2: Product A specific (only if Product A selected)
            {
                "id": "product_a_rating",
                "question": "How would you rate Product A?",
                "question_type": "single",
                "required": True,
                "options": ["1", "2", "3", "4", "5"],
                "routing_rules": [
                    # Skip if they don't use Product A
                    {
                        "conditions": [
                            {
                                "question_id": "product_usage",
                                "operator": "not_contains",
                                "value": "Product A"
                            }
                        ],
                        "action": "goto_question",
                        "target_question_id": "overall_satisfaction"
                    }
                ]
            },

            # Question 3: Follow-up for low ratings
            {
                "id": "improvement_suggestions",
                "question": "What can we improve about Product A?",
                "question_type": "free_text",
                "required": True,
                "routing_rules": [
                    # Only show if rating is 1, 2, or 3
                    {
                        "conditions": [
                            {
                                "question_id": "product_a_rating",
                                "operator": "greater_than",
                                "value": 3
                            }
                        ],
                        "action": "goto_question",
                        "target_question_id": "overall_satisfaction"
                    }
                ]
            },

            # Question 4: Overall satisfaction
            {
                "id": "overall_satisfaction",
                "question": "Overall, how satisfied are you with our products?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very satisfied",
                    "Satisfied",
                    "Neutral",
                    "Dissatisfied",
                    "Very dissatisfied"
                ]
            }
        ]
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{API_BASE_URL}/api/surveys/",
        json=survey_data,
        headers=headers
    )

    if response.status_code == 200:
        print("\n✅ Advanced survey created successfully!")
        print(f"Survey Slug: {survey_data['survey_slug']}")
        print(f"Survey Name: {survey_data['name']}")
        print(f"\n📋 Routing Logic:")
        print("  • Question 1: If 'don't use any products' → End survey")
        print("  • Question 2: If Product A not selected → Skip to Question 4")
        print("  • Question 3: If rating > 3 → Skip to Question 4")
        print(f"\n🌐 Access survey at: {API_BASE_URL}/survey/{survey_data['survey_slug']}")
    else:
        print(f"❌ Error creating survey: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("Creating surveys with conditional routing...\n")
    create_survey_with_routing()
    print("\n" + "="*80 + "\n")
    create_advanced_routing_survey()
