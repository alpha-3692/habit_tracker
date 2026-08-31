from typing import Optional, List, Set
from uuid import UUID
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.habit_log import HabitLog


class HabitLogRepository:
    @staticmethod
    def get_log_by_habit_and_date(
        db: Session, habit_id: UUID, completed_date: date
    ) -> Optional[HabitLog]:
        stmt = select(HabitLog).where(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.completed_date == completed_date,
            )
        )
        return db.scalars(stmt).first()

    @staticmethod
    def get_completed_dates_set(db: Session, habit_id: UUID) -> Set[date]:
        stmt = select(HabitLog.completed_date).where(HabitLog.habit_id == habit_id)
        results = db.scalars(stmt).all()
        return set(results)

    @staticmethod
    def get_logs_for_habit(db: Session, habit_id: UUID) -> List[HabitLog]:
        stmt = (
            select(HabitLog)
            .where(HabitLog.habit_id == habit_id)
            .order_by(HabitLog.completed_date.desc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_logs_for_habit_range(
        db: Session, habit_id: UUID, start_date: date, end_date: date
    ) -> List[HabitLog]:
        stmt = (
            select(HabitLog)
            .where(
                and_(
                    HabitLog.habit_id == habit_id,
                    HabitLog.completed_date >= start_date,
                    HabitLog.completed_date <= end_date,
                )
            )
            .order_by(HabitLog.completed_date.asc())
        )
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_logs_for_user_range(
        db: Session,
        user_id: UUID,
        start_date: date,
        end_date: date,
        habit_id: Optional[UUID] = None,
    ) -> List[HabitLog]:
        conditions = [
            HabitLog.user_id == user_id,
            HabitLog.completed_date >= start_date,
            HabitLog.completed_date <= end_date,
        ]
        if habit_id:
            conditions.append(HabitLog.habit_id == habit_id)

        stmt = select(HabitLog).where(and_(*conditions)).order_by(HabitLog.completed_date.asc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def create_log(
        db: Session,
        habit_id: UUID,
        user_id: UUID,
        completed_date: date,
        value: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> HabitLog:
        log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            completed_date=completed_date,
            value=value,
            notes=notes,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def delete_log(db: Session, habit_log: HabitLog):
        db.delete(habit_log)
        db.commit()
