from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, update

from app.models.goal import Goal
from app.models.habit import Habit


class GoalRepository:
    @staticmethod
    def get_by_id(db: Session, goal_id: UUID) -> Optional[Goal]:
        stmt = select(Goal).where(and_(Goal.id == goal_id, Goal.is_deleted == False))
        return db.scalars(stmt).first()

    @staticmethod
    def get_user_goals(
        db: Session,
        user_id: UUID,
        status: Optional[str] = None,
    ) -> List[Goal]:
        conditions = [Goal.user_id == user_id, Goal.is_deleted == False]
        if status:
            conditions.append(Goal.status == status)

        stmt = select(Goal).where(and_(*conditions)).order_by(Goal.created_at.desc())
        return list(db.scalars(stmt).all())

    @staticmethod
    def create(db: Session, user_id: UUID, goal_data: dict) -> Goal:
        goal = Goal(user_id=user_id, **goal_data)
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update(db: Session, goal: Goal, update_data: dict) -> Goal:
        for key, value in update_data.items():
            if hasattr(goal, key):
                setattr(goal, key, value)
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def soft_delete(db: Session, goal: Goal) -> Goal:
        goal.is_deleted = True
        db.add(goal)
        # Unlink habits from this goal safely so habit histories are preserved
        stmt = update(Habit).where(Habit.goal_id == goal.id).values(goal_id=None)
        db.execute(stmt)
        db.commit()
        db.refresh(goal)
        return goal
