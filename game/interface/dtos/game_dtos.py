from datetime import datetime
from pydantic import BaseModel, Field


class GameBase(BaseModel):
    pass
    # title: str = Field(min_length=2, max_length=32)
    # number: int = Field(gt=0)
    # description: str = Field(max_length=64)
    # question: str = Field(max_length=64)
    # answer: str = Field(max_length=64)
    # question_link: str = Field(max_length=128)
    # answer_link: str = Field(max_length=128)


class GameCreateDTO(GameBase):
    title: str = Field(min_length=2, max_length=32)
    number: int = Field(gt=0)
    description: str = Field(max_length=64)
    question: str = Field(max_length=64)
    answer: str = Field(max_length=64)
    question_link: str = Field(max_length=128)
    answer_link: str = Field(max_length=128)


class GameUpdateDTO(GameBase):
    title: str = Field(min_length=2, max_length=32)
    description: str = Field(max_length=64)
    question: str = Field(max_length=64)
    answer: str = Field(max_length=64)
    question_link: str = Field(max_length=128)
    answer_link: str = Field(max_length=128)
    status: str = Field(max_length=16)


class GameResponseDTO(GameBase):
    id: str
    number: int
    created_at: datetime
    modified_at: datetime
    opened_at: datetime | None
    closed_at: datetime | None
    title: str
    description: str
    status: str
    memo: str | None
    question: str
    # answer: str | None
    question_link: str | None
    # answer_link: str | None
