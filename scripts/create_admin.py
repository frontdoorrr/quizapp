import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from user.infra.db_models.user import User
from user.domain.user import UserRole
import argparse

def create_admin_user(email: str, password: str):
    """관리자 계정 생성"""
    db = SessionLocal()
    try:
        # 이미 존재하는 이메일인지 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists")
            return

        # 새 관리자 계정 생성
        admin_user = User(
            email=email,
            role=UserRole.ADMIN
        )
        admin_user.set_password(password)
        
        db.add(admin_user)
        db.commit()
        print(f"Admin user created successfully: {email}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True, help="Admin user email")
    parser.add_argument("--password", required=True, help="Admin user password")
    
    args = parser.parse_args()
    create_admin_user(args.email, args.password)
