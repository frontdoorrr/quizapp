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
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    def test_create_game(self, client, auth_headers):
        # Given
        game_data = {
            "title": "Test Game",
            "number": 1,
            "description": "Test Description",
            "question": "Test Question",
            "answer": "Test Answer",
            "question_link": "https://example.com/question",
            "answer_link": "https://example.com/answer",
        }

        # When
        response = client.post("/game/", json=game_data, headers=auth_headers)
        print(
            "************************************************************************"
        )
        print(response.json())
        print(
            "************************************************************************"
        )

        # Then
        assert response.status_code == 201
        assert response.json()["title"] == game_data["title"]
        assert response.json()["number"] == game_data["number"]
        assert response.json()["description"] == game_data["description"]
        assert response.json()["question"] == game_data["question"]
        assert response.json()["answer"] == game_data["answer"]
        assert response.json()["question_link"] == game_data["question_link"]
        assert response.json()["answer_link"] == game_data["answer_link"]
        assert response.json()["status"] == "DRAFT"

        return response.json()["id"]  # 다른 테스트에서 사용할 수 있도록 ID 반환

    def test_get_game_by_id(self, client, auth_headers):
        # Given
        game_id = self.test_create_game(client, auth_headers)

        # When
        response = client.get(f"/game/{game_id}", headers=auth_headers)

        # Then
        assert response.status_code == 200
        assert response.json()["id"] == game_id
        assert response.json()["title"] == "Test Game"

    def test_get_game_not_found(self, client, auth_headers):
        # When
        response = client.get("/game/non-existent-id", headers=auth_headers)

        # Then
        assert (
            response.status_code == 404 or response.status_code == 500
        )  # 서버 구현에 따라 다를 수 있음

    def test_update_game(self, client, auth_headers):
        # Given
        game_id = self.test_create_game(client, auth_headers)
        update_data = {
            "title": "Updated Game",
            "description": "Updated Description",
            "question": "Updated Question",
            "answer": "Updated Answer",
            "question_link": "https://example.com/updated-question",
            "answer_link": "https://example.com/updated-answer",
        }

        # When
        response = client.put(
            f"/game/{game_id}", json=update_data, headers=auth_headers
        )

        # Then
        assert response.status_code == 200
        assert response.json()["title"] == update_data["title"]
        assert response.json()["description"] == update_data["description"]
        assert response.json()["question"] == update_data["question"]
        assert response.json()["answer"] == update_data["answer"]
        assert response.json()["question_link"] == update_data["question_link"]
        assert response.json()["answer_link"] == update_data["answer_link"]

        # 변경 사항이 실제로 저장되었는지 확인
        get_response = client.get(f"/game/{game_id}", headers=auth_headers)
        assert get_response.json()["title"] == update_data["title"]

    def test_get_games(self, client, auth_headers):
        # Given - 여러 게임 생성
        for i in range(3):
            game_data = {
                "title": f"Test Game {i}",
                "number": i + 1,
                "description": f"Test Description {i}",
                "question": f"Test Question {i}",
                "answer": f"Test Answer {i}",
                "question_link": f"https://example.com/question/{i}",
                "answer_link": f"https://example.com/answer/{i}",
            }
            client.post("/game/", json=game_data, headers=auth_headers)

        # When
        response = client.get("/game", headers=auth_headers)

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 3  # 최소 3개 이상의 게임이 있어야 함

    def test_get_games_by_status(self, client, auth_headers):
        # Given - 게임 생성
        game_id = self.test_create_game(client, auth_headers)

        # When - 상태별로 게임 조회
        response = client.get("/game?status=draft", headers=auth_headers)

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert any(game["id"] == game_id for game in response.json())
        assert all(game["status"] == "DRAFT" for game in response.json())

    def test_get_current_game(self, client, auth_headers):
        # Given - 여러 게임 생성 (마지막 게임이 가장 높은 번호를 가짐)
        for i in range(3):
            game_data = {
                "title": f"Test Game {i}",
                "number": i + 100,  # 높은 번호 사용
                "description": f"Test Description {i}",
                "question": f"Test Question {i}",
                "answer": f"Test Answer {i}",
                "question_link": f"https://example.com/question/{i}",
                "answer_link": f"https://example.com/answer/{i}",
            }
            client.post("/game/", json=game_data, headers=auth_headers)

        # When
        response = client.get("/game/current/", headers=auth_headers)

        # Then
        assert response.status_code == 200
        assert (
            response.json()["number"] == 102
        )  # 가장 높은 번호 (0, 1, 2 -> 100, 101, 102)
        assert response.json()["title"] == "Test Game 2"  # 마지막으로 생성된 게임

    def test_close_game(self, client, auth_headers):
        # Given
        game_data = {
            "title": "Game to Close",
            "number": 999,
            "description": "This game will be closed",
            "question": "Close me?",
            "answer": "Yes",
            "question_link": "https://example.com/close",
            "answer_link": "https://example.com/closed",
        }
        create_response = client.post("/game/", json=game_data, headers=auth_headers)
        game_id = create_response.json()["id"]

        # When
        close_response = client.post(f"/game/{game_id}/close", headers=auth_headers)

        # Then
        assert close_response.status_code == 200
        assert close_response.json()["status"] == "CLOSED"
        assert close_response.json()["closed_at"] is not None

        # 게임이 실제로 종료되었는지 확인
        get_response = client.get(f"/game/{game_id}", headers=auth_headers)
        assert get_response.json()["status"] == "CLOSED"

    def test_close_already_closed_game(self, client, auth_headers):
        # Given - 게임 생성 및 종료
        game_data = {
            "title": "Already Closed Game",
            "number": 888,
            "description": "This game is already closed",
            "question": "Close me again?",
            "answer": "No",
            "question_link": "https://example.com/already-closed",
            "answer_link": "https://example.com/already-closed-answer",
        }
        create_response = client.post("/game/", json=game_data, headers=auth_headers)
        game_id = create_response.json()["id"]

        # 게임 종료
        client.post(f"/game/{game_id}/close", headers=auth_headers)

        # When - 이미 종료된 게임을 다시 종료 시도
        second_close_response = client.post(
            f"/game/{game_id}/close", headers=auth_headers
        )

        # Then
        assert (
            second_close_response.status_code == 400
        )  # Bad Request 또는 다른 에러 코드
