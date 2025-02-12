from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AnswerStatus(str, Enum):
    NOT_USED = "not_used"
    SUBMITTED = "submitted"


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
    status: AnswerStatus
