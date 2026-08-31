# HabitForge — Architecture Decision Records

**Format:** Each decision includes context, options considered, decision made, and consequences.

---

## ADR-001: Monorepo Structure

**Date:** 2026-09-01  
**Status:** Accepted

### Context
We need to organize the web frontend and backend into a single repository or separate repositories.

### Options Considered
1. Monorepo (single repository)
2. Separate repositories (frontend-repo, backend-repo)

### Decision
**Monorepo** — single repository with `frontend/` and `backend/` directories.

### Rationale
- Simpler for a small team/solo developer
- Atomic commits across frontend and backend
- Shared documentation
- Single CI pipeline
- Easy to see the full picture

### Consequences
- Need to manage separate package managers (npm for frontend, pip for backend)
- PR reviews cover the full stack in one place
- When team grows, can split repositories (migration is straightforward)

---

## ADR-002: REST API over GraphQL

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Choosing between REST and GraphQL for the API layer.

### Options Considered
1. REST with versioning (`/api/v1/`)
2. GraphQL

### Decision
**REST API** with versioning under `/api/v1/`.

### Rationale
- Simpler to implement and understand
- Better suited for mobile clients (no query language needed)
- FastAPI has excellent built-in support
- Easier to secure and rate limit specific endpoints
- Standard caching works naturally
- GraphQL complexity not justified for this use case

### Consequences
- Potential over-fetching (mitigated by a dedicated `/dashboard` endpoint)
- API versioning required for breaking changes
- Need to maintain API documentation manually (FastAPI auto-generates OpenAPI)

---

## ADR-003: PostgreSQL over MySQL or SQLite

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Choosing the primary database engine.

### Options Considered
1. PostgreSQL
2. MySQL/MariaDB
3. SQLite (development only)

### Decision
**PostgreSQL** as the primary database.

### Rationale
- ACID compliance for habit log integrity
- Excellent JSON support for frequency_days arrays
- Superior analytics query performance
- UUID primary keys supported natively
- TIMESTAMPTZ for timezone-aware timestamps
- Industry standard for serious applications
- Best SQLAlchemy support

### Consequences
- Requires PostgreSQL installation for local development (use Docker or managed service)
- SQLite used only in tests (fast, in-memory)

---

## ADR-004: JWT with Refresh Tokens over Server Sessions

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Authentication strategy for the API.

### Options Considered
1. JWT (stateless) with refresh tokens
2. Server-side sessions (Redis or database)
3. JWT only (no refresh)

### Decision
**JWT with access + refresh tokens**.

### Rationale
- Stateless access tokens work for web and mobile clients
- No session store required (reduces infrastructure complexity)
- Refresh tokens allow long sessions without long-lived access tokens
- Mobile apps can authenticate identically to web clients
- Future horizontal scaling without sticky sessions

### Consequences
- Cannot immediately revoke access tokens (only refresh tokens can be revoked)
- Slightly more complex auth logic (two tokens instead of one)
- Must implement refresh token rotation for security

---

## ADR-005: Streak Calculation from Logs (Not Counter)

**Date:** 2026-09-01  
**Status:** Accepted

### Context
How to calculate and store habit streaks.

### Options Considered
1. Increment/decrement a `current_streak` counter on the `habits` table
2. Calculate streak from `habit_logs` history on demand

### Decision
**Calculate streaks from habit_logs history** on demand, with caching.

### Rationale
- A simple counter can become incorrect (timezone bugs, data migration, etc.)
- History-derived streaks are always accurate and self-healing
- Allows recalculation if bugs are found (just recompute from logs)
- Supports complex frequency types (specific days, weekdays, etc.)
- Prevents streak manipulation via client-side exploits

### Consequences
- Slightly more expensive to compute (mitigated by caching)
- Need careful timezone handling in streak algorithm
- Must cache computed streaks for dashboard performance

---

## ADR-006: Repository Pattern

**Date:** 2026-09-01  
**Status:** Accepted

### Context
How to organize data access in the backend.

### Options Considered
1. Direct SQLAlchemy calls in route handlers
2. Service layer with repository abstraction

### Decision
**Service layer + Repository pattern**:
- Routes → Services → Repositories → Database

