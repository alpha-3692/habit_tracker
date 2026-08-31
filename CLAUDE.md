# CLAUDE.md — HabitForge Engineering Rules

> **This file is the primary instruction set for all AI agents working on this codebase.**
> Read this file completely before making any changes. If in doubt, ask.

---

## 1. INSPECT BEFORE YOU MODIFY

**Before changing any file:**
1. Read the file in full.
2. Understand what it currently does.
3. Identify what other files depend on it.
4. Make only the changes required.

Do NOT rewrite an entire file when a targeted edit is sufficient.
Do NOT modify code unrelated to the current task.

---

## 2. ARCHITECTURE RULES

### Backend is the Source of Truth
- All business logic lives in the backend (FastAPI/Python).
- The frontend (Next.js) is a presentation layer only.
- The frontend must NEVER perform authoritative calculations for:
  - streaks
  - completion rates
  - analytics
  - subscription status
  - achievement unlocks
  - consistency scores

### API-First, Platform-Independent
- The backend must never assume a browser, web session, or DOM.
- The API must be usable by web clients, mobile apps, and CLI tools equally.
- Do NOT use browser-specific concepts in backend design.
- API responses must be structured JSON — always.

### Versioning
- All API endpoints are versioned under `/api/v1/`.
- Never break an existing endpoint without a migration plan.
- When adding new fields to responses, use additive changes.
- Deprecation must be documented in `docs/API.md`.

---

## 3. SECURITY RULES

### Secrets
- Never hardcode secrets, API keys, or passwords in source code.
- Use environment variables. See `.env.example` for all required variables.
- Never commit `.env` files (they are in `.gitignore`).
- The Claude/Anthropic API key must NEVER be exposed to the frontend.
- The database URL must NEVER be exposed to the frontend.

### Authentication & Authorization
- Every protected endpoint must verify the JWT token.
- Every data-modifying endpoint must verify that the authenticated user **owns** the resource.
- Use `get_current_user` dependency on all protected routes.
- Ownership checks must be performed in the service layer, not just the router.

### Input Validation
- All request bodies must have Pydantic schemas.
- Never trust client-supplied IDs without verifying ownership.
- Validate all enum values, date formats, and string lengths.

### Passwords
- Use `passlib` with `bcrypt` for password hashing.
- Never log or return plaintext passwords.
- Never store plaintext passwords.

---

## 4. DATABASE RULES

### Migrations
- **Always** use Alembic for schema changes.
- Never modify the database schema directly with raw SQL in production.
- Every schema change requires a migration file:
  ```bash
  cd backend
  alembic revision --autogenerate -m "description_of_change"
  alembic upgrade head
  ```
- Migration files must be committed to version control.

### Models
- All SQLAlchemy models are in `backend/app/models/`.
- Every model must have `created_at` and `updated_at` timestamps.
- Use proper foreign keys and indexes.
- Use `CASCADE` deletes carefully — document intent.

### Naming Conventions
- Table names: `snake_case`, plural (e.g., `habit_logs`, `user_achievements`)
- Column names: `snake_case`
- Index names: `ix_<table>_<column>`
- Foreign key names: `fk_<table>_<referenced_table>_<column>`

---

## 5. CODE ORGANIZATION

### Backend Structure
```
backend/
├── app/
│   ├── api/v1/          # Route handlers (thin — delegate to services)
│   ├── core/            # Config, security, dependencies
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic (the real work happens here)
│   ├── repositories/    # Database query layer
│   └── utils/           # Pure utility functions
├── alembic/             # Database migrations
├── tests/               # All tests mirror app/ structure
└── main.py
```

### Frontend Structure
```
frontend/
├── src/
│   ├── app/             # Next.js App Router pages
│   ├── components/      # Reusable UI components
│   ├── lib/             # API client, utilities
│   ├── hooks/           # React hooks
│   ├── store/           # State management
│   ├── types/           # TypeScript interfaces
│   └── styles/          # Global styles
```

