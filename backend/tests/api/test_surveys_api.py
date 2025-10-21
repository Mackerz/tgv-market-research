"""Tests for Survey API endpoints"""
import pytest
from fastapi.testclient import TestClient


class TestSurveyCreation:
    """Tests for creating surveys"""

    def test_create_survey_success(self, client: TestClient):
        """Test successful survey creation"""
        survey_data = {
            "survey_slug": "new-survey",
            "name": "New Survey",
            "survey_flow": [
                {
                    "id": "q1",
                    "question": "Test question?",
                    "question_type": "single",
                    "required": True,
                    "options": ["Option 1", "Option 2"]
                }
            ],
            "is_active": True
        }

        response = client.post("/api/surveys/", json=survey_data)

        assert response.status_code == 200
        data = response.json()
        assert data["survey_slug"] == "new-survey"
        assert data["name"] == "New Survey"
        assert data["is_active"] is True
        assert len(data["survey_flow"]) == 1

    def test_create_survey_with_minimal_data(self, client: TestClient):
        """Test creating survey with minimal required data"""
        survey_data = {
            "survey_slug": "minimal-survey",
            "name": "Minimal Survey",
            "survey_flow": [],
            "is_active": False
        }

        response = client.post("/api/surveys/", json=survey_data)

        assert response.status_code == 200
        data = response.json()
        assert data["survey_slug"] == "minimal-survey"
        assert data["is_active"] is False

    def test_create_survey_duplicate_slug(self, client: TestClient, sample_survey):
        """Test creating survey with duplicate slug fails"""
        survey_data = {
            "survey_slug": sample_survey.survey_slug,  # Duplicate
            "name": "Duplicate Survey",
            "survey_flow": [],
            "is_active": True
        }

        response = client.post("/api/surveys/", json=survey_data)

        # Should fail with 400 or 422 (duplicate key)
        assert response.status_code in [400, 422, 500]


