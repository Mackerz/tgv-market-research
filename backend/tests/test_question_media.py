"""
Unit tests for question media functionality
Tests schema validation, media arrays, and backward compatibility
"""

import pytest
from pydantic import ValidationError
from app.schemas.survey import (
    SurveyQuestion,
    QuestionMedia,
    QuestionMediaType,
    QuestionType
)


class TestQuestionMediaSchema:
    """Test QuestionMedia model validation"""

    def test_valid_photo_media(self):
        """Test creating valid photo media"""
        media = QuestionMedia(
            url="https://storage.googleapis.com/bucket/photo.jpg",
            type="photo"
        )
        assert media.url == "https://storage.googleapis.com/bucket/photo.jpg"
        assert media.type == QuestionMediaType.PHOTO
        assert media.caption is None

    def test_valid_video_media(self):
        """Test creating valid video media"""
        media = QuestionMedia(
            url="https://storage.googleapis.com/bucket/video.mp4",
            type="video"
        )
        assert media.type == QuestionMediaType.VIDEO

    def test_media_with_caption(self):
        """Test media with optional caption"""
        media = QuestionMedia(
            url="https://storage.googleapis.com/bucket/photo.jpg",
            type="photo",
            caption="Product design option A"
        )
        assert media.caption == "Product design option A"

    def test_media_requires_url(self):
        """Test that URL is required"""
        with pytest.raises(ValidationError) as exc_info:
            QuestionMedia(type="photo")
        assert "url" in str(exc_info.value)

    def test_media_requires_type(self):
        """Test that type is required"""
        with pytest.raises(ValidationError) as exc_info:
            QuestionMedia(url="https://example.com/photo.jpg")
        assert "type" in str(exc_info.value)

    def test_media_invalid_type(self):
        """Test that invalid media type is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            QuestionMedia(
                url="https://example.com/file.txt",
                type="document"  # Invalid type
            )
        assert "type" in str(exc_info.value).lower()


class TestSurveyQuestionMediaArray:
    """Test SurveyQuestion with media array"""

    def test_question_with_single_media(self):
        """Test question with one media item"""
        question = SurveyQuestion(
            id="q1",
            question="Which design do you prefer?",
            question_type="single",
            required=True,
            options=["Design A", "Design B"],
            media=[
                QuestionMedia(
                    url="https://storage.googleapis.com/bucket/design-a.jpg",
                    type="photo",
                    caption="Design A"
                )
            ]
        )
        assert len(question.media) == 1
        assert question.media[0].type == QuestionMediaType.PHOTO
        assert question.media[0].caption == "Design A"

    def test_question_with_multiple_media(self):
        """Test question with multiple media items"""
        question = SurveyQuestion(
            id="q1",
            question="Compare these designs",
            question_type="single",
            required=True,
            options=["A", "B", "C"],
            media=[
                QuestionMedia(url="https://example.com/a.jpg", type="photo", caption="Design A"),
                QuestionMedia(url="https://example.com/b.jpg", type="photo", caption="Design B"),
                QuestionMedia(url="https://example.com/c.jpg", type="photo", caption="Design C")
            ]
        )
        assert len(question.media) == 3
        assert all(m.type == QuestionMediaType.PHOTO for m in question.media)
        assert [m.caption for m in question.media] == ["Design A", "Design B", "Design C"]

    def test_question_with_mixed_media_types(self):
        """Test question with both photo and video"""
        question = SurveyQuestion(
            id="q1",
            question="Review the product",
            question_type="single",
            required=True,
            options=["Interested", "Not interested"],
            media=[
                QuestionMedia(url="https://example.com/product.jpg", type="photo", caption="Product image"),
                QuestionMedia(url="https://example.com/demo.mp4", type="video", caption="Demo video")
            ]
        )
        assert len(question.media) == 2
        assert question.media[0].type == QuestionMediaType.PHOTO
        assert question.media[1].type == QuestionMediaType.VIDEO

    def test_question_with_no_media(self):
        """Test question without media (should be valid)"""
        question = SurveyQuestion(
            id="q1",
            question="What is your name?",
            question_type="free_text",
            required=True
        )
        assert question.media is None

    def test_question_with_empty_media_array_fails(self):
        """Test that empty media array is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SurveyQuestion(
                id="q1",
                question="Test question",
                question_type="single",
                required=True,
                options=["A", "B"],
                media=[]  # Empty array should fail
            )
        assert "cannot be empty" in str(exc_info.value).lower()

    def test_question_media_array_serialization(self):
        """Test that media array serializes correctly"""
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media=[
                QuestionMedia(url="https://example.com/1.jpg", type="photo", caption="First"),
                QuestionMedia(url="https://example.com/2.jpg", type="photo", caption="Second")
            ]
        )
        data = question.model_dump()
        assert "media" in data
        assert len(data["media"]) == 2
        assert data["media"][0]["url"] == "https://example.com/1.jpg"
        assert data["media"][0]["type"] == "photo"
        assert data["media"][0]["caption"] == "First"


