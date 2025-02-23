import pytest
from fastapi.testclient import TestClient
from main import app


class TestUserFlow:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_user_registration_and_login_flow(self, client):
        # 1. 회원가입
        register_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test1234!",
            "birth": "1990-01-01",
            "phone": "010-1234-5678",
            "nickname": "testuser",
        }
        register_response = client.post("/user/register", json=register_data)
        assert register_response.status_code == 201

        # 2. 로그인
        login_data = {"username": "test@example.com", "password": "Test1234!"}
        login_response = client.post("/user/login", data=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. 프로필 조회
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/user/me", headers=headers)
        assert profile_response.status_code == 200

    def test_complete_game_flow(self, client):
        # 1. 로그인 및 토큰 획득
        login_data = {"username": "test@example.com", "password": "Test1234!"}
        login_response = client.post("/user/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 게임 참여
        game_response = client.get("/game/active", headers=headers)
        assert game_response.status_code == 200
        game_id = game_response.json()["id"]

        # 3. 답안 제출
        answer_data = {"answer": "test answer"}
        answer_response = client.post(
            f"/answer/game/{game_id}", json=answer_data, headers=headers
        )
        assert answer_response.status_code == 200

        # 4. 결과 확인
        result_response = client.get(
            f"/answer/{answer_response.json()['id']}", headers=headers
        )
        assert result_response.status_code == 200
