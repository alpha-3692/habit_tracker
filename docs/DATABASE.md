# HabitForge — Database Design

**Version:** 0.1.0  
**Status:** Active  
**Last Updated:** 2026-09-01  
**Database:** PostgreSQL 15+  
**ORM:** SQLAlchemy 2.x  
**Migrations:** Alembic

---

## 1. Design Principles

- Normalized schema (3NF where practical)
- Every table has `id` (UUID), `created_at`, `updated_at`
- Soft deletes via `deleted_at` or `is_archived` where appropriate
- All foreign keys enforced at database level
- Proper indexes on commonly queried columns
- No raw SQL in application code — use SQLAlchemy ORM

---

## 2. Entity Relationship Diagram

```
users
  │
  ├──── goals (user_id FK)
  │       │
  │       └──── habits (goal_id FK, nullable)
  │
  ├──── habits (user_id FK)
  │       │
  │       ├──── habit_logs (habit_id FK)
  │       │
  │       └──── reminders (habit_id FK)
  │
  ├──── user_achievements (user_id FK)
  │       │
  │       └──── achievements (achievement_id FK)
  │
  └──── subscriptions (user_id FK)
```

---

## 3. Table Definitions

### 3.1 `users`

The central entity. All user data is owned by this record.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Lowercase enforced |
| `username` | VARCHAR(50) | UNIQUE, NULLABLE | Optional display name |
| `hashed_password` | VARCHAR(255) | NULLABLE | Null if OAuth-only account |
| `full_name` | VARCHAR(100) | NULLABLE | |
| `avatar_url` | TEXT | NULLABLE | |
| `timezone` | VARCHAR(50) | NOT NULL, DEFAULT 'UTC' | IANA timezone string |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | Email verification |
| `subscription_tier` | VARCHAR(20) | NOT NULL, DEFAULT 'free' | enum: free, pro |
| `onboarding_completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `last_login_at` | TIMESTAMPTZ | NULLABLE | |

**Indexes:**
- `ix_users_email` ON `email`
- `ix_users_username` ON `username`

---

### 3.2 `goals`

User-defined goals that habits can be associated with.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id, NOT NULL | CASCADE DELETE |
| `title` | VARCHAR(200) | NOT NULL | |
| `description` | TEXT | NULLABLE | |
| `category` | VARCHAR(50) | NOT NULL | See Category enum |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active, completed, paused |
| `target_date` | DATE | NULLABLE | Goal deadline |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Indexes:**
- `ix_goals_user_id` ON `user_id`
- `ix_goals_user_id_status` ON `(user_id, status)`

**Category Enum:**
`fitness` | `study` | `coding` | `reading` | `sleep` | `productivity` | `career` | `personal_growth` | `other`

---

### 3.3 `habits`

Individual habits a user tracks. Can optionally belong to a goal.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id, NOT NULL | CASCADE DELETE |
| `goal_id` | UUID | FK → goals.id, NULLABLE | Optional goal association |
| `title` | VARCHAR(200) | NOT NULL | |
| `description` | TEXT | NULLABLE | |
| `category` | VARCHAR(50) | NOT NULL | See Category enum |
| `frequency_type` | VARCHAR(20) | NOT NULL | daily, weekly, specific_days |
| `frequency_days` | JSON | NULLABLE | [0,1,2,3,4,5,6] for Mon-Sun |
| `target_value` | DECIMAL(10,2) | NULLABLE | e.g., 2 (problems), 60 (mins) |
| `target_unit` | VARCHAR(50) | NULLABLE | e.g., "problems", "minutes" |
| `color` | VARCHAR(7) | NULLABLE | Hex color #RRGGBB |
| `icon` | VARCHAR(50) | NULLABLE | Icon identifier |
| `start_date` | DATE | NOT NULL, DEFAULT today | |
| `end_date` | DATE | NULLABLE | Optional end date |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `is_archived` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft archive |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft delete |
| `order_index` | INTEGER | NOT NULL, DEFAULT 0 | Display ordering |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Indexes:**
- `ix_habits_user_id` ON `user_id`
- `ix_habits_user_id_active` ON `(user_id, is_active, is_deleted)`
- `ix_habits_goal_id` ON `goal_id`

**Frequency Type Enum:**
`daily` | `specific_days` | `weekdays` | `weekends`

---

### 3.4 `habit_logs`

Immutable record of each habit completion. The source of truth for all streak and analytics calculations.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `habit_id` | UUID | FK → habits.id, NOT NULL | CASCADE DELETE |
| `user_id` | UUID | FK → users.id, NOT NULL | Denormalized for query performance |
| `completed_date` | DATE | NOT NULL | The calendar date of completion |
| `completed_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Exact timestamp |
| `value` | DECIMAL(10,2) | NULLABLE | Actual value completed (if tracked) |
| `notes` | TEXT | NULLABLE | Optional user note |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Constraints:**
- `uq_habit_logs_habit_date` UNIQUE ON `(habit_id, completed_date)` — prevents duplicate completion per day

**Indexes:**
- `ix_habit_logs_habit_id` ON `habit_id`
- `ix_habit_logs_user_id_date` ON `(user_id, completed_date)`
- `ix_habit_logs_habit_id_date` ON `(habit_id, completed_date DESC)`