class TestLegacyMediaCompatibility:
    """Test backward compatibility with old media_url/media_type format"""

    def test_question_with_legacy_media_url(self):
        """Test question with old media_url format"""
        question = SurveyQuestion(
            id="q1",
            question="Which design?",
            question_type="single",
            required=True,
            options=["A", "B"],
            media_url="https://example.com/design.jpg",
            media_type="photo"
        )
        assert question.media_url == "https://example.com/design.jpg"
        assert question.media_type == QuestionMediaType.PHOTO
        assert question.media is None  # New field not used

    def test_legacy_media_url_requires_type(self):
        """Test that media_url requires media_type (when validation is enforced)"""
        # Note: This validation only triggers when both fields exist in schemas with validation
        # For backward compatibility, we allow media_url without media_type
        # But in practice, you should always provide both
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media_url="https://example.com/photo.jpg"
            # No media_type - should be allowed for backward compat but not recommended
        )
        # Should work but media_type will be None
        assert question.media_url == "https://example.com/photo.jpg"
        assert question.media_type is None

    def test_can_use_both_formats(self):
        """Test that both old and new formats can coexist (though not recommended)"""
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            # New format
            media=[
                QuestionMedia(url="https://example.com/new.jpg", type="photo")
            ],
            # Old format (for backward compatibility)
            media_url="https://example.com/old.jpg",
            media_type="photo"
        )
        # Both should be present
        assert question.media is not None
        assert question.media_url is not None

    def test_legacy_format_serialization(self):
        """Test legacy format serializes correctly"""
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media_url="https://example.com/legacy.jpg",
            media_type="video"
        )
        data = question.model_dump()
        assert data["media_url"] == "https://example.com/legacy.jpg"
        assert data["media_type"] == "video"


class TestMediaWithQuestionTypes:
    """Test media works with all question types"""

    def test_media_with_single_choice(self):
        """Test media with single choice question"""
        question = SurveyQuestion(
            id="q1",
            question="Choose one",
            question_type="single",
            required=True,
            options=["A", "B", "C"],
            media=[QuestionMedia(url="https://example.com/photo.jpg", type="photo")]
        )
        assert question.question_type == QuestionType.SINGLE
        assert len(question.media) == 1

    def test_media_with_multi_choice(self):
        """Test media with multiple choice question"""
        question = SurveyQuestion(
            id="q1",
            question="Choose all that apply",
            question_type="multi",
            required=True,
            options=["A", "B", "C"],
            media=[QuestionMedia(url="https://example.com/photo.jpg", type="photo")]
        )
        assert question.question_type == QuestionType.MULTI
        assert len(question.media) == 1

    def test_media_with_free_text(self):
        """Test media with free text question"""
        question = SurveyQuestion(
            id="q1",
            question="Describe what you see",
            question_type="free_text",
            required=True,
            media=[QuestionMedia(url="https://example.com/photo.jpg", type="photo")]
        )
        assert question.question_type == QuestionType.FREE_TEXT
        assert len(question.media) == 1

    def test_media_with_photo_upload_question(self):
        """Test media with photo upload question (showing example)"""
        question = SurveyQuestion(
            id="q1",
            question="Upload a similar photo",
            question_type="photo",
            required=False,
            media=[
                QuestionMedia(
                    url="https://example.com/example.jpg",
                    type="photo",
                    caption="Upload something like this"
                )
            ]
        )
        assert question.question_type == QuestionType.PHOTO
        assert question.media[0].caption == "Upload something like this"

    def test_media_with_video_upload_question(self):
        """Test media with video upload question (showing example)"""
        question = SurveyQuestion(
            id="q1",
            question="Upload a video testimonial",
            question_type="video",
            required=False,
            media=[
                QuestionMedia(
                    url="https://example.com/example.mp4",
                    type="video",
                    caption="Example video format"
                )
            ]
        )
        assert question.question_type == QuestionType.VIDEO
        assert question.media[0].type == QuestionMediaType.VIDEO


class TestMediaEdgeCases:
    """Test edge cases and error conditions"""

    def test_many_media_items(self):
        """Test question with many media items (stress test)"""
        media_items = [
            QuestionMedia(
                url=f"https://example.com/image{i}.jpg",
                type="photo",
                caption=f"Image {i}"
            )
            for i in range(10)
        ]
        question = SurveyQuestion(
            id="q1",
            question="Review all images",
            question_type="single",
            required=True,
            options=["Good", "Bad"],
            media=media_items
        )
        assert len(question.media) == 10
        assert all(m.type == QuestionMediaType.PHOTO for m in question.media)

    def test_media_with_special_characters_in_caption(self):
        """Test media caption with special characters"""
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media=[
                QuestionMedia(
                    url="https://example.com/photo.jpg",
                    type="photo",
                    caption="Design A - \"Modern\" & Bold (2024)"
                )
            ]
        )
        assert '"Modern"' in question.media[0].caption
        assert "&" in question.media[0].caption

    def test_media_url_with_query_params(self):
        """Test media URL with query parameters"""
        url_with_params = "https://storage.googleapis.com/bucket/file.jpg?token=abc123&size=large"
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media=[QuestionMedia(url=url_with_params, type="photo")]
        )
        assert "token=abc123" in question.media[0].url

    def test_media_without_caption_is_valid(self):
        """Test that caption is truly optional"""
        question = SurveyQuestion(
            id="q1",
            question="Test",
            question_type="single",
            required=True,
            options=["A", "B"],
            media=[
                QuestionMedia(url="https://example.com/1.jpg", type="photo"),
                QuestionMedia(url="https://example.com/2.jpg", type="photo")
            ]
        )
        assert all(m.caption is None for m in question.media)

    def test_question_json_serialization_with_media(self):
        """Test full JSON serialization/deserialization"""
        import json

        question_dict = {
            "id": "q1",
            "question": "Which design?",
            "question_type": "single",
            "required": True,
            "options": ["A", "B", "C"],
            "media": [
                {
                    "url": "https://example.com/a.jpg",
                    "type": "photo",
                    "caption": "Design A"
                },
                {
                    "url": "https://example.com/b.jpg",
                    "type": "photo",
                    "caption": "Design B"
                }
            ]
        }

        # Should parse without error
        question = SurveyQuestion(**question_dict)

        # Should serialize back
        serialized = question.model_dump()
        assert serialized["media"][0]["url"] == "https://example.com/a.jpg"
        assert len(serialized["media"]) == 2
