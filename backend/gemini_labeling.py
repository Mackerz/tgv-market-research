import os
import json
from typing import List, Optional, Dict
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GeminiLabelGenerator:
    def __init__(self):
        self.enabled = os.getenv("GEMINI_ENABLED", "true").lower() == "true"

        if not self.enabled:
            logger.info("⚠️  Gemini labeling is disabled. Labels will be simulated.")
            return

        try:
            # Configure Gemini with GCP credentials (same as your other GCP services)
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                # Use the same service account credentials as GCP Vision/Video
                import google.auth
                from google.oauth2 import service_account

                credentials = service_account.Credentials.from_service_account_file(credentials_path)
                genai.configure(credentials=credentials)
            else:
                # Use default GCP credentials (Application Default Credentials)
                genai.configure()

            self.model = genai.GenerativeModel('gemini-1.5-flash')

            logger.info("✅ Gemini AI services initialized successfully with GCP credentials")

        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            logger.info("🔧 Falling back to development mode (labeling simulated)")
            self.enabled = False
            self.model = None

    def generate_reporting_labels(self, description: str, transcript: str = None, brands: List[str] = None) -> Optional[List[str]]:
        """
        Generate market research reporting labels from media descriptions

        Args:
            description: Vision/video analysis description
            transcript: Audio transcript (optional)
            brands: Detected brands (optional)

        Returns:
            List of reporting labels suitable for market research analysis
        """
        if not self.enabled or not self.model:
            # Simulate labeling in development
            logger.info("🏷️ [SIMULATION] Generating reporting labels")
            return [
                "product_interaction",
                "positive_sentiment",
                "home_environment",
                "consumer_behavior",
                "brand_awareness"
            ]

        logger.info("🤖 Generating reporting labels with Gemini")

        try:
            # Build comprehensive content for analysis
            content_parts = [f"Visual analysis: {description}"]

            if transcript:
                content_parts.append(f"Audio transcript: {transcript}")

            if brands:
                content_parts.append(f"Brands detected: {', '.join(brands)}")

            content = "\n".join(content_parts)

            # Create detailed prompt for market research labeling
            prompt = f"""
You are a market research analyst. Based on the following media analysis from a consumer survey response, generate relevant reporting labels that would be valuable for market research insights.

Media Analysis:
{content}

Generate 5-8 specific reporting labels that capture:
1. Consumer behaviors and attitudes
2. Product interactions and usage patterns
3. Emotional responses and sentiment
4. Environmental context (home, store, outdoor, etc.)
5. Demographics or lifestyle indicators
6. Brand engagement and awareness
7. Pain points or satisfaction indicators
8. Purchase intent or decision factors

Return ONLY a JSON array of strings, like: ["label1", "label2", "label3"]

Labels should be:
- Specific and actionable for market research
- Use underscore naming (e.g., "positive_brand_sentiment")
- Focus on insights that would help understand consumer behavior
- Be relevant to the actual content described

JSON array of labels:"""

            # Generate content
            response = self.model.generate_content(prompt)

            # Parse the response
            response_text = response.text.strip()

            # Extract JSON array from response
            try:
                # Try to parse as JSON directly
                labels = json.loads(response_text)

                if isinstance(labels, list) and all(isinstance(label, str) for label in labels):
                    logger.info(f"✅ Generated {len(labels)} reporting labels")
                    logger.info(f"🏷️ Labels: {labels}")
                    return labels
                else:
                    raise ValueError("Response is not a list of strings")

            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    labels = json.loads(json_match.group())
                    if isinstance(labels, list) and all(isinstance(label, str) for label in labels):
                        logger.info(f"✅ Generated {len(labels)} reporting labels")
                        logger.info(f"🏷️ Labels: {labels}")
                        return labels

                logger.error(f"❌ Failed to parse Gemini response as JSON: {response_text}")
                return None

        except Exception as e:
            logger.error(f"❌ Gemini label generation failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return None

    def get_label_summary(self, all_labels: List[List[str]]) -> Dict[str, int]:
        """
        Generate a summary of label frequency across multiple responses

        Args:
            all_labels: List of label lists from multiple responses

        Returns:
            Dictionary mapping labels to their frequency counts
        """
        label_counts = {}

        for labels in all_labels:
            if labels:
                for label in labels:
                    label_counts[label] = label_counts.get(label, 0) + 1

        # Sort by frequency
        sorted_labels = dict(sorted(label_counts.items(), key=lambda x: x[1], reverse=True))

        logger.info(f"📊 Label summary: {len(sorted_labels)} unique labels across {len(all_labels)} responses")

        return sorted_labels

# Global instance
gemini_labeler = GeminiLabelGenerator()

def generate_labels_for_media(description: str, transcript: str = None, brands: List[str] = None) -> Optional[List[str]]:
    """Convenience function for generating labels"""
    return gemini_labeler.generate_reporting_labels(description, transcript, brands)

def get_survey_label_summary(survey_id: int, db) -> Dict[str, int]:
    """Get label frequency summary for an entire survey"""
    from survey_crud import get_submissions_by_survey

    # Get all submissions for the survey
    submissions = get_submissions_by_survey(db, survey_id)

    all_labels = []

    for submission in submissions:
        for response in submission.responses:
            if response.media_analysis:
                for media in response.media_analysis:
                    if media.reporting_labels:
                        try:
                            labels = json.loads(media.reporting_labels)
                            all_labels.append(labels)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse labels for media {media.id}")

    return gemini_labeler.get_label_summary(all_labels)