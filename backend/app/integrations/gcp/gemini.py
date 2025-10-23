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
            # Try to configure Gemini with API key first, then fall back to GCP credentials
            # Check environment variable first (set by Cloud Run from secrets)
            api_key = os.getenv("GEMINI_API_KEY")

            # If not in env, try secrets manager
            if not api_key:
                try:
                    from app.integrations.gcp.secrets import get_gemini_api_key
                    api_key = get_gemini_api_key()
                except Exception as e:
                    logger.warning(f"⚠️ Could not retrieve from secrets manager: {e}")

            if api_key:
                genai.configure(api_key=api_key)
                logger.info("✅ Gemini configured with API key")
            else:
                # Configure Gemini with GCP credentials (same as your other GCP services)
                credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if credentials_path and os.path.exists(credentials_path):
                    # Use the same service account credentials as GCP Vision/Video
                    import google.auth
                    from google.oauth2 import service_account

                    credentials = service_account.Credentials.from_service_account_file(credentials_path)
                    genai.configure(credentials=credentials)
                    logger.info("✅ Gemini configured with service account credentials")
                else:
                    # Use default GCP credentials (Application Default Credentials)
                    genai.configure()
                    logger.info("✅ Gemini configured with default GCP credentials")

            # Use the full model name with models/ prefix
            self.model = genai.GenerativeModel('models/gemini-flash-latest')

            logger.info("✅ Gemini AI services initialized successfully")

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

    def summarize_labels(self, all_labels: List[str]) -> Dict[str, any]:
        """
        Use Gemini to consolidate and summarize similar labels into broader market research themes

        Args:
            all_labels: Flat list of all labels from survey responses

        Returns:
            Dictionary containing consolidated themes and key insights
        """
        if not self.enabled or not self.model:
            # Simulate label summarization in development
            logger.info("🏷️ [SIMULATION] Summarizing labels into themes")
            return {
                "themes": [
                    {
                        "theme": "Product Engagement",
                        "frequency": 12,
                        "consolidated_labels": ["product_interaction", "product_usage", "brand_engagement"],
                        "description": "Strong consumer interaction with products and brands"
                    },
                    {
                        "theme": "Consumer Sentiment",
                        "frequency": 8,
                        "consolidated_labels": ["positive_sentiment", "satisfaction", "emotional_response"],
                        "description": "Overall positive emotional responses from consumers"
                    },
                    {
                        "theme": "Environmental Context",
                        "frequency": 6,
                        "consolidated_labels": ["home_environment", "indoor_usage", "lifestyle_context"],
                        "description": "Home-based product usage and lifestyle integration"
                    }
                ],
                "insights": [
                    "Consumers show strong positive engagement with products in home environments",
                    "Brand awareness and interaction levels are consistently high across responses",
                    "Product usage primarily occurs in comfortable, personal spaces"
                ]
            }

        logger.info("🤖 Generating label summary with Gemini")

        try:
            # Count label frequencies
            label_counts = {}
            for label in all_labels:
                label_counts[label] = label_counts.get(label, 0) + 1

            # Sort labels by frequency for the prompt
            sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

            # Format labels for the prompt
            labels_text = "\n".join([f"- {label}: {count} occurrences" for label, count in sorted_labels])

            # Create prompt for label consolidation
            prompt = f"""
You are a market research analyst tasked with consolidating and summarizing survey response labels into actionable market research themes.

Here are all the labels generated from media analysis across survey responses, with their frequency counts:

{labels_text}

Your task:
1. Group similar/related labels into 3-6 high-level market research themes
2. For each theme, provide a clear business-relevant name and description
3. Calculate the total frequency for each theme (sum of constituent labels)
4. Generate 3-5 key insights based on the consolidated themes

Return your analysis in JSON format:
{{
    "themes": [
        {{
            "theme": "Theme Name",
            "frequency": 15,
            "consolidated_labels": ["label1", "label2", "label3"],
            "description": "Clear description of what this theme represents for market research"
        }}
    ],
    "insights": [
        "Actionable insight based on the consolidated themes",
        "Another key finding for market researchers"
    ]
}}

Focus on:
- Grouping semantically similar labels (e.g., "positive_sentiment", "satisfaction", "happy_experience")
- Creating themes that are meaningful for business decision-making
- Providing insights that would help guide marketing, product, or strategy decisions
- Being concise but comprehensive

JSON response:"""

            # Generate content
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Parse the response
            try:
                # Try to parse as JSON directly
                summary = json.loads(response_text)

                if isinstance(summary, dict) and "themes" in summary and "insights" in summary:
                    logger.info(f"✅ Generated label summary with {len(summary.get('themes', []))} themes")
                    logger.info(f"🔍 Key themes: {[theme.get('theme', 'Unknown') for theme in summary.get('themes', [])]}")
                    return summary
                else:
                    raise ValueError("Response does not contain expected structure")

            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    summary = json.loads(json_match.group())
                    if isinstance(summary, dict) and "themes" in summary:
                        logger.info(f"✅ Generated label summary with {len(summary.get('themes', []))} themes")
                        return summary

                logger.error(f"❌ Failed to parse Gemini summary response as JSON: {response_text}")
                return {"themes": [], "insights": []}

        except Exception as e:
            logger.error(f"❌ Gemini label summarization failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return {"themes": [], "insights": []}

    def generate_taxonomy_categories(self, all_labels: List[str], max_categories: int = 6) -> Dict[str, any]:
        """
        Generate high-level taxonomy categories from system labels using Gemini AI

        Args:
            all_labels: Flat list of all system-generated labels
            max_categories: Maximum number of high-level categories to create (3-10)

        Returns:
            Dictionary with taxonomy structure mapping high-level labels to system labels
        """
        if not self.enabled or not self.model:
            # Simulate taxonomy generation in development
            logger.info("🏷️ [SIMULATION] Generating taxonomy categories")
            return {
                "categories": [
                    {
                        "category_name": "Product Experience",
                        "description": "How consumers interact with and experience products",
                        "system_labels": ["product_interaction", "product_usage", "unboxing", "hands_on_experience"]
                    },
                    {
                        "category_name": "Emotional Response",
                        "description": "Consumer sentiment and feelings about products/brands",
                        "system_labels": ["positive_sentiment", "satisfaction", "excitement", "happiness"]
                    },
                    {
                        "category_name": "Environment & Context",
                        "description": "Physical and social context of product usage",
                        "system_labels": ["home_environment", "indoor_usage", "lifestyle_context", "social_setting"]
                    },
                    {
                        "category_name": "Brand Engagement",
                        "description": "Consumer awareness and interaction with brands",
                        "system_labels": ["brand_awareness", "brand_loyalty", "brand_comparison"]
                    }
                ]
            }

        logger.info(f"🤖 Generating taxonomy with Gemini (max {max_categories} categories)")

        try:
            # Count label frequencies
            label_counts = {}
            for label in all_labels:
                label_counts[label] = label_counts.get(label, 0) + 1

            # Sort labels by frequency
            sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

            # Format labels for the prompt
            labels_text = "\n".join([f"- {label}: {count} times" for label, count in sorted_labels])

            # Create prompt for taxonomy generation
            prompt = f"""
You are a market research expert creating a taxonomy system for consumer survey data.

Here are all the system-generated labels from media analysis, with their frequencies:

{labels_text}

Your task:
Create a hierarchical taxonomy by grouping these system labels into {max_categories} or fewer high-level reporting categories.

Requirements:
1. Create {max_categories} or fewer high-level category names that are:
   - Clear and business-focused
   - Meaningful for market research reporting
   - Broad enough to group multiple related concepts
   - Mutually exclusive where possible

2. For each category:
   - Provide a descriptive category name (2-4 words)
   - Write a brief description of what it represents
   - Assign relevant system labels to this category
   - Ensure every system label is assigned to exactly one category

3. Consider:
   - Semantic similarity (group similar concepts)
   - Business value (categories should be useful for reporting)
   - Balance (try to distribute labels reasonably across categories)

Return your taxonomy in JSON format:
{{
    "categories": [
        {{
            "category_name": "Clear Category Name",
            "description": "Brief description of what this category represents for reporting",
            "system_labels": ["label1", "label2", "label3"]
        }}
    ]
}}

JSON response:"""

            # Generate content
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Try to parse JSON from response
            try:
                # Try direct JSON parsing first
                taxonomy = json.loads(response_text)
                if isinstance(taxonomy, dict) and "categories" in taxonomy:
                    logger.info(f"✅ Generated taxonomy with {len(taxonomy.get('categories', []))} categories")
                    return taxonomy
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    taxonomy = json.loads(json_match.group(1))
                    if isinstance(taxonomy, dict) and "categories" in taxonomy:
                        logger.info(f"✅ Generated taxonomy with {len(taxonomy.get('categories', []))} categories")
                        return taxonomy

            logger.error(f"❌ Failed to parse Gemini taxonomy response as JSON: {response_text}")
            return {"categories": []}

        except Exception as e:
            logger.error(f"❌ Gemini taxonomy generation failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return {"categories": []}

# Global instance
gemini_labeler = GeminiLabelGenerator()

def generate_labels_for_media(description: str, transcript: str = None, brands: List[str] = None) -> Optional[List[str]]:
    """Convenience function for generating labels"""
    return gemini_labeler.generate_reporting_labels(description, transcript, brands)

def get_survey_label_summary(survey_id: int, db) -> Dict[str, int]:
    """Get label frequency summary for an entire survey"""
    from app.crud.survey import get_submissions_by_survey

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

def summarize_survey_labels(survey_id: int, db) -> Dict[str, any]:
    """
    Get a comprehensive label analysis including both raw counts and AI-generated summaries

    Returns:
        Dictionary containing raw label counts, summarized themes, and key insights
    """
    from app.crud.survey import get_submissions_by_survey

    # Get all submissions for the survey
    submissions = get_submissions_by_survey(db, survey_id)

    all_labels = []
    all_label_strings = []

    for submission in submissions:
        for response in submission.responses:
            if response.media_analysis:
                for media in response.media_analysis:
                    if media.reporting_labels:
                        try:
                            labels = json.loads(media.reporting_labels)
                            all_labels.extend(labels)  # Flatten all labels
                            all_label_strings.append(', '.join(labels))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse labels for media {media.id}")

    if not all_labels:
        return {
            "raw_label_counts": {},
            "summarized_themes": [],
            "key_insights": [],
            "total_responses": 0,
            "unique_labels": 0
        }

    # Get raw frequency counts
    raw_counts = gemini_labeler.get_label_summary([all_labels])

    # Generate AI summary of the labels
    summarized_themes = gemini_labeler.summarize_labels(all_labels)

    return {
        "raw_label_counts": raw_counts,
        "summarized_themes": summarized_themes.get("themes", []),
        "key_insights": summarized_themes.get("insights", []),
        "total_responses": len([l for labels in [all_labels] for l in labels]),
        "unique_labels": len(raw_counts)
    }