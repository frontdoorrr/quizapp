from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GameStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


@dataclass
class Game:
    id: str
    number: int
    created_at: datetime
    modified_at: datetime
    opened_at: datetime | None
    closed_at: datetime | None
    title: str
    description: str | None
    status: GameStatus
    memo: str | None
    question: str
    answer: str
    question_link: str | None
    answer_link: str | None
