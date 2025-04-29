#!/usr/bin/env python3
import sys
import os
import uuid
from datetime import datetime, date, timedelta
import random
import pytz
import json
import string

# 현재 스크립트 경로를 기준으로 프로젝트 루트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 필요한 모듈 임포트
from containers import Container
from user.application.user_service import UserService
from user.domain.user import Role
from database import Base, engine

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 한국 이름 샘플
FIRST_NAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "전", "홍"]
LAST_NAMES = ["민준", "서준", "예준", "도윤", "시우", "주원", "하준", "지호", "준서", "준우", "지훈", "도현", "건우", "현우", "민재", "현준", "선우", "서진", "연우", "은우",
              "서연", "서윤", "지우", "서현", "하은", "하윤", "민서", "지유", "윤서", "지민", "채원", "수아", "지아", "지윤", "은서", "다은", "예은", "수빈", "지은", "소율"]

# 닉네임 접두사/접미사
NICKNAME_PREFIXES = ["멋진", "귀여운", "똑똑한", "재미있는", "행복한", "신나는", "열정적인", "활기찬", "창의적인", "친절한"]
NICKNAME_SUFFIXES = ["개발자", "프로그래머", "코더", "엔지니어", "디자이너", "학생", "선생님", "마스터", "고수", "팬"]

def generate_random_password():
    """안전한 랜덤 비밀번호 생성"""
    # 최소 8자, 최대 16자
    length = random.randint(8, 16)
    
    # 최소 1개의 대문자, 1개의 소문자, 1개의 숫자, 1개의 특수문자 포함
    uppercase = random.choice(string.ascii_uppercase)
    lowercase = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice('!@#$%^&*(),.?":{}|<>')
    
    # 나머지 문자 랜덤 생성
    remaining_length = length - 4
    remaining_chars = ''.join(random.choices(
        string.ascii_letters + string.digits + '!@#$%^&*(),.?":{}|<>',
        k=remaining_length
    ))
    
    # 모든 문자 조합 후 섞기
    all_chars = uppercase + lowercase + digit + special + remaining_chars
    password_chars = list(all_chars)
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

def generate_dummy_users(num_users=20):
    """
    더미 사용자 데이터를 생성합니다.
    
    Args:
        num_users (int): 생성할 사용자 수
    """
    # 컨테이너 초기화
    container = Container()
    container.init_resources()
    
    # 사용자 서비스 가져오기
    user_service = container.user_service()
    
    # 생성된 사용자 저장
    created_users = []
    
    # 현재 시간 (한국 시간)
    now = datetime.now(KST)
    
    # 관리자 계정 생성
    try:
        admin_password = generate_random_password()
        admin = user_service.create_user(
            name="관리자",
            email="admin@example.com",
            password=admin_password,
            role=Role.ADMIN,
            birth=date(1990, 1, 1),
            address="서울시 강남구",
            phone="010-1234-5678",
            nickname="시스템관리자"
        )
        
        created_users.append({
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "password": admin_password,  # 실제 환경에서는 저장하지 않음
            "role": admin.role.value if hasattr(admin.role, 'value') else admin.role,
            "nickname": admin.nickname
        })
        
        print(f"관리자 계정 생성 완료: {admin.email} (비밀번호: {admin_password})")
    except Exception as e:
        print(f"관리자 계정 생성 실패: {e}")
    
    # 일반 사용자 생성
    for i in range(num_users):
        # 랜덤 이름 생성
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = first_name + last_name
        
        # 랜덤 닉네임 생성
        nickname = f"{random.choice(NICKNAME_PREFIXES)}{random.choice(NICKNAME_SUFFIXES)}{random.randint(1, 999)}"
        
        # 랜덤 이메일 생성
        email_domains = ["gmail.com", "naver.com", "daum.net", "kakao.com", "outlook.com"]
        email = f"user{i+1}_{uuid.uuid4().hex[:6]}@{random.choice(email_domains)}"
        
        # 랜덤 비밀번호 생성
        password = generate_random_password()
        
        # 랜덤 생년월일 생성 (20~40세)
        years_ago = random.randint(20, 40)
        birth_date = date.today() - timedelta(days=365 * years_ago + random.randint(0, 364))
        
        # 랜덤 주소 생성
        cities = ["서울시", "부산시", "인천시", "대구시", "대전시", "광주시", "울산시", "세종시"]
        districts = ["강남구", "서초구", "마포구", "송파구", "중구", "동구", "서구", "남구", "북구", "해운대구"]
        address = f"{random.choice(cities)} {random.choice(districts)}"
        
        # 랜덤 전화번호 생성
        phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        try:
            # 사용자 생성
            user = user_service.create_user(
                name=full_name,
                email=email,
                password=password,
                role=Role.USER,
                birth=birth_date,
                address=address,
                phone=phone,
                nickname=nickname
            )
            
            created_users.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "password": password,  # 실제 환경에서는 저장하지 않음
                "role": user.role.value if hasattr(user.role, 'value') else user.role,
                "nickname": user.nickname
            })
            
            print(f"사용자 생성 완료: {user.email}")
            
        except Exception as e:
            print(f"사용자 생성 실패: {e}")
    
    # 생성된 사용자 저장
    if created_users:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_users.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(created_users, f, ensure_ascii=False, indent=2)
        print(f"생성된 사용자 데이터가 {output_file}에 저장되었습니다.")
    
    print(f"총 {len(created_users)}명의 더미 사용자가 생성되었습니다.")

if __name__ == "__main__":
    # 데이터베이스 초기화
    Base.metadata.create_all(engine)
    
    # 인자로 생성할 사용자 수 받기 (기본값: 20)
    num_users = 20
    if len(sys.argv) > 1:
        try:
            num_users = int(sys.argv[1])
        except ValueError:
            print(f"유효하지 않은 숫자입니다: {sys.argv[1]}")
            sys.exit(1)
    
    # 더미 사용자 생성
    generate_dummy_users(num_users)
