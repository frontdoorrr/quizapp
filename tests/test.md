# 퀴즈 앱 테스트 실행 가이드

이 문서는 퀴즈 앱의 테스트를 실행하는 방법에 대한 가이드입니다.

## 목차

1. [테스트 개요](#테스트-개요)
2. [테스트 환경 설정](#테스트-환경-설정)
3. [테스트 실행 방법](#테스트-실행-방법)
4. [테스트 종류별 실행 방법](#테스트-종류별-실행-방법)
5. [테스트 결과 확인](#테스트-결과-확인)
6. [테스트 작성 가이드](#테스트-작성-가이드)

## 테스트 개요

퀴즈 앱은 다음과 같은 테스트 구조를 가지고 있습니다:

- **단위 테스트(Unit Tests)**: 개별 컴포넌트의 기능을 테스트
- **통합 테스트(Integration Tests)**: 여러 컴포넌트 간의 상호작용을 테스트
- **엔드투엔드 테스트(E2E Tests)**: 전체 시스템의 흐름을 테스트

## 테스트 환경 설정

### 로컬 환경에서 테스트 실행

1. 가상 환경 활성화:
   ```bash
   # Poetry 사용
   poetry shell
   
   # 또는 일반 가상 환경 사용
   source venv/bin/activate
   ```

2. 테스트 의존성 설치:
   ```bash
   poetry install
   ```

### Docker 환경에서 테스트 실행

Docker 환경에서 테스트를 실행하려면:

```bash
# Docker 컨테이너 빌드
docker-compose build

# 테스트 실행
docker-compose run --rm app pytest
```

## 테스트 실행 방법

### 모든 테스트 실행

```bash
# 프로젝트 루트 디렉토리에서
pytest

# 또는 상세 출력과 함께
pytest -v
```

### 특정 테스트 파일 실행

```bash
# 특정 테스트 파일 실행
pytest tests/unit/game/test_game_service.py

# 특정 디렉토리의 모든 테스트 실행
pytest tests/unit/
```

### 특정 테스트 함수 실행

```bash
# 특정 테스트 함수 실행
pytest tests/unit/game/test_game_service.py::TestGameService::test_create_game

# 특정 키워드가 포함된 테스트만 실행
pytest -k "create or update"
```

## 테스트 종류별 실행 방법

### 단위 테스트 실행

```bash
# 모든 단위 테스트 실행
pytest tests/unit/

# 특정 모듈의 단위 테스트 실행
pytest tests/unit/game/
pytest tests/unit/user/
pytest tests/unit/answer/
pytest tests/unit/inquiry/
```

### 통합 테스트 실행

```bash
# 모든 통합 테스트 실행
pytest tests/integration/

# 특정 API의 통합 테스트 실행
pytest tests/integration/test_user_api.py
```

### E2E 테스트 실행

```bash
# 모든 E2E 테스트 실행
pytest tests/e2e/
```

## 테스트 결과 확인

### 테스트 결과 형식 지정

```bash
# 자세한 출력으로 테스트 결과 확인
pytest -v

# 더 자세한 정보 표시
pytest -vv

# 실패한 테스트만 표시
pytest --failed-first
```

### 테스트 커버리지 확인

```bash
# 테스트 커버리지 실행 및 보고서 생성
pytest --cov=.

# HTML 형식의 커버리지 보고서 생성
pytest --cov=. --cov-report=html
```

커버리지 보고서는 `htmlcov/index.html`에서 확인할 수 있습니다.

## 테스트 작성 가이드

### 단위 테스트 작성 예시

```python
import pytest
from datetime import datetime
from game.application.game_service import GameService
from game.domain.game import Game, GameStatus

class TestGameService:
    @pytest.fixture
    def game_service(self, mocker):
        self.game_repo = mocker.Mock()
        self.redis_client = mocker.Mock()
        return GameService(game_repo=self.game_repo, redis_client=self.redis_client)

    def test_create_game(self, game_service):
        # Given
        game_data = {
            "title": "Test Game",
            "number": 1,
            "description": "Test Description",
        }

        # When
        game = game_service.create_game(**game_data)

        # Then
        assert game.title == game_data["title"]
        assert game.number == game_data["number"]
        assert game.description == game_data["description"]
        assert game.status == GameStatus.DRAFT
        assert self.game_repo.save.called
```

### 통합 테스트 작성 예시

```python
import pytest
from fastapi.testclient import TestClient
from main import app

class TestUserAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_register_user(self, client):
        # 설정 및 실행
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test1234!",
            "birth": "1990-01-01",
            "phone": "010-1234-5678",
            "nickname": "testuser",
        }
        response = client.post("/user/register", json=user_data)

        # 검증
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "password" not in data
```

### 테스트 픽스처 활용

테스트에서 공통으로 사용되는 객체는 픽스처로 정의하여 재사용할 수 있습니다:

```python
@pytest.fixture
def test_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Test1234!",
        "birth": "1990-01-01",
        "phone": "010-1234-5678",
        "nickname": "testuser",
    }

@pytest.fixture
def registered_user(client, test_user_data):
    response = client.post("/user/register", json=test_user_data)
    return response.json()
```

### 모킹(Mocking) 활용

외부 의존성이 있는 테스트는 모킹을 활용하여 격리된 환경에서 테스트할 수 있습니다:

```python
def test_close_game(self, game_service, mocker):
    # Given
    game_id = "test-game-id"
    mock_game = mocker.Mock(status=GameStatus.ACTIVE)
    self.game_repo.find_by_id.return_value = mock_game

    # When
    game_service.close_game(game_id)

    # Then
    assert mock_game.status == GameStatus.CLOSED
    self.redis_client.enqueue.assert_called_once_with({"game_id": game_id})
```

## 추가 리소스

- [Pytest 공식 문서](https://docs.pytest.org/)
- [FastAPI 테스트 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
