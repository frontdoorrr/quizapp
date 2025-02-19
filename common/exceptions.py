from typing import Any, Dict, Optional

class QuizAppException(Exception):
    """Base exception for QuizApp"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

class NotFoundError(QuizAppException):
    """리소스를 찾을 수 없을 때 발생하는 예외"""
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=404, detail=detail)

class ValidationError(QuizAppException):
    """입력값 검증 실패시 발생하는 예외"""
    def __init__(
        self,
        message: str = "Validation failed",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=400, detail=detail)

class AuthenticationError(QuizAppException):
    """인증 실패시 발생하는 예외"""
    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=401, detail=detail)

class AuthorizationError(QuizAppException):
    """권한이 없을 때 발생하는 예외"""
    def __init__(
        self,
        message: str = "Permission denied",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=403, detail=detail)

class BusinessLogicError(QuizAppException):
    """비즈니스 로직 처리 중 발생하는 예외"""
    def __init__(
        self,
        message: str = "Business logic error",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=400, detail=detail)

class ExternalServiceError(QuizAppException):
    """외부 서비스 호출 실패시 발생하는 예외"""
    def __init__(
        self,
        message: str = "External service error",
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=502, detail=detail)
