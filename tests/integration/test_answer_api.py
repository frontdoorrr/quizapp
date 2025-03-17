import pytest
from fastapi.testclient import TestClient
from main import app


class TestAnswerAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def user_token(self, client):
        # 사용자 로그인
        login_data = {"username": "user@example.com", "password": "User1234!"}
        response = client.post("/user/login", data=login_data)
        print("--------------------------------")
        print(response.json().get("access_token"))
        print("--------------------------------")
        return response.json().get("access_token")

    @pytest.fixture
    def admin_token(self, client):
        # 관리자 로그인
        login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        response = client.post("/user/login", data=login_data)
        return response.json().get("access_token")

    @pytest.fixture
    def test_game(self, client, admin_token):
        # 테스트용 게임 생성
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        game_data = {
            "title": "Test Answer API Game",
            "number": 5000,
            "description": "Game for testing answer API",
            "question": "What is the test answer?",
            "answer": "test answer",
            "question_link": "https://example.com/test-question",
            "answer_link": "https://example.com/test-answer",
        }
        response = client.post("/game/", json=game_data, headers=admin_headers)
        return response.json()

    def test_participate_in_game(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 실행
        response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )

        # 검증
        assert response.status_code == 201
        data = response.json()
        assert data["game_id"] == game_id
        assert data["answer"] is None
        assert data["is_correct"] is None
        assert data["score"] is None

    def test_submit_answer_correct(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 게임 참여
        participate_response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )
        assert participate_response.status_code == 201

        # 정답 제출
        answer_data = {"answer": "test answer"}
        response = client.post(
            f"/answer/game/{game_id}", json=answer_data, headers=user_headers
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["answer"] == "test answer"
        assert data["is_correct"] is True

    def test_submit_answer_incorrect(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 게임 참여
        participate_response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )
        assert participate_response.status_code == 201

        # 오답 제출
        answer_data = {"answer": "wrong answer"}
        response = client.post(
            f"/answer/game/{game_id}", json=answer_data, headers=user_headers
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["answer"] == "wrong answer"
        assert data["is_correct"] is False

    def test_get_my_answers(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 게임 참여 및 답변 제출
        client.post(f"/answer/game/{game_id}/participate", headers=user_headers)
        answer_data = {"answer": "test answer"}
        client.post(f"/answer/game/{game_id}", json=answer_data, headers=user_headers)

        # 내 답변 조회
        response = client.get("/answer/my", headers=user_headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(answer["game_id"] == game_id for answer in data)

    def test_get_answer_by_game(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 게임 참여 및 답변 제출
        client.post(f"/answer/game/{game_id}/participate", headers=user_headers)
        answer_data = {"answer": "test answer"}
        client.post(f"/answer/game/{game_id}", json=answer_data, headers=user_headers)

        # 특정 게임에 대한 내 답변 조회
        response = client.get(f"/answer/game/{game_id}/my", headers=user_headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["game_id"] == game_id
        assert data["answer"] == "test answer"
        assert data["is_correct"] is True

    def test_get_all_answers_by_game_admin(
        self, client, admin_token, user_token, test_game
    ):
        # 설정
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 사용자가 게임 참여 및 답변 제출
        client.post(f"/answer/game/{game_id}/participate", headers=user_headers)
        answer_data = {"answer": "test answer"}
        client.post(f"/answer/game/{game_id}", json=answer_data, headers=user_headers)

        # 관리자가 특정 게임의 모든 답변 조회
        response = client.get(f"/answer/game/{game_id}", headers=admin_headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["game_id"] == game_id

    def test_get_all_answers_by_game_user_forbidden(
        self, client, user_token, test_game
    ):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 일반 사용자가 특정 게임의 모든 답변 조회 시도 (권한 없음)
        response = client.get(f"/answer/game/{game_id}", headers=user_headers)

        # 검증
        assert response.status_code == 403  # 접근 거부

    def test_participate_in_closed_game(
        self, client, user_token, admin_token, test_game
    ):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        game_id = test_game["id"]

        # 관리자가 게임 종료
        client.post(f"/game/{game_id}/close", headers=admin_headers)

        # 종료된 게임에 참여 시도
        response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )

        # 검증
        assert response.status_code == 400  # 게임이 이미 종료됨

    def test_participate_in_nonexistent_game(self, client, user_token):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        nonexistent_game_id = "01HNONEXISTENTGAMEID1234"

        # 존재하지 않는 게임에 참여 시도
        response = client.post(
            f"/answer/game/{nonexistent_game_id}/participate", headers=user_headers
        )

        # 검증
        assert response.status_code == 404  # 게임을 찾을 수 없음

    def test_submit_answer_without_participation(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 참여 없이 바로 답변 제출 시도
        answer_data = {"answer": "test answer"}
        response = client.post(
            f"/answer/game/{game_id}", json=answer_data, headers=user_headers
        )

        # 검증
        assert response.status_code == 404  # 참여 기록을 찾을 수 없음

    def test_submit_answer_to_closed_game(
        self, client, user_token, admin_token, test_game
    ):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        game_id = test_game["id"]

        # 게임 참여
        participate_response = client.post(
            f"/answer/game/{game_id}/participate", headers=user_headers
        )
        assert participate_response.status_code == 201

        # 관리자가 게임 종료
        client.post(f"/game/{game_id}/close", headers=admin_headers)

        # 종료된 게임에 답변 제출 시도
        answer_data = {"answer": "test answer"}
        response = client.post(
            f"/answer/game/{game_id}", json=answer_data, headers=user_headers
        )

        # 검증
        assert response.status_code == 400  # 게임이 이미 종료됨

    def test_submit_answer_twice(self, client, user_token, test_game):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        game_id = test_game["id"]

        # 게임 참여
        client.post(f"/answer/game/{game_id}/participate", headers=user_headers)

        # 첫 번째 답변 제출
        first_answer_data = {"answer": "first answer"}
        first_response = client.post(
            f"/answer/game/{game_id}", json=first_answer_data, headers=user_headers
        )
        assert first_response.status_code == 200

        # 두 번째 답변 제출 시도
        second_answer_data = {"answer": "second answer"}
        second_response = client.post(
            f"/answer/game/{game_id}", json=second_answer_data, headers=user_headers
        )

        # 검증
        assert second_response.status_code == 400  # 이미 답변이 제출됨

    def test_get_nonexistent_answer(self, client, user_token):
        # 설정
        user_headers = {"Authorization": f"Bearer {user_token}"}
        nonexistent_game_id = "01HNONEXISTENTGAMEID1234"

        # 존재하지 않는 게임에 대한 답변 조회 시도
        response = client.get(
            f"/answer/game/{nonexistent_game_id}/my", headers=user_headers
        )

        # 검증
        assert response.status_code == 404  # 답변을 찾을 수 없음
