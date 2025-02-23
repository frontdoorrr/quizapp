import pytest
from fastapi.testclient import TestClient
from main import app


class TestUserAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_create_user(self, client):
        # Given
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test1234!",
            "birth": "1990-01-01",
            "phone": "010-1234-5678",
            "nickname": "testuser",
        }

        # When
        response = client.post("/user/register", json=user_data)

        # Then
        assert response.status_code == 201
        assert response.json()["email"] == user_data["email"]

    def test_check_email_exists(self, client):
        # Given
        email = "test@example.com"

        # When
        response = client.get(f"/user/check-email/{email}")

        # Then
        assert response.status_code == 200
        assert "exists" in response.json()

    def test_check_nickname_exists(self, client):
        # Given
        nickname = "testuser"

        # When
        response = client.get(f"/user/check-nickname/{nickname}")

        # Then
        assert response.status_code == 200
        assert "exists" in response.json()
