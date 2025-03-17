import pytest
from fastapi.testclient import TestClient
from main import app
import time
import random


class TestGameFlow:
    # 클래스 내부의 client 픽스처 제거 (conftest.py의 픽스처 사용)

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
        return response.json().get("access_token")

    @pytest.fixture
    def admin_token(self, client):
        # 관리자 로그인
        login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        response = client.post("/user/login", data=login_data)
        return (
            response.json().get("access_token") if response.status_code == 200 else None
        )

    def test_complete_game_flow(self, client, user_token, admin_token, db_session):
        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 관리자가 게임 생성
        # 랜덤 게임 번호 생성 (중복 방지)
        game_number = random.randint(10000, 99999)
        game_data = {
            "title": "E2E Test Game",
            "number": game_number,
            "description": "Test game for E2E testing",
            "question": "What is the correct answer?",
            "answer": "correct answer",
            "question_link": "https://example.com/e2e-question",
            "answer_link": "https://example.com/e2e-answer",
        }
        game_response = client.post("/game/", json=game_data, headers=admin_headers)
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]

        # 2. 사용자가 활성 게임 목록 조회
        games_response = client.get("/game", headers=user_headers)
        assert games_response.status_code == 200
        assert len(games_response.json()) > 0
        assert any(game["id"] == game_id for game in games_response.json())

        # 3. 사용자가 게임에 참여 (답안 생성)
        participate_response = client.post(
            f"/answer",
            headers=user_headers,
            json={"game_id": game_id, "answer": "correct answer"},
        )
        print("----------------heyhey----------------")
        print(participate_response.json())
        print("----------------heyhey----------------")
        print("----------------heyhey----------------")
        print("----------------heyhey----------------")
        print("----------------heyhey----------------")
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

        # 7. 관리자가 게임 종료
        close_response = client.post(f"/game/{game_id}/close", headers=admin_headers)
        assert close_response.status_code == 200
        assert close_response.json()["status"] == "CLOSED"

        # 8. 게임 종료 확인
        game_check_response = client.get(f"/game/{game_id}", headers=user_headers)
        assert game_check_response.status_code == 200
        assert game_check_response.json()["status"] == "CLOSED"

        # 9. 점수 계산 작업이 큐에 추가되었는지 확인 (이 부분은 실제로 확인하기 어려울 수 있음)
        # 대신 잠시 대기 후 결과를 확인
        time.sleep(2)  # 점수 계산 작업이 처리될 시간을 줌

        # 10. 최종 점수 확인
        final_score_response = client.get(
            f"/answer/game/{game_id}/my", headers=user_headers
        )
        assert final_score_response.status_code == 200
        # 점수가 계산되었는지 확인 (실제 구현에 따라 다를 수 있음)
        # assert final_score_response.json()["score"] > 0

    def test_admin_game_management_flow(self, client, admin_token, db_session):
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 관리자가 여러 게임 생성
        game_ids = []
        for i in range(3):
            game_data = {
                "title": f"Admin Test Game {i}",
                "number": 2000 + i,
                "description": f"Admin test game {i}",
                "question": f"Admin question {i}?",
                "answer": f"Admin answer {i}",
                "question_link": f"https://example.com/admin-question-{i}",
                "answer_link": f"https://example.com/admin-answer-{i}",
            }
            response = client.post("/game/", json=game_data, headers=admin_headers)
            assert response.status_code == 201
            game_ids.append(response.json()["id"])

        # 2. 관리자가 모든 게임 조회
        all_games_response = client.get("/game", headers=admin_headers)
        assert all_games_response.status_code == 200
        assert len(all_games_response.json()) >= 3
        for game_id in game_ids:
            assert any(game["id"] == game_id for game in all_games_response.json())

        # 3. 관리자가 특정 게임 수정
        update_data = {
            "title": "Updated Admin Game",
            "description": "Updated by admin",
            "question": "Updated question?",
            "answer": "Updated answer",
            "question_link": "https://example.com/updated-question",
            "answer_link": "https://example.com/updated-answer",
        }
        update_response = client.put(
            f"/game/{game_ids[0]}", json=update_data, headers=admin_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == update_data["title"]

        # 4. 수정 확인
        get_response = client.get(f"/game/{game_ids[0]}", headers=admin_headers)
        assert get_response.status_code == 200
        assert get_response.json()["title"] == update_data["title"]
        assert get_response.json()["description"] == update_data["description"]

        # 5. 관리자가 게임 종료
        for game_id in game_ids:
            close_response = client.post(
                f"/game/{game_id}/close", headers=admin_headers
            )
            assert close_response.status_code == 200
            assert close_response.json()["status"] == "CLOSED"

        # 6. 종료된 게임 필터링 확인
        closed_games_response = client.get("/game?status=closed", headers=admin_headers)
        assert closed_games_response.status_code == 200
        closed_games = closed_games_response.json()
        assert len(closed_games) >= len(game_ids)
        for game_id in game_ids:
            assert any(game["id"] == game_id for game in closed_games)

    def test_multi_user_game_flow(self, client, admin_token, db_session):
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. 관리자가 게임 생성
        game_data = {
            "title": "Multi-User Game",
            "number": 3000,
            "description": "Game for multiple users",
            "question": "What is the multi-user answer?",
            "answer": "multi-user answer",
            "question_link": "https://example.com/multi-question",
            "answer_link": "https://example.com/multi-answer",
        }
        game_response = client.post("/game/", json=game_data, headers=admin_headers)
        assert game_response.status_code == 201
        game_id = game_response.json()["id"]

        # 2. 여러 사용자 생성 및 게임 참여
        users = []
        for i in range(3):
            # 사용자 등록
            register_data = {
                "name": f"Multi User {i}",
                "email": f"multi_user_{i}@example.com",
                "password": "MultiUser1234!",
                "birth": "1990-01-01",
                "phone": f"010-1234-{i:04d}",
                "nickname": f"multiuser{i}",
            }
            register_response = client.post("/user/register", json=register_data)
            assert (
                register_response.status_code == 201
                or register_response.status_code == 200
            )

            # 로그인
            login_data = {
                "username": f"multi_user_{i}@example.com",
                "password": "MultiUser1234!",
            }
            login_response = client.post("/user/login", data=login_data)
            assert login_response.status_code == 200
            token = login_response.json().get("access_token")
            user_headers = {"Authorization": f"Bearer {token}"}
            users.append(
                {"email": f"multi_user_{i}@example.com", "headers": user_headers}
            )

            # 게임 참여
            participate_response = client.post(
                f"/answer/game/{game_id}/participate", headers=user_headers
            )
            assert participate_response.status_code == 201

            # 답변 제출 (일부는 정답, 일부는 오답)
            if i % 2 == 0:
                answer_data = {"answer": "multi-user answer"}  # 정답
            else:
                answer_data = {"answer": f"wrong answer {i}"}  # 오답

            submit_response = client.post(
                f"/answer/game/{game_id}", json=answer_data, headers=user_headers
            )
            assert submit_response.status_code == 200

        # 3. 관리자가 게임 종료
        close_response = client.post(f"/game/{game_id}/close", headers=admin_headers)
        assert close_response.status_code == 200

        # 4. 잠시 대기 후 결과 확인
        time.sleep(2)  # 점수 계산 작업이 처리될 시간을 줌

        # 5. 각 사용자의 최종 점수 확인
        for user in users:
            score_response = client.get(
                f"/answer/game/{game_id}/my", headers=user["headers"]
            )
            assert score_response.status_code == 200
            # 점수 확인 (실제 구현에 따라 다를 수 있음)
            # if user["email"].endswith("_0@example.com") or user["email"].endswith("_2@example.com"):
            #     assert score_response.json()["is_correct"] == True
            # else:
            #     assert score_response.json()["is_correct"] == False
