import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, date
import bcrypt
from jose import jwt

from user.application.user_service import UserService
from user.domain.user import User
from user.infra.repository.user_repo import UserRepository
from ulid import ULID
from config import get_settings

settings = get_settings()


class TestUserService:
    @pytest.fixture
    def ulid(self):
        return ULID()

    @pytest.fixture
    def user_repo_mock(self):
        return Mock(spec=UserRepository)
        
    @pytest.fixture
    def login_history_repo_mock(self):
        return Mock()

    @pytest.fixture
    def user_service(self, user_repo_mock, login_history_repo_mock, ulid):
        return UserService(
            user_repo=user_repo_mock,
            login_history_repo=login_history_repo_mock,
            
        )

    @pytest.fixture
    def test_user(self):
        # 테스트용 사용자 생성
        password = "Test1234!"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        return User(
            id="01HUSER12345678ABCDEFGHJK",
            name="Test User",
            email="test@example.com",
            password=hashed_password,
            birth="1990-01-01",
            address=None,
            point=0,
            coin=0,
            phone="010-1234-5678",
            nickname="testuser",
            role="USER",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def test_register_user(self, user_service, user_repo_mock, login_history_repo_mock):
        # 설정
        # user_service.check_email_exists.return_value = None  # 이메일 중복 없음
        # user_service.check_nickname_exists.return_value = None  # 닉네임 중복 없음
        
        user_data = {
            "name": "New User",
            "email": "new@example.com",
            "password": "NewUser1234!",
            "birth": "1995-05-05",
            "phone": "010-9876-5432",
            "nickname": "newuser"
        }
        
        # 실행
        result = user_service.create_user(**user_data)
        
        # 검증
        user_repo_mock.find_by_email.assert_called_once_with(user_data["email"])
        user_repo_mock.find_by_nickname.assert_called_once_with(user_data["nickname"])
        user_repo_mock.save.assert_called_once()
        
        assert result.id is not None
        assert result.name == user_data["name"]
        assert result.email == user_data["email"]
        assert result.nickname == user_data["nickname"]
        assert result.role == "USER"  # 기본 역할은 USER
        assert bcrypt.checkpw(user_data["password"].encode("utf-8"), result.password.encode("utf-8"))

    def test_register_user_email_exists(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_email.return_value = test_user  # 이메일 중복
        
        user_data = {
            "name": "Duplicate Email",
            "email": "test@example.com",  # 이미 존재하는 이메일
            "password": "Duplicate1234!",
            "birth": "1995-05-05",
            "phone": "010-9876-5432",
            "nickname": "duplicate"
        }
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.create_user(**user_data)
        
        user_repo_mock.find_by_email.assert_called_once_with(user_data["email"])
        user_repo_mock.save.assert_not_called()

    def test_register_user_nickname_exists(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_email.return_value = None  # 이메일 중복 없음
        user_repo_mock.find_by_nickname.return_value = test_user  # 닉네임 중복
        
        user_data = {
            "name": "Duplicate Nickname",
            "email": "unique@example.com",
            "password": "Duplicate1234!",
            "birth": "1995-05-05",
            "phone": "010-9876-5432",
            "nickname": "testuser"  # 이미 존재하는 닉네임
        }
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.create_user(**user_data)
        
        user_repo_mock.find_by_email.assert_called_once_with(user_data["email"])
        user_repo_mock.find_by_nickname.assert_called_once_with(user_data["nickname"])
        user_repo_mock.save.assert_not_called()

    def test_login_user_success(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_email.return_value = test_user
        password = "Test1234!"  # test_user의 원래 비밀번호
        
        # 실행
        result = user_service.login_user(test_user.email, password)
        
        # 검증
        user_repo_mock.find_by_email.assert_called_once_with(test_user.email)
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
        
        # 토큰 검증
        token = result["access_token"]
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == test_user.id
        assert payload["email"] == test_user.email
        assert payload["role"] == test_user.role

    def test_login_user_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_email.return_value = None  # 사용자가 존재하지 않음
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.login_user("nonexistent@example.com", "Password1234!")
        
        user_repo_mock.find_by_email.assert_called_once_with("nonexistent@example.com")

    def test_login_user_wrong_password(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_email.return_value = test_user
        wrong_password = "WrongPassword1234!"
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.login_user(test_user.email, wrong_password)
        
        user_repo_mock.find_by_email.assert_called_once_with(test_user.email)

    def test_get_user_by_id(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        
        # 실행
        result = user_service.get_user_by_id(test_user.id)
        
        # 검증
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        assert result == test_user

    def test_get_user_by_id_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.get_user_by_id("nonexistent_id")
        
        user_repo_mock.find_by_id.assert_called_once_with("nonexistent_id")

    def test_get_user_by_email(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_email.return_value = test_user
        
        # 실행
        result = user_service.get_user_by_email(test_user.email)
        
        # 검증
        user_repo_mock.find_by_email.assert_called_once_with(test_user.email)
        assert result == test_user

    def test_get_user_by_email_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_email.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.get_user_by_email("nonexistent@example.com")
        
        user_repo_mock.find_by_email.assert_called_once_with("nonexistent@example.com")

    def test_update_user(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        user_repo_mock.find_by_nickname.return_value = None  # 닉네임 중복 없음
        
        update_data = {
            "name": "Updated Name",
            "nickname": "updateduser",
            "phone": "010-5555-5555"
        }
        
        # 실행
        result = user_service.update_user(test_user.id, **update_data)
        
        # 검증
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        user_repo_mock.find_by_nickname.assert_called_once_with(update_data["nickname"])
        user_repo_mock.save.assert_called_once()
        
        assert result.name == update_data["name"]
        assert result.nickname == update_data["nickname"]
        assert result.phone == update_data["phone"]
        assert result.email == test_user.email  # 변경되지 않은 필드

    def test_update_user_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_id.return_value = None
        
        update_data = {
            "name": "Updated Name",
            "nickname": "updateduser"
        }
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.update_user("nonexistent_id", **update_data)
        
        user_repo_mock.find_by_id.assert_called_once_with("nonexistent_id")
        user_repo_mock.save.assert_not_called()

    def test_update_user_nickname_exists(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        
        other_user = User(
            id="01HOTHERUSER12345ABCDEFGHJK",
            name="Other User",
            email="other@example.com",
            password="hashed_password",
            birth="1990-01-01",
            phone="010-1234-5678",
            nickname="otheruser",
            role="USER",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 다른 사용자가 이미 사용 중인 닉네임
        user_repo_mock.find_by_nickname.return_value = other_user
        
        update_data = {
            "nickname": "otheruser"  # 이미 사용 중인 닉네임
        }
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.update_user(test_user.id, **update_data)
        
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        user_repo_mock.find_by_nickname.assert_called_once_with(update_data["nickname"])
        user_repo_mock.save.assert_not_called()

    def test_change_password(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        old_password = "Test1234!"  # test_user의 원래 비밀번호
        new_password = "NewPassword1234!"
        
        # 실행
        result = user_service.change_password(test_user.id, old_password, new_password)
        
        # 검증
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        user_repo_mock.save.assert_called_once()
        
        assert bcrypt.checkpw(new_password.encode("utf-8"), result.password.encode("utf-8"))
        assert not bcrypt.checkpw(old_password.encode("utf-8"), result.password.encode("utf-8"))

    def test_change_password_user_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.change_password("nonexistent_id", "OldPassword", "NewPassword")
        
        user_repo_mock.find_by_id.assert_called_once_with("nonexistent_id")
        user_repo_mock.save.assert_not_called()

    def test_change_password_wrong_old_password(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        wrong_old_password = "WrongPassword1234!"
        new_password = "NewPassword1234!"
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.change_password(test_user.id, wrong_old_password, new_password)
        
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        user_repo_mock.save.assert_not_called()

    def test_delete_user(self, user_service, user_repo_mock, test_user):
        # 설정
        user_repo_mock.find_by_id.return_value = test_user
        
        # 실행
        user_service.delete_user(test_user.id)
        
        # 검증
        user_repo_mock.find_by_id.assert_called_once_with(test_user.id)
        user_repo_mock.delete.assert_called_once_with(test_user.id)

    def test_delete_user_not_found(self, user_service, user_repo_mock):
        # 설정
        user_repo_mock.find_by_id.return_value = None
        
        # 실행 및 검증
        with pytest.raises(Exception):
            user_service.delete_user("nonexistent_id")
        
        user_repo_mock.find_by_id.assert_called_once_with("nonexistent_id")
        user_repo_mock.delete.assert_not_called()
