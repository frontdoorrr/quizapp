import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
import os
import logging

from database import Base, get_db
from main import app
from scripts.generate_test_data import generate_test_data

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트 데이터베이스 URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@db:5432/testdb"
)

logger.info(f"테스트 데이터베이스 URL: {TEST_DATABASE_URL}")


@pytest.fixture(scope="session")
def test_engine():
    """테스트 데이터베이스 엔진 생성"""
    logger.info("테스트 엔진 생성 시작")
    engine = create_engine(TEST_DATABASE_URL)

    # 테스트 DB가 존재하면 삭제
    if database_exists(engine.url):
        logger.info("기존 테스트 DB 삭제")
        drop_database(engine.url)

    # 테스트 DB 생성
    logger.info("새 테스트 DB 생성")
    create_database(engine.url)

    # 테이블 생성
    logger.info("테이블 생성")
    Base.metadata.create_all(bind=engine)

    yield engine

    # 테스트 종료 후 DB 삭제 (주석 처리하여 DB 유지)
    # logger.info("테스트 종료 후 DB 삭제")
    # drop_database(engine.url)


@pytest.fixture(scope="session")
def test_db(test_engine):
    """테스트 데이터베이스 세션 생성"""
    logger.info("테스트 DB 세션 생성")
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    return TestingSessionLocal


@pytest.fixture(scope="function")
def db_session(test_db):
    """각 테스트 함수에서 사용할 데이터베이스 세션"""
    logger.info("테스트 함수용 DB 세션 생성")
    db = test_db()
    
    # 모든 테이블의 데이터 삭제
    logger.info("모든 테이블 데이터 삭제")
    connection = db.connection()
    
    try:
        # 외래 키 제약 조건 비활성화
        connection.execute(text("SET session_replication_role = 'replica';"))
        
        # 모든 테이블 비우기
        for table in reversed(Base.metadata.sorted_tables):
            logger.info(f"테이블 비우기: {table.name}")
            # PostgreSQL에서 'user'는 예약어이므로 따옴표로 묶어서 사용
            table_name = f'"{table.name}"' if table.name == 'user' else table.name
            connection.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;"))
        
        # 외래 키 제약 조건 다시 활성화
        connection.execute(text("SET session_replication_role = 'origin';"))
        
        db.commit()
        logger.info("모든 테이블 초기화 완료")
    except Exception as e:
        logger.error(f"테이블 초기화 중 오류 발생: {e}")
        db.rollback()
        raise e
    
    try:
        yield db
    finally:
        logger.info("DB 세션 롤백 및 종료")
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(db_session, test_data):
    """테스트 클라이언트"""
    logger.info("테스트 클라이언트 생성")

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 의존성 재설정
    logger.info("테스트 클라이언트 의존성 재설정")
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_data(db_session):
    """테스트 데이터 생성"""
    logger.info("테스트 데이터 생성 시작")
    try:
        # 관리자 계정 생성
        from user.infra.db_models.user import User
        from user.domain.user import Role
        from datetime import date, datetime
        import uuid
        from passlib.context import CryptContext
        from sqlalchemy import text

        # 먼저 관리자 계정이 이미 존재하는지 확인
        admin_exists = db_session.execute(
            text("SELECT * FROM \"user\" WHERE email = 'admin@example.com'")
        ).fetchone()

        if not admin_exists:
            # 비밀번호 해싱
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password = "Admin1234!"
            hashed_password = pwd_context.hash(password)

            admin = User(
                id=str(uuid.uuid4()),
                name="Admin User",
                email="admin@example.com",
                nickname="admin",
                role=Role.ADMIN,
                birth=date(1990, 1, 1),
                phone="010-1234-5678",
                password=hashed_password,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db_session.add(admin)
            db_session.commit()  # 명시적으로 커밋하여 관리자 계정이 저장되도록 함
            print("관리자 계정이 생성되었습니다.")
        else:
            print("관리자 계정이 이미 존재합니다.")
        
        # 여기서 추가 테스트 데이터를 생성할 수 있습니다
        # generate_test_data 함수는 직접 DB 세션을 생성하므로 주석 처리
        # generate_test_data(num_users=5, num_games=3)
    except Exception as e:
        logger.error(f"테스트 데이터 생성 중 오류: {e}")
        db_session.rollback()
        raise e
    
    return db_session
