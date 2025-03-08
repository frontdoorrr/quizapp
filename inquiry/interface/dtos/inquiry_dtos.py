from pydantic import BaseModel


class InquiryBase(BaseModel):
    name: str
    email: str
    content: str


class InquiryCreateDTO(InquiryBase):
    pass


class InquiryResponseDTO(InquiryBase):
    id: str
    created_at: datetime
    content: str
    is_replied: bool