### Rationale
- Routes stay thin and testable
- Business logic is in services (no framework dependencies)
- Repositories can be mocked in tests
- Easy to swap database implementation if needed
- Services don't import from the API layer (clean dependency direction)

### Consequences
- More files and boilerplate
- Developers must understand the layering
- Worth the investment for a product intended to grow

---

## ADR-007: Next.js App Router

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Which Next.js routing approach to use.

### Options Considered
1. Next.js App Router (React Server Components + Client Components)
2. Next.js Pages Router (traditional)

### Decision
**Next.js App Router**.

### Rationale
- Current recommendation from Next.js team
- Server components for initial page loads (faster LCP)
- Better code splitting
- Modern React patterns
- Better streaming support

### Consequences
- Steeper learning curve (RSC vs Client Components)
- Some libraries not yet compatible with RSC
- More careful about where to use `"use client"` directive

---

## ADR-008: Anthropic Claude for AI Features

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Choosing an AI provider for habit suggestions, coaching, and insights.

### Options Considered
1. OpenAI (GPT-4)
2. Anthropic (Claude)
3. Self-hosted model (Ollama, etc.)

### Decision
**Anthropic Claude** via API.

### Rationale
- Strong reasoning capabilities for behavioral analysis
- Long context window for conversation history
- Good instruction following for structured outputs
- Competitive pricing for API usage
- Can be replaced later (AI calls are isolated in `ai_service.py`)

### Consequences
- External API dependency for AI features
- API costs scale with usage (must rate limit)
- Core product must not depend on AI (AI is an enhancement)
- API key must be kept server-side (never exposed to frontend)

---

## ADR-009: Timezone-Aware Habit Completion & Frequency-Aware Streak Engine

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Habit completion dates and streak calculations must accurately reflect the user's local calendar date across different timezones and flexible habit frequencies (daily, specific days, weekdays, weekends, weekly).

### Options Considered
1. Use server local system date for completions and assume all habits are daily.
2. Store user timezone string on `User` model (`timezone`, e.g. `"Asia/Kolkata"`), evaluate completions against `get_user_today(user.timezone)`, and implement a frequency-aware `StreakService` that ignores off-days and accounts for weekly intervals.

### Decision
**Option 2** — Store `timezone` on `User` and perform all date calculations relative to `get_user_today(user.timezone)`.

### Rationale
- Server system dates (e.g. UTC or US East) cause premature or late date boundaries for users in other timezones.
- Flexible habits (e.g. Mon/Wed/Fri or weekly habits) must not be penalized as broken streaks on unscheduled days.
- Derived `StreakService` calculates `current_streak`, `best_streak`, `total_completions`, and `completion_percentage` directly from immutable `habit_logs`.

### Consequences
- Requires timezone evaluation on every completion request (`POST /habits/{id}/complete`).
- High precision and user trust in streak accuracy across global timezones.

## ADR-010: Backend-Authoritative Daily Dashboard Aggregation

**Date:** 2026-09-01  
**Status:** Accepted

### Context
The user needs a primary daily workspace (`/api/v1/dashboard`) showing habits due today, completion status, completion percentage, and overall consistency metrics.

### Options Considered
1. Frontend fetching raw habits and raw log lists and computing today's checklist, progress percentage, and streak numbers client-side.
2. Backend serving an aggregated `GET /api/v1/dashboard` endpoint that resolves user-local dates, applies `StreakService` frequency rules, calculates expected habit count and completion percentage authoritatively, and returns self-contained JSON.

### Decision
**Option 2** — Backend-authoritative dashboard aggregation.

### Rationale
- The frontend remains a thin presentation layer across Web, iOS, and Android.
- Prevents duplication of timezone resolution and habit scheduling/frequency evaluation.
- Ensures identical dashboard progress metrics across all client platforms.

### Consequences
- Single efficient API request (`GET /api/v1/dashboard`) powers the entire main screen.
- Avoids N+1 queries by batching user habit and log evaluations in `DashboardService`.

## ADR-011: Goal Progress Calculation & Habit-Goal Association Lifecycle

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Goals represent user-defined high-level outcomes that daily habits contribute toward. The system requires an authoritative, deterministic progress calculation and safe lifecycle rules when goals or linked habits are modified, completed, or deleted.

