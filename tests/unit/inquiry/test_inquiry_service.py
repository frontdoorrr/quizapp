import pytest
from datetime import datetime
from inquiry.application.inquiry_service import InquiryService
from inquiry.domain.inquiry import Inquiry, InquiryStatus, InquiryType


class TestInquiryService:
    @pytest.fixture
    def inquiry_service(self, mocker):
        self.inquiry_repo = mocker.Mock()
        return InquiryService(inquiry_repo=self.inquiry_repo)

    def test_create_inquiry(self, inquiry_service):
        # Given
        inquiry_data = {
            "user_id": "test-user-id",
            "title": "Test Inquiry",
            "content": "Test Content",
            "type": InquiryType.GENERAL,
        }

        # When
        inquiry = inquiry_service.create_inquiry(**inquiry_data)

        # Then
        assert inquiry.title == inquiry_data["title"]
        assert inquiry.status == InquiryStatus.PENDING

    def test_answer_inquiry(self, inquiry_service):
        # Given
        inquiry_id = "test-inquiry-id"
        answer = "Test Answer"
        mock_inquiry = Inquiry(
            id=inquiry_id,
            user_id="test-user-id",
            title="Test Inquiry",
            content="Test Content",
            type=InquiryType.GENERAL,
            status=InquiryStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.inquiry_repo.find_by_id.return_value = mock_inquiry

        # When
        result = inquiry_service.answer_inquiry(inquiry_id, answer)

        # Then
        assert result.status == InquiryStatus.ANSWERED
        assert result.answer == answer
