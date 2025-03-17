import pytest
from fastapi.testclient import TestClient
from main import app


class TestInquiryAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, client):
        # 사용자 로그인
        login_data = {"username": "test@example.com", "password": "Test1234!"}
        response = client.post("/user/login", data=login_data)
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_create_inquiry(self, client, auth_headers):
        # Given
        inquiry_data = {
            "title": "Test Inquiry",
            "content": "Test Content",
            "type": "GENERAL",
        }

        # When
        response = client.post("/inquiry/", json=inquiry_data, headers=auth_headers)

        # Then
        assert response.status_code == 201
        assert response.json()["title"] == inquiry_data["title"]

    def test_get_user_inquiries(self, client, auth_headers):
        # When
        response = client.get("/inquiry/my", headers=auth_headers)

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), list)
