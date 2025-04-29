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
from answer.application.answer_service import AnswerService
from game.application.game_service import GameService
from user.application.user_service import UserService
from database import Base, engine
from answer.domain.answer import AnswerStatus, Answer

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def generate_dummy_answers(num_answers=50):
    """
    더미 답변 데이터를 생성합니다.
    
    Args:
        num_answers (int): 생성할 답변 수
    """
    # 컨테이너 초기화
    container = Container()
    container.init_resources()
    
    # 서비스 가져오기
    answer_service = container.answer_service()
    game_service = container.game_service()
    user_service = container.user_service()
    
    # 게임 목록 가져오기
    games = game_service.get_games()
    if not games:
        print("게임이 없습니다. 먼저 게임을 생성해주세요.")
        return
    
    # 사용자 목록 가져오기
    users = user_service.get_users()
    if not users:
        print("사용자가 없습니다. 먼저 사용자를 생성해주세요.")
        return
    
    # 생성된 답변 저장
    created_answers = []
    
    # 답변 생성
    for _ in range(num_answers):
        # 랜덤 게임 선택
        game = random.choice(games)
        
        # 랜덤 사용자 선택
        user = random.choice(users)
        
        # 랜덤 답변 생성
        is_correct = random.choice([True, False])
        
        # 정답인 경우 게임 정답 사용, 아닌 경우 랜덤 텍스트
        answer_text = game.answer if is_correct else f"오답_{uuid.uuid4().hex[:8]}"
        
        # 생성 시간 (최근 30일 내 랜덤)
        now = datetime.now(KST)
        created_at = now - timedelta(days=random.randint(0, 30), 
                                   hours=random.randint(0, 23), 
                                   minutes=random.randint(0, 59))
        
        # 해결 시간 (정답인 경우만)
        solved_at = created_at if is_correct else None
        
        # 포인트 (정답인 경우 1-100 랜덤, 오답은 0)
        point = random.randint(1, 100) if is_correct else 0
        
        try:
            # 새 답변 생성
            answer = answer_service.create_answer(
                game_id=game.id,
                user_id=user.id,
                answer_text=answer_text
            )
            
            # 답변 업데이트를 위한 새 객체 생성
            updated_answer = Answer(
                id=answer.id,
                game_id=game.id,
                user_id=user.id,
                answer=answer_text,
                is_correct=is_correct,
                solved_at=solved_at,
                created_at=created_at,
                updated_at=created_at,
                point=point,
                status=AnswerStatus.SUBMITTED if is_correct else AnswerStatus.NOT_USED
            )
            
            # 답변 업데이트
            answer = answer_service.update_answer(answer.id, updated_answer)
            
            created_answers.append({
                "id": answer.id,
                "game_id": answer.game_id,
                "user_id": answer.user_id,
                "answer": answer.answer,
                "is_correct": answer.is_correct,
                "solved_at": str(answer.solved_at) if answer.solved_at else None,
                "created_at": str(answer.created_at),
                "point": answer.point
            })
            
            print(f"답변 생성 완료: {answer.id} (게임: {game.title}, 사용자: {user.name}, 정답여부: {is_correct})")
            
        except Exception as e:
            print(f"답변 생성 실패: {e}")
    
    # 생성된 답변 저장
    if created_answers:
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dummy_answers.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(created_answers, f, ensure_ascii=False, indent=2)
        print(f"생성된 답변 데이터가 {output_file}에 저장되었습니다.")
    
    print(f"총 {len(created_answers)}개의 더미 답변이 생성되었습니다.")

if __name__ == "__main__":
    # 데이터베이스 초기화
    Base.metadata.create_all(engine)
    
    # 인자로 생성할 답변 수 받기 (기본값: 50)
    num_answers = 50
    if len(sys.argv) > 1:
        try:
            num_answers = int(sys.argv[1])
        except ValueError:
            print(f"유효하지 않은 숫자입니다: {sys.argv[1]}")
            sys.exit(1)
    
    # 더미 답변 생성
    generate_dummy_answers(num_answers)
