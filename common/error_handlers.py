from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

from common.exceptions import QuizAppException

logger = logging.getLogger(__name__)

async def quiz_app_exception_handler(request: Request, exc: QuizAppException):
    """QuizApp 커스텀 예외 핸들러"""
    logger.error(
        f"QuizApp error occurred",
        extra={
            "error_type": exc.__class__.__name__,
            "error_message": exc.message,
            "error_detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "detail": exc.detail
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """입력값 검증 실패 예외 핸들러"""
    logger.error(
        f"Validation error",
        extra={
            "error_type": "ValidationError",
            "error_detail": exc.errors(),
            "body": await request.body(),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "detail": exc.errors()
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """데이터베이스 예외 핸들러"""
    logger.error(
        f"Database error",
        extra={
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": {"db_error": str(exc)}
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    """처리되지 않은 예외 핸들러"""
    logger.error(
        f"Unhandled error",
        extra={
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "path": request.url.path
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": {"error": str(exc)}
        }
    )
