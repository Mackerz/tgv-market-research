#!/usr/bin/env python3
"""
Sample script to create a demo survey using the survey system API
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def create_sample_survey():
    """Create a sample survey with all question types"""

    sample_survey = {
        "survey_slug": "sample-survey-2024",
        "name": "Customer Feedback Survey",
        "survey_flow": [
            {
                "id": "satisfaction",
                "question": "How satisfied are you with our service?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very Satisfied",
                    "Satisfied",
                    "Neutral",
                    "Dissatisfied",
                    "Very Dissatisfied"
                ]
            },
            {
                "id": "features",
                "question": "Which features do you use most often? (Select all that apply)",
                "question_type": "multi",
                "required": True,
                "options": [
                    "Dashboard",
                    "Reports",
                    "User Management",
                    "Settings",
                    "Mobile App",
                    "API Integration"
                ]
            },
            {
                "id": "feedback",
                "question": "Please provide detailed feedback about your experience:",
                "question_type": "free_text",
                "required": True
            },
            {
                "id": "screenshot",
                "question": "If you encountered any issues, please upload a screenshot:",
                "question_type": "photo",
                "required": False
            },
            {
                "id": "testimonial",
                "question": "Would you like to record a short testimonial video?",
                "question_type": "video",
                "required": False
            }
        ],
        "is_active": True
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/surveys/",
            json=sample_survey,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            survey = response.json()
            print(f"✅ Survey created successfully!")
            print(f"Survey ID: {survey['id']}")
            print(f"Survey Slug: {survey['survey_slug']}")
            print(f"Survey URL: http://localhost:3000/survey/{survey['survey_slug']}")
            return survey
        else:
            print(f"❌ Failed to create survey: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def get_all_surveys():
    """Get all surveys"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/surveys/")

        if response.status_code == 200:
            surveys = response.json()
            print(f"\n📋 Found {len(surveys)} surveys:")
            for survey in surveys:
                print(f"  • {survey['name']} (slug: {survey['survey_slug']})")
                print(f"    Status: {'Active' if survey['is_active'] else 'Inactive'}")
                print(f"    Questions: {len(survey['survey_flow'])}")
                print(f"    URL: http://localhost:3000/survey/{survey['survey_slug']}")
                print()
            return surveys
        else:
            print(f"❌ Failed to get surveys: {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Survey System Demo Script")
    print("=" * 50)

    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print("❌ API health check failed")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Make sure the backend is running on http://localhost:8000")
        exit(1)

    # Get existing surveys
    get_all_surveys()

    # Create sample survey
    print("\n🔨 Creating sample survey...")
    survey = create_sample_survey()

    if survey:
        print(f"\n🎉 Sample survey is ready!")
        print(f"Visit: http://localhost:3000/survey/{survey['survey_slug']}")
        print(f"\n💡 The survey includes:")
        print("  • Personal information form (email, phone, region, DOB, gender)")
        print("  • Single choice question (satisfaction rating)")
        print("  • Multiple choice question (features used)")
        print("  • Free text question (detailed feedback)")
        print("  • Photo upload (optional screenshot)")
        print("  • Video upload (optional testimonial)")
