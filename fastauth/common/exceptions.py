class FastAuthException(Exception):
    """Base exception for FastAuth."""

    pass


# Database exceptions


class DatabaseException(FastAuthException):
    """Base exception for database operations."""

    pass


class NotUniqueException(DatabaseException):
    """Exception raised when we expect a unique result from database but we get multiple."""

    pass


class NotFoundException(DatabaseException):
    """Exception raised when we expect a result from database but we get nothing."""

    pass
