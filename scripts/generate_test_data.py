import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from user.infra.db_models.user import User
from game.infra.db_models.game import Game
from answer.infra.db_models.answer import Answer
import random
from datetime import datetime, timedelta, date
import uuid


def generate_test_data(num_users: int = 10, num_games: int = 5):
    """테스트용 데이터 생성"""
    db = SessionLocal()
    try:
        # 테스트 유저 생성
        print(f"Creating {num_users} test users...")
        users = []
        for i in range(num_users):
            user = User(
                name=f"Test User {i}",
                email=f"test_user_{i}@example.com",
                password="testpassword123",
                nickname=f"TestUser{i}",
                birth=date(
                    1990 + random.randint(0, 20),
                    random.randint(1, 12),
                    random.randint(1, 28),
                ),
                phone=f"010{random.randint(10000000, 99999999)}",
                address=f"Test Address {i}",
                email_verified=True,
            )
            user.set_password("testpassword123")
            db.add(user)
            users.append(user)

        # 테스트 게임 생성
        print(f"Creating {num_games} test games...")
        games = []
        for i in range(num_games):
            game = Game(
                id=str(uuid.uuid4()),
                title=f"Test Game {i}",
                description=f"This is test game number {i}",
                difficulty=random.choice(["EASY", "MEDIUM", "HARD"]),
                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                updated_at=datetime.now(),
            )
            db.add(game)
            games.append(game)

        # 테스트 답변 생성
        print("Creating test answers...")
        for user in users:
            for game in games:
                if random.random() < 0.7:  # 70% 확률로 답변 생성
                    answer = Answer(
                        id=str(uuid.uuid4()),
                        user_id=user.id,
                        game_id=game.id,
                        content=f"Test answer from {user.nickname} for game {game.title}",
                        score=random.randint(0, 100),
                        created_at=datetime.now()
                        - timedelta(days=random.randint(0, 30)),
                        updated_at=datetime.now(),
                    )
                    db.add(answer)

        db.commit()
        print("Test data generated successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error generating test data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test data")
    parser.add_argument(
        "--users", type=int, default=10, help="Number of test users to create"
    )
    parser.add_argument(
        "--games", type=int, default=5, help="Number of test games to create"
    )

    args = parser.parse_args()
    generate_test_data(args.users, args.games)
