from dataclasses import dataclass
from datetime import datetime


@dataclass
class Game:
    id: str
    number: int
    created_at: datetime
    modified_at: datetime
    opened_at: datetime
    closed_at: datetime

    title: str
    description: str
    status: str  # Choice
    memo: str | None
    question: str
    answer: str
    question_link: str | None
    answer_link: str | None