> **Design Note:** `completed_date` is a DATE (not TIMESTAMPTZ) because completion is per-calendar-day in the user's timezone. The full timestamp is stored in `completed_at` for future analytics.

---

### 3.5 `reminders`

Time-based reminders for habits.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `habit_id` | UUID | FK → habits.id, NOT NULL | CASCADE DELETE |
| `user_id` | UUID | FK → users.id, NOT NULL | |
| `reminder_time` | TIME | NOT NULL | Local time in user's timezone |
| `days_of_week` | JSON | NULLABLE | [0..6], null = all habit days |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Indexes:**
- `ix_reminders_habit_id` ON `habit_id`

---

### 3.6 `achievements`

System-defined achievement definitions (not per-user).

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `code` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., "STREAK_7" |
| `title` | VARCHAR(100) | NOT NULL | "7-Day Streak" |
| `description` | TEXT | NOT NULL | |
| `icon` | VARCHAR(50) | NULLABLE | |
| `category` | VARCHAR(50) | NOT NULL | streak, completion, milestone |
| `criteria_type` | VARCHAR(50) | NOT NULL | streak_days, total_completions, etc. |
| `criteria_value` | INTEGER | NOT NULL | e.g., 7 (days) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Seed Data (MVP):**
| code | title | criteria |
|------|-------|---------|
| `FIRST_HABIT` | First Habit | type: habit_created, value: 1 |
| `STREAK_7` | 7-Day Streak | type: streak_days, value: 7 |
| `STREAK_30` | 30-Day Streak | type: streak_days, value: 30 |
| `COMPLETIONS_100` | Century Club | type: total_completions, value: 100 |

---

### 3.7 `user_achievements`

Junction table tracking which achievements each user has unlocked.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id, NOT NULL | CASCADE DELETE |
| `achievement_id` | UUID | FK → achievements.id, NOT NULL | |
| `habit_id` | UUID | FK → habits.id, NULLABLE | Which habit triggered it |
| `unlocked_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Constraints:**
- `uq_user_achievements_user_achievement` UNIQUE ON `(user_id, achievement_id)`

**Indexes:**
- `ix_user_achievements_user_id` ON `user_id`

---

### 3.8 `subscriptions`

Subscription state for each user. Decoupled from payment provider.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id, NOT NULL, UNIQUE | One subscription per user |
| `tier` | VARCHAR(20) | NOT NULL, DEFAULT 'free' | free, pro |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active, cancelled, expired, trial |
| `trial_ends_at` | TIMESTAMPTZ | NULLABLE | |
| `current_period_start` | TIMESTAMPTZ | NULLABLE | |
| `current_period_end` | TIMESTAMPTZ | NULLABLE | |
| `cancelled_at` | TIMESTAMPTZ | NULLABLE | |
| `provider` | VARCHAR(50) | NULLABLE | stripe, paddle, etc. |
| `provider_subscription_id` | VARCHAR(255) | NULLABLE | External subscription ID |
| `provider_customer_id` | VARCHAR(255) | NULLABLE | External customer ID |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Indexes:**
- `ix_subscriptions_user_id` ON `user_id`
- `ix_subscriptions_provider_id` ON `provider_subscription_id`

---

## 4. Future Tables (Not Implemented in MVP)

### `ai_conversations`
Track AI chat sessions for context and usage limits.

### `ai_usage`
Track token usage per user per day for rate limiting and billing.

### `challenges`
Group habit challenges between users.

### `challenge_members`
Members participating in a challenge.

### `notifications`
Scheduled and triggered notification queue.

### `oauth_accounts`
Link social login accounts to users (Google, Apple, etc.).

---

## 5. Streak Calculation Design

Streaks are **never stored as a simple counter** (which can become stale or be exploited).

Instead, streak calculations are **derived from `habit_logs`** on demand:

```python
def calculate_current_streak(habit_id, user_timezone, db):
    """
    Algorithm:
    1. Get habit's frequency_type and frequency_days
    2. Get today's date in user's timezone
    3. Walk backwards day by day
    4. For each date, check if the habit was 'due' that day
    5. If due and completed → continue streak
    6. If due and NOT completed → streak broken
    7. If not due that day → skip (non-habit day doesn't break streak)
    8. Return count of consecutive completed due-days
    """
```

**Cached Fields** (denormalized on `habits` or computed view for performance):
- `current_streak` — computed, cached, refreshed on completion/daily job
- `best_streak` — computed, cached, updated when current exceeds it
- `total_completions` — count of habit_logs rows

---

## 6. Free Tier Enforcement

Business rule: Free users can have max 5 active habits.

This is enforced in `HabitService.create_habit()`:
```python
if user.subscription_tier == 'free':
    active_count = habit_repo.count_active_habits(user_id)
    if active_count >= FREE_TIER_HABIT_LIMIT:
        raise HabitLimitExceedException(limit=FREE_TIER_HABIT_LIMIT)
```

---

## 7. Migration Strategy

All schema changes go through Alembic:

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "add_user_timezone_column"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

Migration files are in `backend/alembic/versions/` and committed to git.

---

*Update this document when database schema changes.*
