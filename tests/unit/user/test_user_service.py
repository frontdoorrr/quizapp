import pytest
from datetime import datetime
from user.application.user_service import UserService
from user.domain.user import User, Role
from common.exceptions import AuthenticationError


class TestUserService:
    @pytest.fixture
    def user_service(self, mocker):
        self.user_repo = mocker.Mock()
        self.login_history_repo = mocker.Mock()
        self.redis_client = mocker.Mock()
        self.email_sender = mocker.Mock()
        return UserService(
            user_repo=self.user_repo,
            login_history_repo=self.login_history_repo,
            redis=self.redis_client,
            email_sender=self.email_sender,
        )

    def test_create_user(self, user_service):
        # Given
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test1234!",
            "role": Role.USER,
            "birth": datetime.now().date(),
            "phone": "010-1234-5678",
            "nickname": "testuser",
        }

        # When
        user = user_service.create_user(**user_data)

        # Then
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
        assert user.role == Role.USER

    def test_login_success(self, user_service):
        # Given
        email = "test@example.com"
        password = "Test1234!"
        mock_user = User(
            id="test-id",
            email=email,
            password="hashed_password",
            role=Role.USER,
            name="Test User",
            birth=datetime.now().date(),
            phone="010-1234-5678",
            nickname="testuser",
            point=0,
            coin=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.user_repo.find_by_email.return_value = mock_user

        # When
        result = user_service.login(email=email, password=password)

        # Then
        assert "access_token" in result
        assert result["token_type"] == "bearer"

    def test_login_fail_invalid_password(self, user_service):
        # Given
        email = "test@example.com"
        password = "WrongPassword123!"
        mock_user = User(
            id="test-id",
            email=email,
            password="different_hash",
            role=Role.USER,
            name="Test User",
            birth=datetime.now().date(),
            phone="010-1234-5678",
            nickname="testuser",
            point=0,
            coin=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.user_repo.find_by_email.return_value = mock_user

        # When/Then
        with pytest.raises(AuthenticationError):
            user_service.login(email=email, password=password)

    def test_send_verification_email(self, user_service):
        # Given
        email = "test@example.com"

        # When
        user_service.send_verification_email(email)

        # Then
        assert self.email_sender.send_verification_email.called
        assert self.redis_client.set.called
