from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserPublic
from app.core.exceptions import ConflictException


class UserService:
    @staticmethod
    def get_current_user_profile(user: User) -> UserPublic:
        return UserPublic.model_validate(user)

    @staticmethod
    def update_user_profile(db: Session, user: User, payload: UserUpdate) -> UserPublic:
        update_data = payload.model_dump(exclude_unset=True)

        if "username" in update_data and update_data["username"]:
            existing = UserRepository.get_by_username(db, update_data["username"])
            if existing and existing.id != user.id:
                raise ConflictException("Username is already taken")

        updated_user = UserRepository.update(db, user, update_data)
        return UserPublic.model_validate(updated_user)
