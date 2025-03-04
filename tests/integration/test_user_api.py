import pytest
from fastapi.testclient import TestClient
from main import app
from jose import jwt
from config import get_settings

settings = get_settings()


class TestUserAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def test_user_data(self):
        return {
            "name": "Test User",
            "email": "test_api@example.com",
            "password": "Test1234!",
            "birth": "1990-01-01",
            "phone": "010-1234-5678",
            "nickname": "testapi",
        }

    @pytest.fixture
    def registered_user(self, client, test_user_data):
        response = client.post("/user/register", json=test_user_data)
        return response.json()

    @pytest.fixture
    def user_token(self, client, test_user_data):
        # 사용자 로그인
        login_data = {"username": test_user_data["email"], "password": test_user_data["password"]}
        response = client.post("/user/login", data=login_data)
        return response.json()["access_token"]

    def test_register_user(self, client, test_user_data):
        # 설정 및 실행
        response = client.post("/user/register", json=test_user_data)

        # 검증
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]
        assert data["nickname"] == test_user_data["nickname"]
        assert "password" not in data  # 비밀번호는 응답에 포함되지 않아야 함

    def test_register_user_duplicate_email(self, client, registered_user, test_user_data):
        # 설정 - 이미 등록된 이메일로 다시 등록 시도
        duplicate_user_data = test_user_data.copy()
        duplicate_user_data["nickname"] = "different_nickname"

        # 실행
        response = client.post("/user/register", json=duplicate_user_data)

        # 검증
        assert response.status_code == 400  # 이메일 중복으로 인한 오류

    def test_register_user_duplicate_nickname(self, client, registered_user, test_user_data):
        # 설정 - 이미 등록된 닉네임으로 다시 등록 시도
        duplicate_user_data = test_user_data.copy()
        duplicate_user_data["email"] = "different_email@example.com"

        # 실행
        response = client.post("/user/register", json=duplicate_user_data)

        # 검증
        assert response.status_code == 400  # 닉네임 중복으로 인한 오류

    def test_login_user(self, client, registered_user, test_user_data):
        # 설정
        login_data = {"username": test_user_data["email"], "password": test_user_data["password"]}

        # 실행
        response = client.post("/user/login", data=login_data)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # 토큰 검증
        token = data["access_token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["email"] == test_user_data["email"]

    def test_login_user_invalid_credentials(self, client, registered_user):
        # 설정 - 잘못된 비밀번호
        login_data = {"username": registered_user["email"], "password": "WrongPassword1234!"}

        # 실행
        response = client.post("/user/login", data=login_data)

        # 검증
        assert response.status_code == 401  # 인증 실패

    def test_get_current_user(self, client, user_token):
        # 설정
        headers = {"Authorization": f"Bearer {user_token}"}

        # 실행
        response = client.get("/user/me", headers=headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "name" in data
        assert "nickname" in data
        assert "password" not in data  # 비밀번호는 응답에 포함되지 않아야 함

    def test_get_current_user_no_token(self, client):
        # 토큰 없이 요청
        response = client.get("/user/me")

        # 검증
        assert response.status_code == 401  # 인증 실패

    def test_update_user(self, client, user_token):
        # 설정
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {
            "name": "Updated Name",
            "nickname": "updated_nickname",
            "phone": "010-9876-5432"
        }

        # 실행
        response = client.put("/user/me", json=update_data, headers=headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["nickname"] == update_data["nickname"]
        assert data["phone"] == update_data["phone"]

    def test_update_user_no_token(self, client):
        # 토큰 없이 요청
        update_data = {"name": "Updated Name"}
        response = client.put("/user/me", json=update_data)

        # 검증
        assert response.status_code == 401  # 인증 실패

    def test_change_password(self, client, user_token, test_user_data):
        # 설정
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "old_password": test_user_data["password"],
            "new_password": "NewPassword1234!"
        }

        # 실행
        response = client.post("/user/change-password", json=password_data, headers=headers)

        # 검증
        assert response.status_code == 200
        
        # 새 비밀번호로 로그인 시도
        login_data = {"username": test_user_data["email"], "password": "NewPassword1234!"}
        login_response = client.post("/user/login", data=login_data)
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, client, user_token):
        # 설정
        headers = {"Authorization": f"Bearer {user_token}"}
        password_data = {
            "old_password": "WrongPassword1234!",
            "new_password": "NewPassword1234!"
        }

        # 실행
        response = client.post("/user/change-password", json=password_data, headers=headers)

        # 검증
        assert response.status_code == 401  # 인증 실패

    def test_check_email_exists(self, client, registered_user):
        # 설정 - 존재하는 이메일
        email = registered_user["email"]

        # 실행
        response = client.get(f"/user/check-email/{email}")

        # 검증
        assert response.status_code == 200
        assert response.json()["exists"] == True

    def test_check_email_not_exists(self, client):
        # 설정 - 존재하지 않는 이메일
        email = "nonexistent@example.com"

        # 실행
        response = client.get(f"/user/check-email/{email}")

        # 검증
        assert response.status_code == 200
        assert response.json()["exists"] == False

    def test_check_nickname_exists(self, client, registered_user):
        # 설정 - 존재하는 닉네임
        nickname = registered_user["nickname"]

        # 실행
        response = client.get(f"/user/check-nickname/{nickname}")

        # 검증
        assert response.status_code == 200
        assert response.json()["exists"] == True

    def test_check_nickname_not_exists(self, client):
        # 설정 - 존재하지 않는 닉네임
        nickname = "nonexistent_nickname"

        # 실행
        response = client.get(f"/user/check-nickname/{nickname}")

        # 검증
        assert response.status_code == 200
        assert response.json()["exists"] == False

    def test_get_user_by_id_admin(self, client):
        # 관리자 로그인
        admin_login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        admin_login_response = client.post("/user/login", data=admin_login_data)
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 사용자 등록
        user_data = {
            "name": "User For Admin",
            "email": "user_for_admin@example.com",
            "password": "User1234!",
            "birth": "1990-01-01",
            "phone": "010-1111-2222",
            "nickname": "user_for_admin",
        }
        register_response = client.post("/user/register", json=user_data)
        user_id = register_response.json()["id"]

        # 관리자가 사용자 정보 조회
        response = client.get(f"/user/{user_id}", headers=admin_headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == user_data["email"]
        assert data["nickname"] == user_data["nickname"]

    def test_get_user_by_id_forbidden(self, client, user_token, registered_user):
        # 일반 사용자가 다른 사용자 정보 조회 시도 (권한 없음)
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # 관리자 ID로 가정
        admin_id = "01HADMIN12345678ABCDEFGHJK"
        
        response = client.get(f"/user/{admin_id}", headers=headers)

        # 검증
        assert response.status_code == 403  # 접근 거부

    def test_get_all_users_admin(self, client):
        # 관리자 로그인
        admin_login_data = {"username": "admin@example.com", "password": "Admin1234!"}
        admin_login_response = client.post("/user/login", data=admin_login_data)
        admin_token = admin_login_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # 관리자가 모든 사용자 조회
        response = client.get("/user/", headers=admin_headers)

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_all_users_forbidden(self, client, user_token):
        # 일반 사용자가 모든 사용자 조회 시도 (권한 없음)
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/user/", headers=headers)

        # 검증
        assert response.status_code == 403  # 접근 거부
