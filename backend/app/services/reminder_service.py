import uuid
from datetime import datetime, timedelta, time, date
import pytz
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.habit import Habit
from app.models.reminder import Reminder
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.utils.datetime_utils import get_user_today
from app.core.exceptions import HabitNotFoundException, ForbiddenException
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderPublic,
    DueReminderItem,
    NextReminderPublic,
)


def _get_tz(timezone_str: Optional[str]):
    if not timezone_str:
        return pytz.UTC
    try:
        return pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        return pytz.UTC


class ReminderService:
    @classmethod
    def _to_public(cls, reminder: Reminder) -> ReminderPublic:
        habit_title = reminder.habit.title if reminder.habit else None
        habit_category = reminder.habit.category if reminder.habit else None
        return ReminderPublic(
            id=reminder.id,
            habit_id=reminder.habit_id,
            habit_title=habit_title,
            habit_category=habit_category,
            user_id=reminder.user_id,
            reminder_time=reminder.reminder_time,
            days_of_week=reminder.days_of_week,
            is_active=reminder.is_active,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at,
        )

    @classmethod
    def create_reminder(
        cls, db: Session, user: User, payload: ReminderCreate
    ) -> ReminderPublic:
        # Validate habit
        habit = HabitRepository.get_by_id(db, payload.habit_id)
        if not habit:
            raise HabitNotFoundException()
        if habit.user_id != user.id:
            raise ForbiddenException("You do not have permission to add reminders for this habit")
        if habit.is_deleted or habit.is_archived:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create a reminder for an archived or deleted habit.",
            )

        reminder = ReminderRepository.create(
            db,
            user_id=user.id,
            habit_id=payload.habit_id,
            reminder_time=payload.reminder_time,
            days_of_week=payload.days_of_week,
            is_active=payload.is_active,
        )
        return cls._to_public(reminder)

    @classmethod
    def get_user_reminders(
        cls, db: Session, user: User, is_active: Optional[bool] = None
    ) -> List[ReminderPublic]:
        reminders = ReminderRepository.get_user_reminders(
            db, user_id=user.id, is_active=is_active
        )
        return [cls._to_public(r) for r in reminders]

    @classmethod
    def get_reminder_by_id(
        cls, db: Session, user: User, reminder_id: uuid.UUID
    ) -> ReminderPublic:
        reminder = ReminderRepository.get_by_id(db, reminder_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
            )
        if reminder.user_id != user.id:
            raise ForbiddenException("You do not have permission to access this reminder")
        return cls._to_public(reminder)

    @classmethod
    def update_reminder(
        cls, db: Session, user: User, reminder_id: uuid.UUID, payload: ReminderUpdate
    ) -> ReminderPublic:
        reminder = ReminderRepository.get_by_id(db, reminder_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
            )
        if reminder.user_id != user.id:
            raise ForbiddenException("You do not have permission to modify this reminder")

        update_dict = payload.model_dump(exclude_unset=True)
        updated = ReminderRepository.update(db, reminder, update_dict)
        return cls._to_public(updated)

    @classmethod
    def delete_reminder(
        cls, db: Session, user: User, reminder_id: uuid.UUID
    ) -> None:
        reminder = ReminderRepository.get_by_id(db, reminder_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found"
            )
        if reminder.user_id != user.id:
            raise ForbiddenException("You do not have permission to delete this reminder")

        ReminderRepository.delete(db, reminder)

    @classmethod
    def get_due_reminders(
        cls, db: Session, current_utc_datetime: Optional[datetime] = None
    ) -> List[DueReminderItem]:
        """
        Deterministic scheduler evaluation:
        Evaluates which reminders are due at the given UTC moment,
        respecting user local timezones, habit schedules, and completion states.
        """
        if not current_utc_datetime:
            current_utc_datetime = datetime.now(pytz.UTC)
        elif current_utc_datetime.tzinfo is None:
            current_utc_datetime = pytz.UTC.localize(current_utc_datetime)

        active_reminders = ReminderRepository.get_all_active_with_habits_and_users(db)
        due_items: List[DueReminderItem] = []

        for reminder in active_reminders:
            habit = reminder.habit
            if not habit or not habit.is_active or habit.is_archived or habit.is_deleted:
                continue

            user = db.query(User).filter(User.id == reminder.user_id).first()
            if not user:
                continue

            user_tz = _get_tz(user.timezone)
            local_dt = current_utc_datetime.astimezone(user_tz)
            local_date = local_dt.date()
            local_weekday = local_dt.weekday()  # 0 = Mon, 6 = Sun

            # 1. Day filter check
            if reminder.days_of_week is not None and len(reminder.days_of_week) > 0:
                if local_weekday not in reminder.days_of_week:
                    continue
            else:
                # Follow habit schedule
                if not StreakService.is_due_on_date(habit, local_date):
                    continue

            # 2. Time match check (match hour and minute)
            if (
                reminder.reminder_time.hour != local_dt.hour
                or reminder.reminder_time.minute != local_dt.minute
            ):
                continue

            # 3. Duplicate / Completion prevention:
            # If habit is already completed for local date, do not fire reminder
            log = HabitLogRepository.get_log_by_habit_and_date(db, habit.id, local_date)
            if log is not None:
                continue

            due_items.append(
                DueReminderItem(
                    reminder_id=reminder.id,
                    habit_id=habit.id,
                    habit_title=habit.title,
                    habit_category=habit.category,
                    user_id=user.id,
                    user_timezone=user.timezone,
                    local_time=reminder.reminder_time.strftime("%H:%M"),
                    local_date=local_date,
                    message=f"Time to complete '{habit.title}'!",
                )
            )

        return due_items

    @classmethod
    def get_next_reminder_for_user(
        cls, db: Session, user: User
    ) -> Optional[NextReminderPublic]:
        """Calculates next upcoming reminder for the user."""
        reminders = ReminderRepository.get_user_reminders(
            db, user_id=user.id, is_active=True
        )
        if not reminders:
            return None

        user_tz = _get_tz(user.timezone)
        now_local = datetime.now(user_tz)
        today = now_local.date()

        upcoming: List[tuple] = []  # (datetime, reminder)

        for r in reminders:
            habit = r.habit
            if not habit or not habit.is_active or habit.is_archived or habit.is_deleted:
                continue

            # Check next 7 days
            for d_offset in range(7):
                candidate_date = today + timedelta(days=d_offset)
                candidate_weekday = candidate_date.weekday()

                # Check if due on this weekday
                if r.days_of_week is not None and len(r.days_of_week) > 0:
                    if candidate_weekday not in r.days_of_week:
                        continue
                else:
                    if not StreakService.is_due_on_date(habit, candidate_date):
                        continue

                # Candidate datetime
                candidate_naive = datetime.combine(candidate_date, r.reminder_time)
                candidate_dt = user_tz.localize(candidate_naive)
                if candidate_dt > now_local:
                    # Check if already completed today
                    if d_offset == 0:
                        log = HabitLogRepository.get_log_by_habit_and_date(db, habit.id, today)
                        if log is not None:
                            continue
                    upcoming.append((candidate_dt, r))
                    break

        if not upcoming:
            return None

        upcoming.sort(key=lambda x: x[0])
        next_dt, next_reminder = upcoming[0]

        # Format occurrence string
        if next_dt.date() == today:
            occurrence = f"Today at {next_reminder.reminder_time.strftime('%H:%M')}"
        elif next_dt.date() == today + timedelta(days=1):
            occurrence = f"Tomorrow at {next_reminder.reminder_time.strftime('%H:%M')}"
        else:
            weekday_name = next_dt.strftime("%a")
            occurrence = f"{weekday_name} at {next_reminder.reminder_time.strftime('%H:%M')}"

        return NextReminderPublic(
            reminder_id=next_reminder.id,
            habit_id=next_reminder.habit_id,
            habit_title=next_reminder.habit.title,
            habit_category=next_reminder.habit.category,
            reminder_time=next_reminder.reminder_time,
            next_occurrence=occurrence,
        )
