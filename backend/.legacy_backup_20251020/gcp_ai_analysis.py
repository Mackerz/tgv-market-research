import os
import json
from typing import Optional, List, Tuple
from google.cloud import videointelligence
from google.cloud import vision
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GCPAIAnalyzer:
    def __init__(self):
        self.enabled = os.getenv("GCP_AI_ENABLED", "false").lower() == "true"

        if not self.enabled:
            logger.info("⚠️  GCP AI Analysis is disabled. Photo/video analysis will be simulated.")
            self.vision_client = None
            self.video_client = None
            return

        try:
            # Initialize clients
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path:
                self.vision_client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
                self.video_client = videointelligence.VideoIntelligenceServiceClient.from_service_account_json(credentials_path)
            else:
                # Use default credentials
                self.vision_client = vision.ImageAnnotatorClient()
                self.video_client = videointelligence.VideoIntelligenceServiceClient()

            logger.info("✅ GCP AI services initialized successfully")

        except Exception as e:
            logger.error(f"❌ GCP AI initialization failed: {e}")
            logger.info("🔧 Falling back to development mode (AI analysis simulated)")
            self.enabled = False
            self.vision_client = None
            self.video_client = None

    def analyze_image(self, gcs_uri: str) -> Optional[str]:
        """
        Analyze an image using GCP Vision API and return a description

        Args:
            gcs_uri: Google Cloud Storage URI (e.g., 'gs://bucket/path/image.jpg')

        Returns:
            Description string or None if analysis fails
        """
        if not self.enabled or not self.vision_client:
            # Simulate analysis in development
            logger.info(f"📷 [SIMULATION] Image analysis for: {gcs_uri}")
            return "Simulated image description: A photo showing various elements captured during the survey response."

        logger.info(f"🔍 Starting real Vision API analysis for: {gcs_uri}")

        try:
            # Create image object
            image = vision.Image()
            image.source.image_uri = gcs_uri

            # Perform multiple types of analysis
            features = [
                vision.Feature(type_=vision.Feature.Type.LABEL_DETECTION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.OBJECT_LOCALIZATION, max_results=10),
                vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION),
                vision.Feature(type_=vision.Feature.Type.LOGO_DETECTION),
            ]

            # Call the API
            request = vision.AnnotateImageRequest(image=image, features=features)
            response = self.vision_client.annotate_image(request=request)

            # Process results into a description
            description_parts = []

            # Labels (general content)
            if response.label_annotations:
                labels = [label.description for label in response.label_annotations[:5]]
                description_parts.append(f"Image contains: {', '.join(labels)}")

            # Objects
            if response.localized_object_annotations:
                objects = [obj.name for obj in response.localized_object_annotations[:5]]
                description_parts.append(f"Objects detected: {', '.join(objects)}")

            # Text
            if response.text_annotations:
                text_content = response.text_annotations[0].description.replace('\n', ' ').strip()[:200]
                if text_content:
                    description_parts.append(f"Text visible: {text_content}")

            # Logos/Brands
            if response.logo_annotations:
                logos = [logo.description for logo in response.logo_annotations]
                description_parts.append(f"Brands/logos detected: {', '.join(logos)}")

            # Error handling
            if response.error.message:
                logger.error(f"❌ Vision API error for {gcs_uri}: {response.error.message}")
                return None

            # Log analysis results
            logger.info(f"📊 Vision API results for {gcs_uri}:")
            if response.label_annotations:
                labels = [label.description for label in response.label_annotations[:3]]
                logger.info(f"   🏷️ Labels: {labels}")
            if response.localized_object_annotations:
                objects = [obj.name for obj in response.localized_object_annotations[:3]]
                logger.info(f"   📦 Objects: {objects}")
            if response.logo_annotations:
                logos = [logo.description for logo in response.logo_annotations]
                logger.info(f"   🏪 Brands/Logos: {logos}")

            final_description = ". ".join(description_parts) if description_parts else "No specific content detected in image"
            logger.info(f"✅ Image analysis completed for {gcs_uri}")
            logger.info(f"📝 Final description: {final_description[:150]}...")
            return final_description

        except Exception as e:
            logger.error(f"❌ Image analysis failed for {gcs_uri}: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return None

    def analyze_video(self, gcs_uri: str) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
        """
        Analyze a video using GCP Video Intelligence API

        Args:
            gcs_uri: Google Cloud Storage URI (e.g., 'gs://bucket/path/video.mp4')

        Returns:
            Tuple of (description, transcript, brands_list)
        """
        if not self.enabled or not self.video_client:
            # Simulate analysis in development
            logger.info(f"🎥 [SIMULATION] Video analysis for: {gcs_uri}")
            return (
                "Simulated video description: A video response showing various activities and content.",
                "Simulated transcript: User speaking about their experience and feedback.",
                ["Brand A", "Product B"]
            )

        logger.info(f"🔍 Starting real Video Intelligence API analysis for: {gcs_uri}")

        try:
            # Configure analysis features
            features = [
                videointelligence.Feature.LABEL_DETECTION,
                videointelligence.Feature.OBJECT_TRACKING,
                videointelligence.Feature.SPEECH_TRANSCRIPTION,
                videointelligence.Feature.LOGO_RECOGNITION,
            ]

            # Speech transcription config
            speech_config = videointelligence.SpeechTranscriptionConfig(
                language_code="en-US",
                enable_automatic_punctuation=True,
            )

            # Start the analysis operation
            operation = self.video_client.annotate_video(
                request={
                    "input_uri": gcs_uri,
                    "features": features,
                    "video_context": videointelligence.VideoContext(
                        speech_transcription_config=speech_config,
                    ),
                }
            )

            logger.info(f"🔄 Video analysis started for {gcs_uri}. Waiting for completion...")
            result = operation.result(timeout=300)  # 5 minute timeout

            # Debug: Log the raw API response structure
            logger.info(f"🔍 API Response Debug for {gcs_uri}:")
            logger.info(f"   📊 Total annotation results: {len(result.annotation_results)}")

            if result.annotation_results:
                annotation = result.annotation_results[0]
                logger.info(f"   🏷️ Segment labels: {len(annotation.segment_label_annotations)}")
                logger.info(f"   📦 Object annotations: {len(annotation.object_annotations)}")
                logger.info(f"   🗣️ Speech transcriptions: {len(annotation.speech_transcriptions)}")
                logger.info(f"   🏪 Logo annotations: {len(annotation.logo_recognition_annotations)}")

                # Log first few labels if they exist
                if annotation.segment_label_annotations:
                    for i, label in enumerate(annotation.segment_label_annotations[:3]):
                        logger.info(f"      Label {i+1}: {label.entity.description if hasattr(label, 'entity') else 'No entity'}")

            # Process results
            description_parts = []
            transcript_parts = []
            brands_detected = []

            # Process ALL annotation results, not just the first one
            for result_idx, annotation_result in enumerate(result.annotation_results):
                logger.info(f"   🔍 Processing annotation result {result_idx + 1}/{len(result.annotation_results)}")

                # Labels (general content)
                for annotation in annotation_result.segment_label_annotations:
                    if hasattr(annotation, 'entity') and hasattr(annotation.entity, 'description'):
                        description_parts.append(annotation.entity.description)
                        logger.info(f"      Found label: {annotation.entity.description}")

                # Object tracking
                for annotation in annotation_result.object_annotations:
                    if hasattr(annotation, 'entity') and hasattr(annotation.entity, 'description'):
                        description_parts.append(f"Object: {annotation.entity.description}")
                        logger.info(f"      Found object: {annotation.entity.description}")

                # Speech transcription
                for annotation in annotation_result.speech_transcriptions:
                    for alternative in annotation.alternatives:
                        if alternative.transcript.strip():
                            transcript_parts.append(alternative.transcript.strip())
                            logger.info(f"      Found speech: {alternative.transcript.strip()[:50]}...")

                # Logo detection
                for annotation in annotation_result.logo_recognition_annotations:
                    for track in annotation.tracks:
                        # Handle different API response formats
                        if hasattr(track, 'entity') and hasattr(track.entity, 'description'):
                            brands_detected.append(track.entity.description)
                            logger.info(f"      Found brand: {track.entity.description}")
                        elif hasattr(annotation, 'entity') and hasattr(annotation.entity, 'description'):
                            brands_detected.append(annotation.entity.description)
                            logger.info(f"      Found brand: {annotation.entity.description}")

            # Format results
            description = "Video shows: " + ", ".join(set(description_parts[:10])) if description_parts else "No specific content detected in video"
            transcript = " ".join(transcript_parts) if transcript_parts else None
            brands_list = list(set(brands_detected)) if brands_detected else []

            logger.info(f"✅ Video analysis completed for {gcs_uri}")
            return description, transcript, brands_list

        except Exception as e:
            logger.error(f"❌ Video analysis failed for {gcs_uri}: {e}")
            return None, None, None

# Global instance
gcp_ai_analyzer = GCPAIAnalyzer()

def analyze_photo_response(gcs_uri: str) -> Optional[str]:
    """Convenience function for photo analysis"""
    return gcp_ai_analyzer.analyze_image(gcs_uri)

def analyze_video_response(gcs_uri: str) -> Tuple[Optional[str], Optional[str], Optional[List[str]]]:
    """Convenience function for video analysis"""
    return gcp_ai_analyzer.analyze_video(gcs_uri)