### Route Handler Rules (Backend)
- Routers should be thin — they validate input and delegate to services.
- Business logic must NOT live in route handlers.
- Return consistent response schemas.

### Service Layer Rules (Backend)
- Services contain all business logic.
- Services call repositories for data access.
- Services must not import from `api/` layer.
- Services must not directly use `Request` or `Response` objects.

---

## 6. DEPENDENCY RULES

- Do NOT add a new dependency unless it is clearly necessary.
- Check if existing dependencies already solve the problem.
- All Python dependencies go in `backend/requirements.txt`.
- All Node dependencies go in `frontend/package.json`.
- Document why a major dependency was added in `docs/DECISIONS.md`.

---

## 7. TESTING RULES

### Run Tests After Changes
After any meaningful change, run:
```bash
# Backend
cd backend && python -m pytest tests/ -v

# Frontend
cd frontend && npm test
```

### What Must Be Tested
- User registration and login
- JWT token generation and validation
- Ownership and authorization checks
- Habit creation, update, deletion
- Habit completion (including duplicate prevention)
- Streak calculation logic
- Goal creation and association with habits
- Analytics calculations
- Subscription status checks

### Test Structure
- Backend tests: `backend/tests/` mirroring `app/` structure
- Unit tests: test individual service functions
- Integration tests: test full API flows with a test database

---

## 8. AI INTEGRATION RULES

- AI features are enhancements, not core dependencies.
- The core habit tracking system must work without AI.
- All AI calls go through `backend/app/services/ai_service.py`.
- Never call the Claude API from the frontend.
- Never send more user data to the AI than is necessary.
- AI-generated recommendations must be validated before applying data changes.
- Rate limit AI endpoints.

---

## 9. ERROR HANDLING RULES

- Never return raw Python exceptions or stack traces to API clients.
- Use custom exception classes in `backend/app/core/exceptions.py`.
- Return structured error responses:
  ```json
  {
    "error": {
      "code": "HABIT_NOT_FOUND",
      "message": "The requested habit was not found.",
      "details": {}
    }
  }
  ```
- Log the full error internally. Return a safe message externally.
- Use appropriate HTTP status codes (400, 401, 403, 404, 409, 422, 500).

---

## 10. LOGGING RULES

- Use structured logging (JSON format in production).
- Log: request ID, user ID (not PII), action, outcome.
- Never log: passwords, tokens, API keys, full request bodies with sensitive data.
- Log level: DEBUG in development, INFO in production.

---

## 11. FRONTEND RULES

- No business logic in React components.
- API calls go through `frontend/src/lib/api/` client modules only.
- Use TypeScript — no `any` types without justification.
- All API response types must be in `frontend/src/types/`.
- Protected pages must redirect unauthenticated users to `/login`.
- Use environment variables for all URLs — never hardcode `localhost:8000`.

---

## 12. DOCUMENTATION RULES

After any significant change, update the relevant document in `docs/`:
- New endpoint → update `docs/API.md`
- Schema change → update `docs/DATABASE.md`
- Architecture change → update `docs/ARCHITECTURE.md`
- Security change → update `docs/SECURITY.md`
- New technology → update `docs/DECISIONS.md`

---

## 13. MOBILE COMPATIBILITY

Always ask: "Can a mobile client use this API?"
- Response bodies must be self-contained JSON.
- Do not rely on cookies for auth — use Bearer tokens.
- Pagination must be cursor or offset-based (not DOM-dependent).
- Never return HTML in API responses.

---

## 14. SUBSCRIPTIONS

- Subscription status is determined by the backend.
- The frontend must never control feature access based on its own subscription logic.
- Check `user.subscription_tier` from the API on every protected feature access.
- Free tier limits are enforced server-side.

---

## 15. GIT COMMIT RULES

- Write descriptive commit messages.
- Format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Example: `feat(habits): add streak calculation service`
- Never commit directly to `main` for significant changes — use feature branches.

---

*Last updated: 2026-09-01*
*Maintainer: HabitForge Engineering*
