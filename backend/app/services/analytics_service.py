from datetime import date, timedelta
from typing import List, Dict, Set, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.habit import Habit
from app.repositories.habit_repository import HabitRepository
from app.repositories.habit_log_repository import HabitLogRepository
from app.services.streak_service import StreakService
from app.utils.datetime_utils import get_user_today
from app.schemas.analytics import (
    AnalyticsTrendsResponse,
    WeeklyTrendItem,
    DayOfWeekItem,
    CategoryPerformanceItem,
    BehaviorInsight,
)

WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


class AnalyticsService:
    @classmethod
    def get_trends(
        cls,
        db: Session,
        user: User,
        days: int = 30,
    ) -> AnalyticsTrendsResponse:
        if days < 7 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="days parameter must be between 7 and 365.",
            )

        today = get_user_today(user.timezone)
        start_date = today - timedelta(days=days - 1)
        end_date = today

        # Fetch active habits for current user
        habits = HabitRepository.get_user_habits(
            db, user_id=user.id, is_active=True, is_archived=False
        )

        # Fetch all logs in range
        logs = HabitLogRepository.get_logs_for_user_range(
            db, user_id=user.id, start_date=start_date, end_date=end_date
        )
        completed_pairs: Set[tuple] = {(log.habit_id, log.completed_date) for log in logs}

        # ── 1. Overall Consistency & Aggregations ─────────────────────────────
        total_expected = 0
        total_completed = 0

        # Day of week buckets: [0..6] -> {expected, completed}
        dow_buckets = {i: {"expected": 0, "completed": 0} for i in range(7)}

        # Category buckets: category -> {habit_count, expected, completed}
        category_habits = defaultdict(set)
        category_stats = defaultdict(lambda: {"expected": 0, "completed": 0})
        for h in habits:
            category_habits[h.category].add(h.id)

        # Daily date iteration
        curr = start_date
        while curr <= end_date:
            weekday = curr.weekday()
            for h in habits:
                if StreakService.is_due_on_date(h, curr):
                    total_expected += 1
                    dow_buckets[weekday]["expected"] += 1
                    category_stats[h.category]["expected"] += 1

                    if (h.id, curr) in completed_pairs:
                        total_completed += 1
                        dow_buckets[weekday]["completed"] += 1
                        category_stats[h.category]["completed"] += 1

            curr += timedelta(days=1)

        overall_pct = (
            round((total_completed / total_expected) * 100.0, 1)
            if total_expected > 0
            else 0.0
        )

        # ── 2. Momentum Score (0–100) ──────────────────────────────────────────
        # Rolling 7-day rate (50%) + Rolling 30-day rate (30%) + Active streak bonus (20%)
        curr_7 = today - timedelta(days=6)
        exp_7, comp_7 = 0, 0
        while curr_7 <= today:
            for h in habits:
                if StreakService.is_due_on_date(h, curr_7):
                    exp_7 += 1
                    if (h.id, curr_7) in completed_pairs:
                        comp_7 += 1
            curr_7 += timedelta(days=1)
        rate_7 = (comp_7 / exp_7) if exp_7 > 0 else 0.0

        curr_30 = today - timedelta(days=29)
        exp_30, comp_30 = 0, 0
        while curr_30 <= today:
            for h in habits:
                if StreakService.is_due_on_date(h, curr_30):
                    exp_30 += 1
                    if (h.id, curr_30) in completed_pairs:
                        comp_30 += 1
            curr_30 += timedelta(days=1)
        rate_30 = (comp_30 / exp_30) if exp_30 > 0 else 0.0

        avg_streak = (
            sum(h.current_streak for h in habits) / len(habits) if habits else 0.0
        )
        streak_bonus = min(20.0, avg_streak * 2.0)
        momentum_score = int(
            round(min(100.0, (rate_7 * 50.0) + (rate_30 * 30.0) + streak_bonus))
        )

        # ── 3. Weekly Trends ──────────────────────────────────────────────────
        weekly_trends: List[WeeklyTrendItem] = []
        w_start = start_date
        while w_start <= end_date:
            w_end = min(w_start + timedelta(days=6), end_date)
            w_exp, w_comp = 0, 0
            d = w_start
            while d <= w_end:
                for h in habits:
                    if StreakService.is_due_on_date(h, d):
                        w_exp += 1
                        if (h.id, d) in completed_pairs:
                            w_comp += 1
                d += timedelta(days=1)

            w_pct = round((w_comp / w_exp) * 100.0, 1) if w_exp > 0 else 0.0
            weekly_trends.append(
                WeeklyTrendItem(
                    week_start=w_start,
                    week_end=w_end,
                    expected=w_exp,
                    completed=w_comp,
                    percentage=w_pct,
                )
            )
            w_start = w_end + timedelta(days=1)

        # ── 4. Day of Week Breakdown ──────────────────────────────────────────
        day_of_week: List[DayOfWeekItem] = []
        for i in range(7):
            e = dow_buckets[i]["expected"]
            c = dow_buckets[i]["completed"]
            pct = round((c / e) * 100.0, 1) if e > 0 else 0.0
            day_of_week.append(
                DayOfWeekItem(
                    day_name=WEEKDAY_NAMES[i],
                    day_index=i,
                    expected=e,
                    completed=c,
                    percentage=pct,
                )
            )

        # ── 5. Category Breakdown ─────────────────────────────────────────────
        category_breakdown: List[CategoryPerformanceItem] = []
        for cat, stats in category_stats.items():
            e = stats["expected"]
            c = stats["completed"]
            pct = round((c / e) * 100.0, 1) if e > 0 else 0.0
            category_breakdown.append(
                CategoryPerformanceItem(
                    category=cat,
                    habit_count=len(category_habits[cat]),
                    expected=e,
                    completed=c,
                    percentage=pct,
                )
            )
        category_breakdown.sort(key=lambda x: x.percentage, reverse=True)

        # ── 6. Deterministic Behavioral Insights ──────────────────────────────
        insights: List[BehaviorInsight] = []

        # Find best and weakest active days
        active_days = [d for d in day_of_week if d.expected >= 3]
        if active_days:
            best_day = max(active_days, key=lambda d: d.percentage)
            weakest_day = min(active_days, key=lambda d: d.percentage)

            if best_day.percentage > 0:
                insights.append(
                    BehaviorInsight(
                        type="best_day",
                        title=f"Peak Consistency: {best_day.day_name}",
                        description=f"You complete {best_day.percentage}% of habits scheduled on {best_day.day_name}s.",
                        impact="positive",
                    )
                )

            if weakest_day.percentage < best_day.percentage and weakest_day.percentage < 70.0:
                insights.append(
                    BehaviorInsight(
                        type="weakest_day",
                        title=f"Opportunity Area: {weakest_day.day_name}",
                        description=f"{weakest_day.day_name}s have a {weakest_day.percentage}% completion rate. Focus on keeping routines friction-free on this day.",
                        impact="warning",
                    )
                )

        # Weekend drop detection
        weekday_days = [day_of_week[i] for i in range(5) if day_of_week[i].expected > 0]
        weekend_days = [day_of_week[i] for i in range(5, 7) if day_of_week[i].expected > 0]
        if weekday_days and weekend_days:
            weekday_avg = sum(d.percentage for d in weekday_days) / len(weekday_days)
            weekend_avg = sum(d.percentage for d in weekend_days) / len(weekend_days)
            if weekday_avg - weekend_avg >= 20.0:
                insights.append(
                    BehaviorInsight(
                        type="weekend_drop",
                        title="Weekend Rhythm Shift",
                        description=f"Your weekend completion rate ({round(weekend_avg, 1)}%) is lower than weekdays ({round(weekday_avg, 1)}%). Consider lighter weekend targets.",
                        impact="neutral",
                    )
                )

        # Category leader
        if category_breakdown and category_breakdown[0].expected >= 5:
            top_cat = category_breakdown[0]
            insights.append(
                BehaviorInsight(
                    type="category_leader",
                    title=f"Top Category: {top_cat.category.capitalize()}",
                    description=f"{top_cat.category.capitalize()} habits are leading with {top_cat.percentage}% consistency across {top_cat.completed} completions.",
                    impact="positive",
                )
            )

        # Momentum summary insight
        if momentum_score >= 80:
            insights.append(
                BehaviorInsight(
                    type="momentum",
                    title="High Execution Momentum",
                    description=f"Your consistency score is {momentum_score}/100. Excellent habit lock-in!",
                    impact="positive",
                )
            )
        elif momentum_score < 40 and total_expected > 0:
            insights.append(
                BehaviorInsight(
                    type="momentum",
                    title="Rebuild Momentum",
                    description=f"Your momentum score is {momentum_score}/100. Focus on completing just 1 core habit today to restart your streaks.",
                    impact="warning",
                )
            )

        return AnalyticsTrendsResponse(
            time_range_days=days,
            overall_consistency=overall_pct,
            total_habits_tracked=len(habits),
            total_completions=total_completed,
            momentum_score=momentum_score,
            weekly_trends=weekly_trends,
            day_of_week=day_of_week,
            category_breakdown=category_breakdown,
            insights=insights,
        )
