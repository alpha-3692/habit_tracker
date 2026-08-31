from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.subscription import Subscription


class SubscriptionRepository:
    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        return db.scalars(stmt).first()

    @staticmethod
    def create_default_free_subscription(db: Session, user_id: UUID) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            tier="free",
            status="active",
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription
