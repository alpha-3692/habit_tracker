import uuid
from datetime import datetime, time
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Time, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.habit import Habit


class Reminder(Base, TimestampMixin):
    """Time-based reminder for a habit."""
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    habit_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reminder_time: Mapped[time] = mapped_column(Time, nullable=False)
    days_of_week: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    habit: Mapped["Habit"] = relationship("Habit", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<Reminder habit_id={self.habit_id} time={self.reminder_time}>"
