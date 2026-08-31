from fastapi import HTTPException, status


class HabitForgeException(Exception):
    """Base exception for all HabitForge business logic errors."""
    pass


class NotFoundException(HTTPException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found",
        )


class ForbiddenException(HTTPException):
    def __init__(self, message: str = "You do not have permission to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
        )


class ConflictException(HTTPException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )


class BadRequestException(HTTPException):
    def __init__(self, message: str = "Invalid request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Domain-specific exceptions ────────────────────────────────────────────────

class UserNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("User")


class HabitNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Habit")


class GoalNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Goal")


class HabitAlreadyCompletedException(ConflictException):
    def __init__(self):
        super().__init__("Habit already completed for this date")


class HabitLimitExceededException(ForbiddenException):
    def __init__(self, limit: int):
        super().__init__(
            f"Free plan allows a maximum of {limit} active habits. "
            "Upgrade to Pro for unlimited habits."
        )


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid email or password")


class EmailAlreadyExistsException(ConflictException):
    def __init__(self):
        super().__init__("An account with this email already exists")

