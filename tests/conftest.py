import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
import os

from database import Base, get_db
from main import app
from scripts.generate_test_data import generate_test_data

# 테스트 데이터베이스 URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@test-db:5432/testdb"
)


@pytest.fixture(scope="session")
def test_engine():
    """테스트 데이터베이스 엔진 생성"""
    engine = create_engine(TEST_DATABASE_URL)

    # 테스트 DB가 존재하면 삭제
    if database_exists(engine.url):
        drop_database(engine.url)

    # 테스트 DB 생성
    create_database(engine.url)

    # 테이블 생성
    Base.metadata.create_all(bind=engine)

    yield engine

    # 테스트 종료 후 DB 삭제
    drop_database(engine.url)


@pytest.fixture(scope="session")
def test_db(test_engine):
    """테스트 데이터베이스 세션 생성"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    return TestingSessionLocal


@pytest.fixture(scope="function")
def db_session(test_db):
    """각 테스트 함수에서 사용할 데이터베이스 세션"""
    db = test_db()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """테스트 클라이언트"""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 의존성 재설정
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_data(test_db):
    """테스트 데이터 생성"""
    db = test_db()
    try:
        # 관리자 계정 생성
        from user.infra.db_models.user import User
        from user.domain.user import Role
        from datetime import date

        admin = User(
            name="Admin User",
            email="admin@example.com",
            nickname="admin",
            role=Role.ADMIN,
            birth=date(1990, 1, 1),
            phone="010-1234-5678",
        )
        admin.set_password("Admin1234!")
        db.add(admin)

        # 테스트 데이터 생성
        generate_test_data(num_users=5, num_games=3)

        db.commit()
    finally:
        db.close()
