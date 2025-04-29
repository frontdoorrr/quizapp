#!/usr/bin/env python3
import sys
import os
import uuid
from datetime import datetime, timedelta
import random
import pytz
import json

# 현재 스크립트 경로를 기준으로 프로젝트 루트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 필요한 모듈 임포트
from containers import Container
from game.application.game_service import GameService
from game.domain.game import GameStatus
from database import Base, engine

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 퀴즈 샘플 데이터
SAMPLE_QUIZZES = [
    {
        "title": "첫 번째 퀴즈",
        "description": "간단한 프로그래밍 문제",
        "question": "파이썬에서 리스트를 정렬하는 메소드는?",
        "answer": "sort",
        "question_link": "https://example.com/question1",
        "answer_link": "https://example.com/answer1"
    },
    {
        "title": "두 번째 퀴즈",
        "description": "알고리즘 문제",
        "question": "O(n log n) 시간 복잡도를 가진 정렬 알고리즘은?",
        "answer": "퀵소트",
        "question_link": "https://example.com/question2",
        "answer_link": "https://example.com/answer2"
    },
    {
        "title": "세 번째 퀴즈",
        "description": "데이터베이스 문제",
        "question": "SQL에서 데이터를 선택하는 명령어는?",
        "answer": "SELECT",
        "question_link": "https://example.com/question3",
        "answer_link": "https://example.com/answer3"
    },
    {
        "title": "네 번째 퀴즈",
        "description": "웹 개발 문제",
        "question": "HTML에서 링크를 만드는 태그는?",
        "answer": "a",
        "question_link": "https://example.com/question4",
        "answer_link": "https://example.com/answer4"
    },
    {
        "title": "다섯 번째 퀴즈",
        "description": "네트워크 문제",
        "question": "HTTP의 기본 포트 번호는?",
        "answer": "80",
        "question_link": "https://example.com/question5",
        "answer_link": "https://example.com/answer5"
    },
    {
        "title": "여섯 번째 퀴즈",
        "description": "운영체제 문제",
        "question": "리눅스에서 파일 권한을 변경하는 명령어는?",
        "answer": "chmod",
        "question_link": "https://example.com/question6",
        "answer_link": "https://example.com/answer6"
    },
    {
        "title": "일곱 번째 퀴즈",
        "description": "자료구조 문제",
        "question": "LIFO 원칙을 따르는 자료구조는?",
        "answer": "스택",
        "question_link": "https://example.com/question7",
        "answer_link": "https://example.com/answer7"
    },
    {
        "title": "여덟 번째 퀴즈",
        "description": "보안 문제",
        "question": "대칭키 암호화 알고리즘의 예는?",
        "answer": "AES",
        "question_link": "https://example.com/question8",
        "answer_link": "https://example.com/answer8"
    },
    {
        "title": "아홉 번째 퀴즈",
        "description": "프론트엔드 문제",
        "question": "자바스크립트에서 비동기 처리를 위한 객체는?",
        "answer": "Promise",
        "question_link": "https://example.com/question9",
        "answer_link": "https://example.com/answer9"
    },
    {
        "title": "열 번째 퀴즈",
        "description": "백엔드 문제",
        "question": "REST API에서 리소스 생성에 사용되는 HTTP 메소드는?",
        "answer": "POST",
        "question_link": "https://example.com/question10",
        "answer_link": "https://example.com/answer10"
    }
]

def generate_dummy_games(num_games=10):
    """
    더미 게임 데이터를 생성합니다.
    
    Args:
        num_games (int): 생성할 게임 수
    """
    # 컨테이너 초기화
    container = Container()
    container.init_resources()
    
    # 게임 서비스 가져오기
    game_service = container.game_service()
    
    # 생성된 게임 저장
    created_games = []
    
    # 현재 시간 (한국 시간)
    now = datetime.now(KST)
    
    # 게임 생성
    for i in range(num_games):
        # 퀴즈 데이터 선택 (샘플이 부족하면 반복)
        quiz_data = SAMPLE_QUIZZES[i % len(SAMPLE_QUIZZES)]
        
        # 게임 번호
        number = i + 1
        
        # 게임 상태 랜덤 선택 (DRAFT, OPEN, CLOSED)
        status_choices = [GameStatus.DRAFT, GameStatus.OPEN, GameStatus.CLOSED]
        status_weights = [0.2, 0.5, 0.3]  # 20% 초안, 50% 열림, 30% 닫힘
        status = random.choices(status_choices, weights=status_weights, k=1)[0]
        
        # 게임 생성 시간 (최근 60일 내 랜덤)
        created_at = now - timedelta(days=random.randint(0, 60), 
                                   hours=random.randint(0, 23), 
                                   minutes=random.randint(0, 59))
        
        # 게임 오픈 시간 (OPEN, CLOSED 상태인 경우만)
        opened_at = None
        if status in [GameStatus.OPEN, GameStatus.CLOSED]:
            opened_at = created_at + timedelta(days=random.randint(1, 5))
        
        # 게임 종료 시간 (CLOSED 상태인 경우만)
        closed_at = None
        if status == GameStatus.CLOSED:
            closed_at = opened_at + timedelta(days=random.randint(1, 7))
        
        try:
            # 게임 생성
            game = game_service.create_game(
                title=f"{quiz_data['title']} #{number}",
                number=number,
                description=quiz_data['description'],
                question=quiz_data['question'],
                answer=quiz_data['answer'],
                question_link=quiz_data['question_link'],
                answer_link=quiz_data['answer_link'],
            )
            
            # 게임 상태 업데이트
            if status != GameStatus.DRAFT:
                game = game_service.update_game(
                    id=game.id,
                    status=status.value,
                    opened_at=opened_at,
                    closed_at=closed_at
                )
            
            created_games.append({
                "id": game.id,
                "number": game.number,
                "title": game.title,
                "description": game.description,
                "question": game.question,
                "answer": game.answer,
                "status": game.status.value if hasattr(game.status, 'value') else game.status,
                "created_at": str(game.created_at),
                "opened_at": str(game.opened_at) if game.opened_at else None,
                "closed_at": str(game.closed_at) if game.closed_at else None
            })
            
            print(f"게임 생성 완료: {game.title} (상태: {game.status})")
            
        except Exception as e:
            print(f"게임 생성 실패: {e}")
    
    # 생성된 게임 저장
    if created_games:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_games.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(created_games, f, ensure_ascii=False, indent=2)
        print(f"생성된 게임 데이터가 {output_file}에 저장되었습니다.")
    
    print(f"총 {len(created_games)}개의 더미 게임이 생성되었습니다.")

if __name__ == "__main__":
    # 데이터베이스 초기화
    Base.metadata.create_all(engine)
    
    # 인자로 생성할 게임 수 받기 (기본값: 10)
    num_games = 10
    if len(sys.argv) > 1:
        try:
            num_games = int(sys.argv[1])
        except ValueError:
            print(f"유효하지 않은 숫자입니다: {sys.argv[1]}")
            sys.exit(1)
    
    # 더미 게임 생성
    generate_dummy_games(num_games)
