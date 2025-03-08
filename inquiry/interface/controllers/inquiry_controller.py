from datetime import datetime

from fastapi import APIRouter, Depends


from dependency_injector.wiring import inject, Provide

from containers import Container
from inquiry.application.inquiry_service import InquiryService
from inquiry.interface.dtos.inquiry_dtos import InquiryCreateDTO, InquiryResponseDTO

router = APIRouter(prefix="/inquiry", tags=["inquiry"])


@router.post("", status_code=201, response_model=InquiryResponseDTO)
@inject
async def create_inquiry(
    body: InquiryCreateDTO,
    inquiry_service: InquiryService = Depends(Provide[Container.inquiry_service]),
) -> InquiryResponseDTO:
    inquiry = inquiry_service.create_inquiry(
        name=body.name,
        email=body.email,
        content=body.content,
    )
    return InquiryResponseDTO(
        id=inquiry.id,
        name=inquiry.name,
        email=inquiry.email,
        content=inquiry.content,
        is_replied=inquiry.is_replied,
        created_at=inquiry.created_at,
    )


@router.get("", response_model=list[InquiryResponseDTO])
@inject
async def find_all_inquiry(
    inquiry_service: InquiryService = Depends(Provide[Container.inquiry_service]),
) -> list[InquiryResponseDTO]:
    inquiries = inquiry_service.get_inquiries()
    return [
        InquiryResponseDTO(
            id=inquiry.id,
            name=inquiry.name,
            email=inquiry.email,
            content=inquiry.content,
            is_replied=inquiry.is_replied,
            created_at=inquiry.created_at,
        )
        for inquiry in inquiries
    ]


@router.patch("/{inquiry_id}", status_code=200, response_model=InquiryResponseDTO)
@inject
async def update_inquiry(
    inquiry_id: str,
    body: InquiryCreateDTO,
    inquiry_service: InquiryService = Depends(Provide[Container.inquiry_service]),
) -> InquiryResponseDTO:
    inquiry = inquiry_service.update_inquiry(
        id=inquiry_id,
        name=body.name,
        email=body.email,
        content=body.content,
    )
    return InquiryResponseDTO(
        id=inquiry.id,
        name=inquiry.name,
        email=inquiry.email,
        content=inquiry.content,
        is_replied=inquiry.is_replied,
        created_at=inquiry.created_at,
    )


@router.delete("/{inquiry_id}", status_code=204)
@inject
async def delete_inquiry(
    inquiry_id: str,
    inquiry_service: InquiryService = Depends(Provide[Container.inquiry_service]),
) -> None:
    inquiry_service.delete_inquiry(id=inquiry_id)
    return None
