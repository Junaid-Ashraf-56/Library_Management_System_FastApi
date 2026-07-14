"""Business service package."""


class LibraryError(Exception):
    pass


class NotFoundError(LibraryError):
    pass


class ValidationError(LibraryError):
    pass
