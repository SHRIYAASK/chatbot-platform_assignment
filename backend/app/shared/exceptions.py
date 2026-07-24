class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DuplicateResourceError(AppException):
    pass


class ResourceNotFoundError(AppException):
    pass


class AuthorizationError(AppException):
    pass
