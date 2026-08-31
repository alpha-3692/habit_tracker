import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import (
    String, Boolean, Date, ForeignKey, Text, Integer,
    Numeric, JSON, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.goal import Goal
    from app.models.habit_log import HabitLog
    from app.models.reminder import Reminder


class Habit(Base, TimestampMixin):
    """
    A trackable habit belonging to a user. Optionally associated with a goal.

    Frequency types:
        - daily: Every day
        - specific_days: Only on days listed in frequency_days ([0=Mon..6=Sun])
        - weekdays: Mon-Fri
        - weekends: Sat-Sun

    Streak data (current_streak, best_streak, total_completions) is cached here
    for performance but always re-derivable from habit_logs.
    """
    __tablename__ = "habits"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Frequency
    frequency_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="daily"
    )
    frequency_days: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True
    )  # e.g., [0, 1, 2, 3, 4] for Mon-Fri

    # Target (optional — e.g., "2 problems", "60 minutes")
    target_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    target_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Appearance
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Scheduling
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Cached streak data (always re-derivable from habit_logs)
    current_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_completions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Relationships ──────────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="habits")
    goal: Mapped[Optional["Goal"]] = relationship("Goal", back_populates="habits")
    logs: Mapped[List["HabitLog"]] = relationship(
        "HabitLog", back_populates="habit", cascade="all, delete-orphan"
    )
    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder", back_populates="habit", cascade="all, delete-orphan"
    )

    # ── Indexes ───────────────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_habits_user_id_active", "user_id", "is_active", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Habit id={self.id} title={self.title!r}>"
