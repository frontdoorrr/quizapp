import pytest
from fastapi.testclient import TestClient
from main import app


class TestGameFlow:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def user_token(self, client):
        # 1. 회원가입
        register_data = {
            "name": "Test Player",
            "email": "player@example.com",
            "password": "Player1234!",
            "birth": "1990-01-01",
            "phone": "010-1234-5678",
            "nickname": "testplayer",
        }
        client.post("/user/register", json=register_data)

        # 2. 로그인
        login_data = {"username": "player@example.com", "password": "Player1234!"}
        response = client.post("/user/login", data=login_data)
        return response.json()["access_token"]

    @pytest.fixture
    def admin_token(self, client):
        # 관리자 로그인
        login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        response = client.post("/user/login", data=login_data)
        return response.json()["access_token"]

    def test_complete_game_flow(self, client, user_token, admin_token):
        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 관리자가 게임 생성
        game_data = {
            "title": "E2E Test Game",
            "description": "Test game for E2E testing",
            "difficulty": "EASY",
            "answer": "correct answer",
            "hint": "test hint",
            "max_players": 100,
        }
        game_response = client.post("/game/", json=game_data, headers=admin_headers)
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]

        # 2. 사용자가 활성 게임 목록 조회
        games_response = client.get("/game/active", headers=user_headers)
        assert games_response.status_code == 200
        assert len(games_response.json()) > 0
        assert any(game["id"] == game_id for game in games_response.json())

        # 3. 사용자가 게임에 참여 (답안 생성)
        participate_response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )
        assert participate_response.status_code == 201
        answer_id = participate_response.json()["id"]

        # 4. 사용자가 오답 제출
        wrong_answer_data = {"answer": "wrong answer"}
        submit_response = client.post(
            f"/answer/game/{game_id}", json=wrong_answer_data, headers=user_headers
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["is_correct"] == False

        # 5. 사용자가 정답 제출
        correct_answer_data = {"answer": "correct answer"}
        submit_response = client.post(
            f"/answer/game/{game_id}", json=correct_answer_data, headers=user_headers
        )
        assert submit_response.status_code == 200
        assert submit_response.json()["is_correct"] == True

        # 6. 사용자가 자신의 답안 이력 조회
        history_response = client.get("/answer/my", headers=user_headers)
        assert history_response.status_code == 200
        assert len(history_response.json()) > 0
        assert any(answer["id"] == answer_id for answer in history_response.json())

        # 7. 문의사항 등록
        inquiry_data = {
            "title": "Game Feedback",
            "content": "Great game!",
            "type": "GENERAL",
        }
        inquiry_response = client.post(
            "/inquiry/", json=inquiry_data, headers=user_headers
        )
        assert inquiry_response.status_code == 201
        inquiry_id = inquiry_response.json()["id"]

        # 8. 관리자가 문의사항 답변
        answer_data = {"answer": "Thank you for playing!"}
        admin_response = client.post(
            f"/inquiry/{inquiry_id}/answer", json=answer_data, headers=admin_headers
        )
        assert admin_response.status_code == 200
        assert admin_response.json()["status"] == "ANSWERED"

        # 9. 사용자가 문의사항 확인
        inquiry_check_response = client.get(
            f"/inquiry/{inquiry_id}", headers=user_headers
        )
        assert inquiry_check_response.status_code == 200
        assert inquiry_check_response.json()["answer"] == answer_data["answer"]
