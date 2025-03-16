from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from user.interface.dtos.user_dto import UserResponseDTO


class AnswerBase(BaseModel):
    id: str
    game_id: str
    user_id: str
    answer: str
    is_correct: bool
    solved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    point: int


class AnswerRequestDTO(BaseModel):
    game_id: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class AnswerResponseDTO(AnswerBase):
    user: UserResponseDTO | None = None


class AnswerResponseListDTO(BaseModel):
    total_count: int
    answers: List[AnswerResponseDTO]
