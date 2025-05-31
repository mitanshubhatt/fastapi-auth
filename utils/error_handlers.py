from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, Dict, Any

from utils.exceptions import BaseAppException
from utils.custom_logger import logger
from utils.serializers import ResponseData

async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """
    Handle all custom application exceptions.
    Returns a consistent error response format.
    """
    response_data = ResponseData.model_construct(
        success=False,
        message=str(exc.detail),
        errors=[{
            "code": exc.internal_code or str(exc.status_code),
            "detail": exc.detail
        }]
    )
    
    logger.error(
        f"Application error: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "internal_code": exc.internal_code
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data.model_dump()
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle SQLAlchemy specific exceptions.
    Converts database errors into a consistent response format.
    """
    response_data = ResponseData.model_construct(
        success=False,
        message="Database operation failed",
        errors=[{
            "code": "DATABASE_ERROR",
            "detail": "An error occurred while processing your request"
        }]
    )
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data.model_dump()
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle any unhandled exceptions.
    Provides a safe, generic error response while logging the actual error.
    """
    response_data = ResponseData.model_construct(
        success=False,
        message="Internal server error",
        errors=[{
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred"
        }]
    )
    
    logger.error(
        f"Unhandled error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data.model_dump()
    ) 