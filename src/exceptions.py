"""
Global exception handlers and custom exception classes.
Implements exception middleware and standardized error responses.
"""
"""
Global exception handlers and custom exception classes.
Implements exception middleware and standardized error responses.
"""

from typing import Any, Dict, List, Optional, Type, Union

from fastapi import HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Error details for structured API error responses"""
    code: str
    message: str
    params: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: ErrorDetail
    data: Optional[Any] = None


# Base exception class
class MemoryAppException(Exception):
    """Base exception for all application-specific exceptions"""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"
    message: str = "An unexpected error occurred"
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        params: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.params = params or {}
        super().__init__(self.message)


# Authentication exceptions
class AuthenticationException(MemoryAppException):
    """Base class for authentication-related exceptions"""
    status_code: int = status.HTTP_401_UNAUTHORIZED
    code: str = "authentication_error"
    message: str = "Authentication failed"


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid authentication credentials"""
    code: str = "invalid_credentials"
    message: str = "Invalid username or password"


class TokenExpiredException(AuthenticationException):
    """Exception for expired authentication tokens"""
    code: str = "token_expired"
    message: str = "Authentication token has expired"


class InvalidTokenException(AuthenticationException):
    """Exception for invalid authentication tokens"""
    code: str = "invalid_token"
    message: str = "Invalid authentication token"


# Authorization exceptions
class PermissionDeniedException(MemoryAppException):
    """Exception for permission/authorization failures"""
    status_code: int = status.HTTP_403_FORBIDDEN
    code: str = "permission_denied"
    message: str = "You do not have permission to perform this action"


# Resource exceptions
class ResourceNotFoundException(MemoryAppException):
    """Exception for resources that don't exist"""
    status_code: int = status.HTTP_404_NOT_FOUND
    code: str = "not_found"
    message: str = "The requested resource was not found"


class ResourceAlreadyExistsException(MemoryAppException):
    """Exception for duplicate resources"""
    status_code: int = status.HTTP_409_CONFLICT
    code: str = "already_exists"
    message: str = "A resource with this identifier already exists"


# Validation exceptions
class ValidationException(MemoryAppException):
    """Exception for data validation errors"""
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    code: str = "validation_error"
    message: str = "Validation error"


# Age Gate exceptions
class AgeGateException(MemoryAppException):
    """Exception for age gate restriction violations"""
    status_code: int = status.HTTP_403_FORBIDDEN
    code: str = "age_gate_restricted"
    message: str = "This content is not yet available due to age gate restrictions"


# Media exceptions
class MediaProcessingException(MemoryAppException):
    """Exception for media processing errors"""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "media_processing_error"
    message: str = "Error processing media content"


class InvalidMediaTypeException(ValidationException):
    """Exception for unsupported media types"""
    code: str = "invalid_media_type"
    message: str = "This media type is not supported"


class MediaTooLargeException(ValidationException):
    """Exception for media files exceeding size limits"""
    code: str = "media_too_large"
    message: str = "Media file exceeds maximum allowed size"


# Global exception handler
async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all application exceptions"""
    if isinstance(exc, MemoryAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=exc.code,
                    message=exc.message,
                    params=exc.params
                )
            ).dict()
        )
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code=f"http_{exc.status_code}",
                    message=exc.detail
                )
            ).dict()
        )
    
    # Fallback for unexpected exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code="internal_error",
                message="An unexpected error occurred"
            )
        ).dict()
    )


# Register the exception handler with FastAPI
def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI application"""
    app.add_exception_handler(Exception, exception_handler)
    app.add_exception_handler(MemoryAppException, exception_handler)
    app.add_exception_handler(HTTPException, exception_handler)