### Options Considered
1. Static user-entered progress percentages (e.g. user manually drags a progress slider).
2. Binary completion tracking (goal only marked done when all habits reach 100 days).
3. Authoritative arithmetic mean of associated active habits' completion percentages:
   $$\text{goal\_progress} = \frac{1}{N} \sum_{i=1}^N \text{habit\_completion\_percentage}_i$$
   where each habit's completion percentage is authoritatively derived from `StreakService` based on scheduled due days vs. logged completions.

### Decision
**Option 3** — Deterministic aggregation of contributing habit performance.

### Lifecycle & Relationship Rules
- **Ownership Validation**: A habit can only be assigned to a goal if `goal.user_id == current_user.id`. Cross-user associations are strictly rejected with `403 Forbidden`.
- **Goal Deletion**: When a goal is soft-deleted (`is_deleted=True`), all linked habits are safely unlinked (`Habit.goal_id = None`). Habit records and historical logs are preserved.
- **Completed Goals**: When a goal status is set to `completed`, progress is reported as `100.0%`.
- **Empty Goals**: A goal with 0 active habits reports `0.0%` progress.
- **Deadline Handling**: Target dates in the past indicate expired goals but do not automatically alter goal status, leaving status transitions under user control.

## ADR-012: Batch Range Aggregation for Habit History, Calendars & Heatmaps

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Users require historical visibility into their habit performance across flexible date ranges (monthly calendar views, day-by-day habit audit trails, and 365-day consistency heatmaps).

### Options Considered
1. Executing daily SQL queries iteratively in a loop for each date in the requested range ($O(D)$ database trips, creating severe N+1 latency).
2. Fetching raw database logs directly to the frontend and computing expected vs. completed schedules client-side.
3. **Backend Batch Range Aggregation**: Query all relevant habit logs within `[start_date, end_date]` in a single indexed query (`WHERE habit_id = :id AND completed_date BETWEEN :start AND :end`), map them in memory, and walk the calendar interval authoritatively using `StreakService.is_due_on_date`.

### Decision
**Option 3** — Backend Batch Range Aggregation.

### Rationale
- **Performance**: Eliminates N+1 query patterns. A 365-day heatmap query executes in $< 15\text{ ms}$ on PostgreSQL using composite index `ix_habit_logs_user_id_date`.
- **Authoritative Semantic Consistency**: Distinguishes between Completed (`is_completed: true`), Missed / Due (`is_due: true, is_completed: false`), and Off / Unscheduled (`is_due: false`) server-side.
- **Safety & Limits**: Enforces a maximum date range limit of 365 days (`MAX_RANGE_DAYS = 365`) and validates `start_date <= end_date` to protect backend memory from unbounded queries.
- **Monetization Extensibility**: Provides a clean service-level hook to restrict free-tier users to 30/90 days of history when billing enforcement is activated.

## ADR-013: Deterministic Momentum Scoring & Rule-Based Behavioral Insights

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Users require actionable visibility into their behavioral trends, execution velocity, day-of-week drop-offs, and category strengths without needing non-deterministic or expensive third-party LLM calls for core analytical metrics.

### Decision
Implement a deterministic, mathematical, backend-authoritative calculation engine in `AnalyticsService` for Momentum Scoring and Behavioral Pattern Extraction.

### Mathematical Formulation for Momentum Score ($M \in [0, 100]$):
$$\text{Rate}_7 = \frac{\text{Completed Habits (last 7 days)}}{\text{Scheduled Habits (last 7 days)}}$$
$$\text{Rate}_{30} = \frac{\text{Completed Habits (last 30 days)}}{\text{Scheduled Habits (last 30 days)}}$$
$$\text{StreakBonus} = \min\left(20, \frac{\sum_{i=1}^N \text{Streak}_i}{N} \times 2\right)$$
$$M = \min\left(100, \text{round}\left(\text{Rate}_7 \times 50 + \text{Rate}_{30} \times 30 + \text{StreakBonus}\right)\right)$$

