#!/usr/bin/env python3
"""
Sample script to create a demo survey with media (photos/videos) in questions
Demonstrates how to add GCP bucket URLs to questions for displaying images or videos
"""

import requests
import json

# API_BASE_URL = "http://localhost:8000"
API_BASE_URL = "https://tmg-market-research-backend-953615400721.us-central1.run.app"

def create_survey_with_media():
    """Create a sample survey with media in questions"""

    # Example survey: Product Design Preferences
    sample_survey = {
        "survey_slug": "product-design-test",
        "name": "Product Design Preferences Survey",
        "survey_flow": [
            {
                "id": "design_preference",
                "question": "Which design do you prefer?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Design A (shown above)",
                    "Design B",
                    "No preference"
                ],
                # Example: Add a photo showing the design options
                "media_url": "https://storage.googleapis.com/your-bucket-name/designs/comparison.jpg",
                "media_type": "photo"
            },
            {
                "id": "color_preference",
                "question": "Which color variant appeals to you most?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Blue (as shown)",
                    "Red",
                    "Green",
                    "Black"
                ],
                # Example: Add a photo showing color options
                "media_url": "https://storage.googleapis.com/your-bucket-name/colors/variants.jpg",
                "media_type": "photo"
            },
            {
                "id": "video_tutorial",
                "question": "After watching the video above, how easy do you think this product is to use?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very easy",
                    "Somewhat easy",
                    "Neutral",
                    "Somewhat difficult",
                    "Very difficult"
                ],
                # Example: Add a video tutorial
                "media_url": "https://storage.googleapis.com/your-bucket-name/videos/tutorial.mp4",
                "media_type": "video"
            },
            {
                "id": "additional_feedback",
                "question": "Do you have any additional feedback about the designs shown?",
                "question_type": "free_text",
                "required": False
            }
        ],
        "is_active": True,
        "client": "Design Team"
    }

    # Note: You'll need to provide X-API-Key header for authentication
    headers = {
        "Content-Type": "application/json",
        # Uncomment and add your API key if required:
        # "X-API-Key": "your-api-key-here"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/surveys/",
            json=sample_survey,
            headers=headers
        )

        if response.status_code == 200:
            survey = response.json()
            print(f"✅ Survey created successfully!")
            print(f"Survey ID: {survey['id']}")
            print(f"Survey Slug: {survey['survey_slug']}")
            print(f"Survey URL: {API_BASE_URL}/survey/{survey['survey_slug']}")
            print(f"\nQuestions with media:")
            for q in survey['survey_flow']:
                if q.get('media_url'):
                    print(f"  - {q['question'][:50]}... ({q['media_type']})")
        else:
            print(f"❌ Failed to create survey: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def print_usage_instructions():
    """Print instructions for using media in questions"""
    print("\n" + "="*80)
    print("HOW TO USE MEDIA IN SURVEY QUESTIONS")
    print("="*80)
    print("""
1. Upload your media files to Google Cloud Storage:
   - Photos: JPEG, PNG (recommended max size: 5MB)
   - Videos: MP4, WebM (recommended max size: 50MB)

2. Make the files publicly accessible or use signed URLs

3. Get the GCS URL (format: https://storage.googleapis.com/bucket-name/path/file.ext)

4. Add media to your question:
   {
       "id": "question_id",
       "question": "Your question text",
       "question_type": "single",  // or any question type
       "required": true,
       "options": ["Option 1", "Option 2"],
       "media_url": "https://storage.googleapis.com/your-bucket/image.jpg",
       "media_type": "photo"  // or "video"
   }

5. Supported media types:
   - "photo": Displays an image above the question
   - "video": Displays a video player above the question

EXAMPLE USAGE:
   - Product comparisons: Show different product designs
   - Brand awareness: Display logos or packaging
   - Video instructions: Show tutorials or demos
   - Concept testing: Present mockups or prototypes

Note: The media is displayed ABOVE the question text and options.
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    print("Creating sample survey with media examples...\n")
    create_survey_with_media()
    print_usage_instructions()
