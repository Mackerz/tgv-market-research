#!/usr/bin/env python3
"""
Sample script demonstrating multiple photos/videos in survey questions
Shows how to use the new 'media' array field
"""

import requests
import json

# API_BASE_URL = "http://localhost:8000"
API_BASE_URL = "https://tmg-market-research-backend-953615400721.us-central1.run.app"

def create_survey_with_multiple_media():
    """Create a survey with multiple media items per question"""

    sample_survey = {
        "survey_slug": "product-comparison-multi",
        "name": "Product Design Comparison (Multiple Images)",
        "survey_flow": [
            {
                "id": "design_preference",
                "question": "Review the three design options shown above. Which is your favorite?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Design A (first image)",
                    "Design B (second image)",
                    "Design C (third image)",
                    "No preference"
                ],
                # NEW: Multiple photos in one question
                "media": [
                    {
                        "url": "https://storage.googleapis.com/your-bucket/designs/design-a.jpg",
                        "type": "photo",
                        "caption": "Design A - Classic style"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/designs/design-b.jpg",
                        "type": "photo",
                        "caption": "Design B - Modern minimalist"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/designs/design-c.jpg",
                        "type": "photo",
                        "caption": "Design C - Bold and vibrant"
                    }
                ]
            },
            {
                "id": "color_preference",
                "question": "Which color variant do you prefer?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Red",
                    "Blue",
                    "Green",
                    "Black"
                ],
                # Multiple color photos
                "media": [
                    {
                        "url": "https://storage.googleapis.com/your-bucket/colors/red.jpg",
                        "type": "photo",
                        "caption": "Red variant"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/colors/blue.jpg",
                        "type": "photo",
                        "caption": "Blue variant"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/colors/green.jpg",
                        "type": "photo",
                        "caption": "Green variant"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/colors/black.jpg",
                        "type": "photo",
                        "caption": "Black variant"
                    }
                ]
            },
            {
                "id": "tutorial_videos",
                "question": "After watching both tutorial videos, how easy is the product to use?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very easy",
                    "Easy",
                    "Neutral",
                    "Difficult",
                    "Very difficult"
                ],
                # Multiple videos
                "media": [
                    {
                        "url": "https://storage.googleapis.com/your-bucket/videos/setup.mp4",
                        "type": "video",
                        "caption": "Part 1: Initial setup"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/videos/usage.mp4",
                        "type": "video",
                        "caption": "Part 2: Daily usage"
                    }
                ]
            },
            {
                "id": "mixed_media",
                "question": "Review the product overview (photo and demo video). How interested are you?",
                "question_type": "single",
                "required": True,
                "options": [
                    "Very interested",
                    "Somewhat interested",
                    "Neutral",
                    "Not very interested",
                    "Not interested at all"
                ],
                # Mixed: photo + video
                "media": [
                    {
                        "url": "https://storage.googleapis.com/your-bucket/product/hero-shot.jpg",
                        "type": "photo",
                        "caption": "Product overview"
                    },
                    {
                        "url": "https://storage.googleapis.com/your-bucket/product/demo.mp4",
                        "type": "video",
                        "caption": "Quick demo"
                    }
                ]
            },
            {
                "id": "feedback",
                "question": "Any additional feedback about the designs or videos you reviewed?",
                "question_type": "free_text",
                "required": False
            }
        ],
        "is_active": True,
        "client": "Product Team"
    }

    headers = {
        "Content-Type": "application/json",
        # Add your API key if required:
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
            print(f"\nQuestions with multiple media:")
            for q in survey['survey_flow']:
                if q.get('media'):
                    media_count = len(q['media'])
                    types = [m['type'] for m in q['media']]
                    print(f"  - {q['question'][:60]}...")
                    print(f"    Media: {media_count} items ({', '.join(types)})")
        else:
            print(f"❌ Failed to create survey: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def print_usage_guide():
    """Print usage guide for multiple media"""
    print("\n" + "="*80)
    print("MULTIPLE MEDIA IN QUESTIONS - USAGE GUIDE")
    print("="*80)
    print("""
NEW FORMAT (Array of Media):

{
    "id": "question_id",
    "question": "Your question text",
    "question_type": "single",
    "required": true,
    "options": ["Option 1", "Option 2"],
    "media": [
        {
            "url": "https://storage.googleapis.com/bucket/image1.jpg",
            "type": "photo",
            "caption": "Optional caption for context"
        },
        {
            "url": "https://storage.googleapis.com/bucket/image2.jpg",
            "type": "photo",
            "caption": "Another caption"
        }
    ]
}

KEY FEATURES:

1. MULTIPLE ITEMS: Add as many photos/videos as needed
   - Product comparisons: Show 2-4 options side-by-side
   - Step-by-step: Multiple tutorial videos
   - Color variants: Show all color options

2. CAPTIONS: Each media item can have an optional caption
   - Helps users distinguish between options
   - Provides context for each image/video

3. MIXED MEDIA: Combine photos and videos in one question
   - Show product photo + demo video
   - Before/after photos + explanation video

4. CAROUSEL NAVIGATION:
   - Single media: Displays normally
   - 2-4 media: Shows carousel with thumbnail preview
   - 5+ media: Shows carousel with navigation arrows

5. BACKWARD COMPATIBLE: Old format still works
   Old: "media_url" and "media_type" fields
   New: "media" array (recommended)

EXAMPLE USE CASES:

1. Design A/B/C Testing:
   Show 3 design options, ask which they prefer

2. Color Selection:
   Display 4-6 color variants for feedback

3. Multi-part Tutorial:
   2-3 short videos showing different aspects

4. Before/After:
   Show "before" and "after" photos

5. Product Line Comparison:
   Show multiple products for preference ranking

DISPLAY BEHAVIOR:

- 1 media item: Full display
- 2-4 items: Carousel + thumbnail grid
- 5+ items: Carousel + dot indicators + counter

Each media item loads independently with:
- Loading spinner
- Error fallback
- Responsive sizing
- Optional caption display
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    print("Creating survey with multiple media items per question...\n")
    create_survey_with_multiple_media()
    print_usage_guide()