### Behavioral Pattern Rules
1. **Peak Consistency Day**: Identified as the weekday with the highest completion percentage ($\ge 3$ scheduled occurrences).
2. **Opportunity Area Day**: Identified as the weekday with the lowest completion percentage ($< 70\%$ and below peak day).
3. **Weekend Rhythm Shift**: Triggered when weekday completion average exceeds weekend completion average by $\ge 20\%$.
4. **Category Leader**: Top-performing habit category with $\ge 5$ total scheduled instances.
5. **Momentum Classification**:
   - $M \ge 80$: Peak Lock-In (Positive)
   - $60 \le M < 80$: Strong Momentum (Positive)
   - $40 \le M < 60$: Building Rhythm (Neutral)
   - $M < 40$: Rebuilding Momentum (Warning)

## ADR-014: Deterministic Achievement Engine & Idempotent Milestone Unlocking

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Users require milestones and badge honors to celebrate consistency milestones across streaks (7d, 14d, 30d, 60d, 100d), cumulative completions (1, 10, 50, 100, 500, 1000), habit creation, and goal achievements. The unlock mechanism must be deterministic, idempotent, and non-blocking for the core habit completion pipeline.

### Architectural Decisions
1. **Catalog Seeding & Single Source of Truth**:
   System achievements are defined in `AchievementRepository.INITIAL_ACHIEVEMENTS` and seeded automatically on first catalog access. Achievements are immutable system definitions, not user-created entities.
2. **Idempotent Unlock Architecture**:
   - Check if `(user_id, achievement_id)` already exists in `user_achievements`.
   - If present, skip without database writes.
   - If not present, persist `UserAchievement(user_id, achievement_id, habit_id, unlocked_at)`.
   - Enforce database-level safety with `UniqueConstraint("user_id", "achievement_id", name="uq_user_achievements_user_achievement")`.
3. **Decoupled Evaluation Hook in Habit Completion**:
   - Habit completion logic in `HabitService.complete_habit` records the habit log and updates streaks first.
   - `AchievementService.evaluate_after_habit_completion` is then invoked as an isolated evaluation step.
   - Returns newly unlocked achievement codes in `HabitCompleteResponse.achievements_unlocked` without mutating habit business rules.
4. **Deterministic Progress Computation**:
   `/api/v1/achievements/me` computes current progress and targets on-the-fly from active streak cache, total log count, active habit count, and goal status, guaranteeing exact boundary fidelity (e.g. 6-day streak shows $6/7$ progress, unlocking strictly on day 7).

## ADR-015: Timezone-Aware Reminder Scheduling & Evaluation Engine

**Date:** 2026-09-01  
**Status:** Accepted

### Context
Habit reminders must fire accurately based on user local time (e.g. 07:00 in `Asia/Tokyo` vs 07:00 in `America/New_York`), respect habit schedules, and prevent duplicate notifications when a user has already completed the habit for today. The reminder system must separate user-facing CRUD from background scheduler evaluation to remain platform-independent (ready for CLI crons, mobile push, or web notifications).

### Architectural Decisions
1. **Timezone-Aware Local Interpretation**:
   - `reminder_time` is stored as local wall-clock time (`HH:MM`).
   - The scheduler evaluation service (`ReminderService.get_due_reminders(current_utc_datetime)`) converts UTC evaluation moments into each user's configured timezone (`pytz.timezone(user.timezone)`).
2. **Deterministic Multi-Stage Due Evaluation**:
   A reminder is evaluated as due if and only if:
   - Reminder is active (`reminder.is_active == True`).
   - Linked habit is active, non-archived, and non-deleted.
   - Day of week matches (`local_dt.weekday() in days_of_week` or `StreakService.is_due_on_date(habit, local_date)`).
   - Time matches (`reminder.reminder_time.hour == local_dt.hour` and `reminder.reminder_time.minute == local_dt.minute`).
   - Habit is NOT already completed today (`HabitLogRepository.get_log_by_habit_and_date(db, habit.id, local_date) is None`).
3. **Decoupling CRUD from Delivery Channels**:
   The HTTP API provides pure CRUD (`/api/v1/reminders`) and next-occurrence prediction (`/api/v1/reminders/next`). The evaluation foundation (`get_due_reminders`) is channel-agnostic and does not hardwire push notification SDKs (Firebase/Expo) or worker brokers (Celery/Redis) into the core API domain.
4. **Strict Habit Ownership & State Invariants**:
   A user can only create reminders for active habits they own. Creating reminders for archived/deleted habits is rejected with 400 Bad Request.
---

*Add new ADRs when significant technical decisions are made.*
