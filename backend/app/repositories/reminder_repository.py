import uuid
from datetime import time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload

from app.models.reminder import Reminder
from app.models.habit import Habit


class ReminderRepository:
    @staticmethod
    def create(
        db: Session,
        user_id: uuid.UUID,
        habit_id: uuid.UUID,
        reminder_time: time,
        days_of_week: Optional[List[int]] = None,
        is_active: bool = True,
    ) -> Reminder:
        """Create and persist a new reminder."""
        reminder = Reminder(
            id=uuid.uuid4(),
            user_id=user_id,
            habit_id=habit_id,
            reminder_time=reminder_time,
            days_of_week=days_of_week,
            is_active=is_active,
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def get_by_id(db: Session, reminder_id: uuid.UUID) -> Optional[Reminder]:
        """Fetch reminder by ID with joined habit."""
        return (
            db.query(Reminder)
            .options(joinedload(Reminder.habit))
            .filter(Reminder.id == reminder_id)
            .first()
        )

    @staticmethod
    def get_user_reminders(
        db: Session, user_id: uuid.UUID, is_active: Optional[bool] = None
    ) -> List[Reminder]:
        """Fetch all reminders for a user."""
        query = (
            db.query(Reminder)
            .options(joinedload(Reminder.habit))
            .filter(Reminder.user_id == user_id)
        )
        if is_active is not None:
            query = query.filter(Reminder.is_active == is_active)
        return query.order_by(Reminder.reminder_time.asc()).all()

    @staticmethod
    def get_by_habit_id(db: Session, habit_id: uuid.UUID) -> List[Reminder]:
        """Fetch reminders for a specific habit."""
        return (
            db.query(Reminder)
            .options(joinedload(Reminder.habit))
            .filter(Reminder.habit_id == habit_id)
            .all()
        )

    @staticmethod
    def update(
        db: Session, reminder: Reminder, update_data: Dict[str, Any]
    ) -> Reminder:
        """Update reminder fields."""
        for key, value in update_data.items():
            setattr(reminder, key, value)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def delete(db: Session, reminder: Reminder) -> None:
        """Hard delete a reminder."""
        db.delete(reminder)
        db.commit()

    @staticmethod
    def get_all_active_with_habits_and_users(db: Session) -> List[Reminder]:
        """Fetch all active reminders with habits for batch scheduler evaluation."""
        return (
            db.query(Reminder)
            .options(joinedload(Reminder.habit))
            .filter(Reminder.is_active == True)
            .all()
        )
