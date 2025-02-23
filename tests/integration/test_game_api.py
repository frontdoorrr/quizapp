import pytest
from fastapi.testclient import TestClient
from main import app


class TestGameAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, client):
        # 관리자 로그인
        login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        response = client.post("/user/login", data=login_data)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_game(self, client, auth_headers):
        # Given
        game_data = {
            "title": "Test Game",
            "description": "Test Description",
            "difficulty": "EASY",
            "answer": "test answer",
            "hint": "test hint",
            "max_players": 100,
        }

        # When
        response = client.post("/game/", json=game_data, headers=auth_headers)

        # Then
        assert response.status_code == 201
        assert response.json()["title"] == game_data["title"]

    def test_get_active_games(self, client):
        # When
        response = client.get("/game/active")

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), list)
