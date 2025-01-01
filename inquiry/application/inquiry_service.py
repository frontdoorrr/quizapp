from datetime import datetime
from ulid import ULID

from dependency_injector.wiring import inject

from inquiry.domain.inquiry import Inquiry
from inquiry.domain.repository.inquiry_repo import IInquiryRepository


class InquiryService:
    @inject
    def __init__(self, inquiry_repo: IInquiryRepository):
        self.inquiry_repo = inquiry_repo
        self.ulid = ULID()

    def create_inquiry(
        self,
        name: str,
        email: str,
        content: str,
    ):
        inquiry = Inquiry(
            id=self.ulid.generate(),
            name=name,
            email=email,
            content=content,
            is_replied=False,
            created_at=datetime.now(),
        )
        self.inquiry_repo.save(inquiry)
        return inquiry

    def update_inquiry(
        self,
        id: str,
        name: str | None,
        email: str | None,
        content: str | None,
    ):
        inquiry = self.inquiry_repo.find_by_id(id)
        if name:
            inquiry.name = name
        if email:
            inquiry.email = email
        if content:
            inquiry.content = content

        inquiry = self.inquiry_repo.update(inquiry)
        return inquiry

    def get_inquiries(self):
        return self.inquiry_repo.find_all()
