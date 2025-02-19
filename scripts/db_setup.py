import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine, SessionLocal
from models import Base

def setup_database():
    """데이터베이스 테이블 생성 및 초기 설정"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 데이터베이스 연결 테스트
        db.execute(text("SELECT 1"))
        print("Database connection successful!")
        
        # 여기에 초기 데이터 삽입 로직 추가 가능
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
