from uuid import UUID
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    UnauthorizedException,
    ForbiddenException,
)
from app.repositories.user_repository import UserRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    TokenResponse,
    UserPublic,
)


class AuthService:
    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> AuthResponse:
        existing_user = UserRepository.get_by_email(db, payload.email)
        if existing_user:
            raise EmailAlreadyExistsException()

        hashed_pw = hash_password(payload.password)
        user = UserRepository.create(
            db=db,
            email=payload.email,
            hashed_password=hashed_pw,
            full_name=payload.full_name,
            timezone_str=payload.timezone,
        )

        SubscriptionRepository.create_default_free_subscription(db, user.id)

        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserPublic.model_validate(user),
        )

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> AuthResponse:
        user = UserRepository.get_by_email(db, payload.email)
        if not user:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise ForbiddenException("Account is deactivated")

        if not user.hashed_password or not verify_password(payload.password, user.hashed_password):
            raise InvalidCredentialsException()

        UserRepository.update_last_login(db, user)

        user_id_str = str(user.id)
        access_token = create_access_token(user_id_str)
        refresh_token = create_refresh_token(user_id_str)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserPublic.model_validate(user),
        )

    @staticmethod
    def refresh_token(db: Session, refresh_token_str: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token_str)
            token_type = payload.get("type")
            user_id_str = payload.get("sub")

            if not user_id_str or token_type != "refresh":
                raise UnauthorizedException("Invalid refresh token")
        except JWTError:
            raise UnauthorizedException("Invalid or expired refresh token")

        user = UserRepository.get_by_id(db, UUID(user_id_str))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        new_access_token = create_access_token(str(user.id))
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
        )
