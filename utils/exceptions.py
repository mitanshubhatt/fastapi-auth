from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseAppException(HTTPException):
    """Base exception class for all application exceptions"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        internal_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.internal_code = internal_code

class NotFoundError(BaseAppException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            internal_code=internal_code
        )

class ValidationError(BaseAppException):
    """Validation error"""
    def __init__(self, detail: str, internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            internal_code=internal_code
        )

class UnauthorizedError(BaseAppException):
    """Unauthorized access"""
    def __init__(self, detail: str = "Unauthorized access", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            internal_code=internal_code
        )

class ForbiddenError(BaseAppException):
    """Forbidden access"""
    def __init__(self, detail: str = "Access forbidden", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            internal_code=internal_code
        )

class ConflictError(BaseAppException):
    """Resource conflict"""
    def __init__(self, detail: str = "Resource conflict", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            internal_code=internal_code
        )

class DatabaseError(BaseAppException):
    """Database operation error"""
    def __init__(self, detail: str = "Database operation failed", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            internal_code=internal_code
        )

class ExternalServiceError(BaseAppException):
    """External service error"""
    def __init__(self, detail: str = "External service error", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            internal_code=internal_code
        )

class InternalServerError(BaseAppException):
    """Internal server error"""
    def __init__(self, detail: str = "Internal server error", internal_code: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            internal_code=internal_code
        ) 