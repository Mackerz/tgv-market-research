#!/usr/bin/env python3
"""
Sample script to create a demo survey for local Docker development
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def create_sample_survey():
    """Create a sample survey with all question types"""

    sample_survey = {
        "survey_slug": "monster-lifestyle",
        "name": "Be the best",
        "survey_flow": [
            {
                "id": "satisfaction",
                "question": "How many times do you drink Monster Energy?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Daily",
                    "A few times a week",
                    "Weekly",
                    "Monthly",
                    "Occasionally"
                ]
            },
            {
                "id": "features",
                "question": "What is your favourite flavours of Monster Energy? (Select all that apply)",
                "question_type": "multi",
                "required": True,
                "options": [
                    "Original Green Monster",
                    "Zero Sugar Monster",
                    "Monster Energy Reserve",
                    "Monster Nitro",
                    "Zero Ultra",
                    "Ultra",
                    "Rio Punch",
                    "Ripper",
                    "Pipeline Punch",
                    "Mango Loco",
                    "Ultra Fiesta (Mango)",
                    "Lewis Hamilton Zero",
                    "Bad Apple",
                    "Reserve Orange Dreamsicle",
                ]
            },
            {
                "id": "feedback",
                "question": "Monster is the relentless pursuit of victory, being your best. Explain why you think Monster helps you being at the top of your game.",
                "question_type": "free_text",
                "required": True
            },
            {
                "id": "screenshot",
                "question": "Upload a photo of the can of Monster you are drinking:",
                "question_type": "photo",
                "required": False
            },
            {
                "id": "testimonial",
                "question": "Would you like to record a short testimonial video of how monster is helping you be the best?",
                "question_type": "video",
                "required": False
            }
        ],
        "is_active": True
    }

    try:
        # Check if survey already exists
        response = requests.get(f"{API_BASE_URL}/api/surveys/slug/{sample_survey['survey_slug']}")

        if response.status_code == 200:
            print(f"ℹ️  Survey '{sample_survey['survey_slug']}' already exists, skipping creation")
            survey = response.json()
            print(f"Survey ID: {survey['id']}")
            print(f"Survey Slug: {survey['survey_slug']}")
            return survey

        # Create new survey
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
            return survey
        else:
            print(f"❌ Failed to create survey: {response.status_code}")
            print(f"Error: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Creating sample Monster Energy survey...")
    print("=" * 50)

    # Create sample survey
    survey = create_sample_survey()

    if survey:
        print(f"\n🎉 Sample survey is ready!")
        print(f"\n💡 The survey includes:")
        print("  • Personal information form (email, phone, region, DOB, gender)")
        print("  • Single choice question (frequency of consumption)")
        print("  • Multiple choice question (favorite flavors)")
        print("  • Free text question (detailed feedback)")
        print("  • Photo upload (optional can photo)")
        print("  • Video upload (optional testimonial)")
    else:
        print("\n❌ Failed to create sample survey")
        sys.exit(1)
