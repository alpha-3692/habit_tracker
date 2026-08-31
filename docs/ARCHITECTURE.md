# HabitForge — Architecture Document

**Version:** 0.1.0  
**Status:** Active  
**Last Updated:** 2026-09-01

---

## 1. Architecture Overview

HabitForge uses a clean, layered architecture with a strict separation between the API client, REST API, and backend services.

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│                                                         │
│   Next.js Web App          Future Mobile Apps           │
│   (TypeScript + Tailwind)  (Android / iOS)              │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS / REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   API GATEWAY LAYER                      │
│                                                         │
│   FastAPI — /api/v1/*                                   │
│   - Authentication middleware (JWT)                     │
│   - Request validation (Pydantic)                       │
│   - Rate limiting (future)                              │
│   - CORS                                                │
│   - Logging                                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  SERVICE LAYER (Business Logic)          │
│                                                         │
│   AuthService     HabitService     GoalService          │
│   StreakService   AnalyticsService AchievementService   │
│   AIService       SubscriptionService                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 REPOSITORY LAYER (Data Access)           │
│                                                         │
│   UserRepository  HabitRepository  GoalRepository       │
│   HabitLogRepository  AchievementRepository             │
└────────────────────┬────────────────────────────────────┘
                     │ SQLAlchemy ORM
                     ▼
┌─────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                       │
│                                                         │
│            PostgreSQL (via Alembic migrations)           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 15.x | React framework with App Router |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Utility-first styling |
| React Query (TanStack) | 5.x | Server state management |
| Zustand | 4.x | Client state management |
| React Hook Form | 7.x | Form handling |
| Zod | 3.x | Schema validation (client) |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.111+ | Web framework |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | Database migrations |
| Pydantic | 2.x | Data validation |
| passlib + bcrypt | — | Password hashing |
| python-jose | — | JWT handling |
| httpx | — | Async HTTP (AI calls) |

### Database
| Technology | Purpose |
|-----------|---------|
| PostgreSQL 15+ | Primary relational database |

### AI
| Technology | Purpose |
|-----------|---------|
| Anthropic Claude API | AI coaching, habit suggestions, reviews |

### Infrastructure (Future)
| Technology | Purpose |
|-----------|---------|
| Docker | Containerization |
| Docker Compose | Local development |
| Cloud hosting | TBD (provider-agnostic) |

---

## 3. Project Structure

```
habit_tracker/                    # Monorepo root
├── .env.example                  # Environment variable template
├── .gitignore
├── CLAUDE.md                     # AI agent engineering rules
├── README.md
├── docs/                         # Source of truth documentation
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API.md
│   ├── UI_UX.md
│   ├── SECURITY.md
│   ├── TESTING.md
│   ├── ROADMAP.md
│   └── DECISIONS.md
├── backend/                      # FastAPI Python application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app factory
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py     # Aggregate all v1 routes
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── users.py
│   │   │           ├── goals.py
│   │   │           ├── habits.py
│   │   │           ├── dashboard.py
│   │   │           ├── analytics.py
│   │   │           ├── achievements.py
│   │   │           ├── ai.py
│   │   │           └── subscriptions.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Settings (pydantic-settings)
│   │   │   ├── database.py       # DB session factory
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   ├── dependencies.py   # FastAPI Depends (get_current_user, etc.)
│   │   │   └── exceptions.py     # Custom exception classes
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   ├── habit.py
│   │   │   ├── habit_log.py
│   │   │   ├── reminder.py
│   │   │   ├── achievement.py
│   │   │   └── subscription.py
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   ├── habit.py
│   │   │   ├── habit_log.py
│   │   │   ├── analytics.py
│   │   │   ├── achievement.py
│   │   │   └── subscription.py
│   │   ├── services/             # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── goal_service.py
│   │   │   ├── habit_service.py
│   │   │   ├── streak_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── achievement_service.py
│   │   │   ├── ai_service.py
│   │   │   └── subscription_service.py
│   │   ├── repositories/         # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── user_repository.py
│   │   │   ├── goal_repository.py
│   │   │   ├── habit_repository.py
│   │   │   └── habit_log_repository.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── datetime_utils.py
│   │       └── pagination.py
│   ├── alembic/                  # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_habits.py
│   │   ├── test_goals.py
│   │   ├── test_streaks.py
│   │   └── test_analytics.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env                      # NOT committed (in .gitignore)
└── frontend/                     # Next.js application
    ├── src/
    │   ├── app/                  # Next.js App Router
    │   │   ├── layout.tsx        # Root layout
    │   │   ├── page.tsx          # Landing page (/)
    │   │   ├── (public)/
    │   │   │   ├── features/
    │   │   │   ├── pricing/
    │   │   │   ├── about/
    │   │   │   ├── login/
    │   │   │   └── signup/
    │   │   └── (app)/            # Authenticated area
    │   │       ├── layout.tsx    # App shell layout
    │   │       ├── dashboard/
    │   │       ├── habits/
    │   │       ├── goals/
    │   │       ├── calendar/
    │   │       ├── analytics/
    │   │       ├── achievements/
    │   │       ├── ai-coach/
    │   │       └── settings/
    │   ├── components/
    │   │   ├── ui/               # Base UI components
    │   │   ├── habits/
    │   │   ├── goals/
    │   │   ├── dashboard/
    │   │   ├── analytics/
    │   │   └── layout/
    │   ├── lib/
    │   │   ├── api/              # API client modules
    │   │   │   ├── client.ts     # Base API client
    │   │   │   ├── auth.ts
    │   │   │   ├── habits.ts
    │   │   │   ├── goals.ts
    │   │   │   └── analytics.ts
    │   │   └── utils.ts
    │   ├── hooks/                # React hooks
    │   ├── store/                # Zustand stores
    │   ├── types/                # TypeScript interfaces (mirror API schemas)
    │   └── styles/
    ├── public/
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.ts
    └── .env.local                # NOT committed
```

---

## 4. Authentication Flow

```
Client                    Backend                   Database
  │                          │                          │
  │  POST /auth/register     │                          │
  │─────────────────────────>│                          │
  │                          │  Validate + Hash PW      │
  │                          │──────────────────────────>
  │                          │  INSERT user             │
  │                          │<──────────────────────────
  │  {access_token, user}    │                          │
  │<─────────────────────────│                          │
  │                          │                          │
  │  POST /auth/login        │                          │
  │─────────────────────────>│                          │
  │                          │  Verify PW hash          │
  │                          │  Generate JWT            │
  │  {access_token, ...}     │                          │
  │<─────────────────────────│                          │
  │                          │                          │
  │  GET /habits             │                          │
  │  Authorization: Bearer   │                          │
  │─────────────────────────>│                          │
  │                          │  Verify JWT              │
  │                          │  Extract user_id         │
  │                          │  Query user's habits     │
  │  {habits: [...]}         │                          │
  │<─────────────────────────│                          │
```

---

## 5. Habit Completion Flow

```
Client                    Backend                   Database
  │                          │                          │
  │  POST /habits/{id}/      │                          │
  │  complete                │                          │
  │─────────────────────────>│                          │
  │                          │  1. Authenticate user    │
  │                          │  2. Verify ownership     │
  │                          │  3. Validate habit       │
  │                          │  4. Check duplicate      │
  │                          │  5. Create habit_log     │
  │                          │──────────────────────────>
  │                          │  6. Calculate streak     │
  │                          │  7. Update achievements  │
  │                          │<──────────────────────────
  │  {log, streak, ...}      │                          │
  │<─────────────────────────│                          │
```

---

## 6. Key Architectural Decisions

See `docs/DECISIONS.md` for full rationale. Summary:

1. **Monorepo** — Single repository for web + backend simplifies development at this stage.
2. **REST over GraphQL** — Simpler, better mobile compatibility, easier API docs, sufficient for use case.
3. **PostgreSQL** — ACID compliance, complex queries for analytics, excellent JSON support.
4. **JWT with refresh tokens** — Stateless auth enables mobile clients; refresh tokens extend sessions.
5. **Repository pattern** — Decouples business logic from data access, simplifies testing.
6. **No ORM in service layer** — Services call repositories; repositories use SQLAlchemy. Keeps business logic database-agnostic.
7. **Next.js App Router** — Server components for performance, client components where interactivity is needed.

---

## 7. Scalability Considerations

Current design is appropriate for MVP. Future scaling paths:
- Add Redis for session storage and caching
- Add background job queue (Celery/Bull) for AI processing
- Add CDN for static assets
- Horizontal API scaling (stateless JWT design already supports this)
- Read replicas for analytics queries

These are NOT implemented in MVP to avoid premature complexity.

---

*Update this document when architecture changes.*
