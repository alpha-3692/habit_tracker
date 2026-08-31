import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import (
    String, Date, DateTime, ForeignKey, Text,
    Numeric, Index, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.habit import Habit
    from app.models.user import User


class HabitLog(Base):
    """
    Immutable record of a single habit completion.

    This is the source of truth for all streak and analytics calculations.
    The unique constraint on (habit_id, completed_date) prevents duplicate
    completions for the same day.

    completed_date is DATE (not TIMESTAMPTZ) because completion is per-calendar-day
    in the user's timezone. The full timestamp is preserved in completed_at.
    """
    __tablename__ = "habit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    habit_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("habits.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Denormalized for query performance — avoids joining habits table
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    completed_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    habit: Mapped["Habit"] = relationship("Habit", back_populates="logs")
    user: Mapped["User"] = relationship("User")

    # ── Indexes and Constraints ───────────────────────────────────────────────
    __table_args__ = (
        # Prevents completing same habit twice on same calendar date
        UniqueConstraint("habit_id", "completed_date", name="uq_habit_logs_habit_date"),
        Index("ix_habit_logs_user_id_date", "user_id", "completed_date"),
        Index("ix_habit_logs_habit_id_date", "habit_id", "completed_date"),
    )

    def __repr__(self) -> str:
        return f"<HabitLog habit_id={self.habit_id} date={self.completed_date}>"
