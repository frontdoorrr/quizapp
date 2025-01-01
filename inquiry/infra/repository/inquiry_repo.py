from database import SessionLocal
from inquiry.domain.repository.inquiry_repo import IInquiryRepository
from inquiry.domain.inquiry import Inquiry as InquiryVO
from inquiry.infra.db_models.inquiry import Inquiry


class InquiryRepository(IInquiryRepository):
    def save(self, inquiry: InquiryVO):
        inquiry = Inquiry(
            id=inquiry.id,
            name=inquiry.name,
            email=inquiry.email,
            content=inquiry.content,
            is_replied=inquiry.is_replied,
            created_at=inquiry.created_at,
        )
        with SessionLocal() as db:
            db.add(inquiry)
            db.commit()
            db.refresh(inquiry)
            inquiry.id = inquiry.id

    def find_all(self) -> list[InquiryVO]:
        with SessionLocal() as db:
            inquiries = db.query(Inquiry).all()
            return [
                InquiryVO(
                    id=inquiry.id,
                    name=inquiry.name,
                    email=inquiry.email,
                    content=inquiry.content,
                    is_replied=inquiry.is_replied,
                    created_at=inquiry.created_at,
                )
                for inquiry in inquiries
            ]

    def find_by_id(self, id: str) -> InquiryVO:
        with SessionLocal() as db:
            inquiry = db.query(Inquiry).filter(Inquiry.id == id).first()
            if not inquiry:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
            return InquiryVO(
                id=inquiry.id,
                name=inquiry.name,
                email=inquiry.email,
                content=inquiry.content,
                is_replied=inquiry.is_replied,
                created_at=inquiry.created_at,
            )
