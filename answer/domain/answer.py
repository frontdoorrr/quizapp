from datatclasses import dataclass


@dataclass
class Answer:
    id: str
    game_id: str
    user_id: str

    answer: str
    is_correct: bool
    solved_at: datetime
    created_at: datetime
    updated_at: datetime
    point: int
