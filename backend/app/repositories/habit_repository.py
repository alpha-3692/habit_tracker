from typing import Optional, List, Set
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.models.habit import Habit


class HabitRepository:
    @staticmethod
    def get_by_id(db: Session, habit_id: UUID) -> Optional[Habit]:
        stmt = select(Habit).where(and_(Habit.id == habit_id, Habit.is_deleted == False))
        return db.scalars(stmt).first()

    @staticmethod
    def get_user_habits(
        db: Session,
        user_id: UUID,
        is_active: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        goal_id: Optional[UUID] = None,
    ) -> List[Habit]:
        conditions = [Habit.user_id == user_id, Habit.is_deleted == False]

        if is_active is not None:
            conditions.append(Habit.is_active == is_active)
        if is_archived is not None:
            conditions.append(Habit.is_archived == is_archived)
        if goal_id is not None:
            conditions.append(Habit.goal_id == goal_id)

        stmt = select(Habit).where(and_(*conditions)).order_by(Habit.order_index.asc(), Habit.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def count_active_habits(db: Session, user_id: UUID) -> int:
        stmt = select(func.count(Habit.id)).where(
            and_(
                Habit.user_id == user_id,
                Habit.is_active == True,
                Habit.is_archived == False,
                Habit.is_deleted == False,
            )
        )
        return db.scalar(stmt) or 0

    @staticmethod
    def create(db: Session, user_id: UUID, habit_data: dict) -> Habit:
        habit = Habit(user_id=user_id, **habit_data)
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def update(db: Session, habit: Habit, update_data: dict) -> Habit:
        for key, value in update_data.items():
            if hasattr(habit, key):
                setattr(habit, key, value)
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def archive(db: Session, habit: Habit, is_archived: bool) -> Habit:
        habit.is_archived = is_archived
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def soft_delete(db: Session, habit: Habit) -> Habit:
        habit.is_deleted = True
        habit.is_active = False
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit

    @staticmethod
    def update_cached_streak(
        db: Session,
        habit: Habit,
        current_streak: int,
        best_streak: int,
        total_completions: int,
    ) -> Habit:
        habit.current_streak = current_streak
        habit.best_streak = best_streak
        habit.total_completions = total_completions
        db.add(habit)
        db.commit()
        db.refresh(habit)
        return habit
