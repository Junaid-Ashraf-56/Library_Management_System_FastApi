"""Business service package."""

from app.exceptions import DomainError, NotFoundError, ValidationError

LibraryError = DomainError

__all__ = ["LibraryError", "NotFoundError", "ValidationError"]