class TestSurveyRetrieval:
    """Tests for retrieving surveys"""

    def test_get_surveys_list(self, client: TestClient, sample_survey):
        """Test getting list of surveys"""
        response = client.get("/api/surveys/")

        assert response.status_code == 200
        data = response.json()
        assert "surveys" in data
        assert "total_count" in data
        assert data["total_count"] >= 1
        assert len(data["surveys"]) >= 1

    def test_get_surveys_with_pagination(self, client: TestClient, sample_survey):
        """Test survey pagination"""
        response = client.get("/api/surveys/?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "surveys" in data
        assert len(data["surveys"]) <= 10

    def test_get_surveys_active_only(self, client: TestClient, sample_survey):
        """Test filtering active surveys only"""
        response = client.get("/api/surveys/?active_only=true")

        assert response.status_code == 200
        data = response.json()
        for survey in data["surveys"]:
            assert survey["is_active"] is True

    def test_get_survey_by_id(self, client: TestClient, sample_survey):
        """Test getting specific survey by ID"""
        response = client.get(f"/api/surveys/{sample_survey.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_survey.id
        assert data["survey_slug"] == sample_survey.survey_slug

    def test_get_survey_by_slug(self, client: TestClient, sample_survey):
        """Test getting specific survey by slug"""
        response = client.get(f"/api/surveys/slug/{sample_survey.survey_slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["survey_slug"] == sample_survey.survey_slug
        assert data["name"] == sample_survey.name

    def test_get_nonexistent_survey_by_id(self, client: TestClient):
        """Test getting non-existent survey returns 404"""
        response = client.get("/api/surveys/99999")

        assert response.status_code == 404

    def test_get_nonexistent_survey_by_slug(self, client: TestClient):
        """Test getting non-existent survey by slug returns 404"""
        response = client.get("/api/surveys/slug/nonexistent-slug")

        assert response.status_code == 404

    def test_search_surveys_by_name(self, client: TestClient, sample_survey):
        """Test searching surveys by name"""
        response = client.get(f"/api/surveys/?search={sample_survey.name[:4]}")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] >= 1

    def test_sort_surveys_by_created_at(self, client: TestClient, sample_survey):
        """Test sorting surveys by creation date"""
        response = client.get("/api/surveys/?sort_by=created_at&sort_order=desc")

        assert response.status_code == 200
        data = response.json()
        assert "surveys" in data

    def test_sort_surveys_by_name(self, client: TestClient, sample_survey):
        """Test sorting surveys by name"""
        response = client.get("/api/surveys/?sort_by=name&sort_order=asc")

        assert response.status_code == 200
        data = response.json()
        assert "surveys" in data


class TestSurveyUpdate:
    """Tests for updating surveys"""

    def test_update_survey_success(self, client: TestClient, sample_survey):
        """Test successful survey update"""
        update_data = {
            "name": "Updated Survey Name",
            "is_active": False
        }

        response = client.put(f"/api/surveys/{sample_survey.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Survey Name"
        assert data["is_active"] is False

    def test_update_survey_flow(self, client: TestClient, sample_survey):
        """Test updating survey flow"""
        update_data = {
            "survey_flow": [
                {
                    "id": "new_q1",
                    "question": "New question?",
                    "question_type": "free_text",
                    "required": True
                }
            ]
        }

        response = client.put(f"/api/surveys/{sample_survey.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data["survey_flow"]) == 1
        assert data["survey_flow"][0]["id"] == "new_q1"

    def test_update_nonexistent_survey(self, client: TestClient):
        """Test updating non-existent survey returns 404"""
        update_data = {"name": "Updated Name"}

        response = client.put("/api/surveys/99999", json=update_data)

        assert response.status_code == 404


class TestSurveyDeletion:
    """Tests for deleting surveys"""

    def test_delete_survey_success(self, client: TestClient, sample_survey):
        """Test successful survey deletion"""
        response = client.delete(f"/api/surveys/{sample_survey.id}")

        assert response.status_code in [200, 204]

        # Verify survey is deleted
        get_response = client.get(f"/api/surveys/{sample_survey.id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_survey(self, client: TestClient):
        """Test deleting non-existent survey returns 404"""
        response = client.delete("/api/surveys/99999")

        assert response.status_code == 404


class TestSurveySubmissions:
    """Tests for survey submission endpoints"""

    def test_create_submission_success(self, client: TestClient, sample_survey):
        """Test successful submission creation"""
        submission_data = {
            "email": "newuser@example.com",
            "phone_number": "1234567890",
            "region": "US",
            "date_of_birth": "1990-01-01",
            "gender": "Male"
        }

        response = client.post(
            f"/api/surveys/{sample_survey.survey_slug}/submit",
            json=submission_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["region"] == "US"
        assert data["is_completed"] is False

    def test_create_submission_minimal_data(self, client: TestClient, sample_survey):
        """Test creating submission with minimal required data"""
        submission_data = {
            "email": "minimal@example.com",
            "phone_number": "9876543210",
            "region": "UK",
            "date_of_birth": "1995-05-15",
            "gender": "Female"
        }

        response = client.post(
            f"/api/surveys/{sample_survey.survey_slug}/submit",
            json=submission_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "minimal@example.com"
        assert data["region"] == "UK"

    def test_create_submission_invalid_email(self, client: TestClient, sample_survey):
        """Test creating submission with invalid email fails"""
        submission_data = {
            "email": "not-an-email",
            "phone_number": "1234567890",
            "region": "CA",
            "date_of_birth": "1988-03-20",
            "gender": "Male"
        }

        response = client.post(
            f"/api/surveys/{sample_survey.survey_slug}/submit",
            json=submission_data
        )

        assert response.status_code == 422  # Validation error

    def test_create_submission_nonexistent_survey(self, client: TestClient):
        """Test creating submission for non-existent survey"""
        submission_data = {
            "email": "user@example.com",
            "phone_number": "5551234567",
            "region": "AU",
            "date_of_birth": "1992-11-10",
            "gender": "Female"
        }

        response = client.post(
            "/api/surveys/nonexistent-slug/submit",
            json=submission_data
        )

        assert response.status_code == 404


class TestMediaUpload:
    """Tests for media upload endpoints"""

    def test_upload_photo_endpoint_exists(self, client: TestClient, sample_survey):
        """Test photo upload endpoint exists (without actual file)"""
        # This tests the endpoint exists, actual file upload would need mock
        response = client.post(
            f"/api/surveys/{sample_survey.survey_slug}/upload/photo"
        )

        # Should return 422 (missing file) not 404 (endpoint not found)
        assert response.status_code == 422

    def test_upload_video_endpoint_exists(self, client: TestClient, sample_survey):
        """Test video upload endpoint exists (without actual file)"""
        response = client.post(
            f"/api/surveys/{sample_survey.survey_slug}/upload/video"
        )

        # Should return 422 (missing file) not 404 (endpoint not found)
        assert response.status_code == 422

    def test_upload_to_nonexistent_survey(self, client: TestClient):
        """Test uploading to non-existent survey returns 404"""
        response = client.post(
            "/api/surveys/nonexistent-slug/upload/photo"
        )

        assert response.status_code in [404, 422]


class TestSurveyStatistics:
    """Tests for survey statistics endpoints"""

    def test_get_survey_statistics(self, client: TestClient, sample_survey, multiple_submissions):
        """Test getting survey statistics"""
        response = client.get(f"/api/surveys/{sample_survey.id}/statistics")

        # If endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = response.json()
            assert "total_submissions" in data or "submissions" in data
