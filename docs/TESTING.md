# HabitForge — Testing Strategy

**Version:** 0.1.0  
**Last Updated:** 2026-09-01

---

## 1. Testing Philosophy

- Test business logic thoroughly, not implementation details.
- Every security-critical path must have tests.
- Tests should run fast and be runnable in CI without external dependencies.
- Use a test database (SQLite in memory or test PostgreSQL schema).

---

## 2. Backend Testing

### Framework
- **pytest** — Test runner
- **pytest-asyncio** — Async test support
- **httpx** — For API integration tests
- **factory-boy** — Test data factories
- **pytest-cov** — Coverage reporting

### Test Structure
```
backend/tests/
├── conftest.py           # Shared fixtures (test DB, test client, test user)
├── unit/
│   ├── test_streak_service.py
│   ├── test_analytics_service.py
│   └── test_security.py
├── integration/
│   ├── test_auth.py
│   ├── test_habits.py
│   ├── test_goals.py
│   └── test_dashboard.py
└── factories/
    ├── user_factory.py
    ├── habit_factory.py
    └── goal_factory.py
```

### Running Tests
```bash
cd backend

# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=app --cov-report=html

# Specific file
python -m pytest tests/integration/test_habits.py -v

# Specific test
python -m pytest tests/integration/test_habits.py::test_habit_completion_creates_log -v
```

---

## 3. Critical Test Cases

### 3.1 Authentication
```
✅ test_register_new_user_returns_tokens
✅ test_register_duplicate_email_returns_409
✅ test_login_valid_credentials_returns_tokens
✅ test_login_invalid_password_returns_401
✅ test_login_nonexistent_email_returns_401
✅ test_refresh_token_returns_new_access_token
✅ test_invalid_refresh_token_returns_401
✅ test_expired_access_token_returns_401
✅ test_protected_route_without_token_returns_401
```

### 3.2 Authorization (Ownership)
```
✅ test_user_cannot_access_other_users_habits
✅ test_user_cannot_complete_other_users_habit
✅ test_user_cannot_edit_other_users_goal
✅ test_user_cannot_delete_other_users_habit_log
✅ test_forbidden_returns_403_not_404
```

### 3.3 Habit Management
```
✅ test_create_habit_succeeds
✅ test_create_habit_requires_auth
✅ test_free_user_cannot_exceed_habit_limit
✅ test_pro_user_can_create_unlimited_habits
✅ test_edit_habit_updates_correctly
✅ test_archive_habit_removes_from_active
✅ test_delete_habit_soft_deletes
✅ test_deleted_habit_not_returned_in_list
```

### 3.4 Habit Completion
```
✅ test_complete_habit_creates_log
✅ test_complete_habit_returns_updated_streak
✅ test_complete_habit_twice_same_day_returns_409
✅ test_complete_habit_for_future_date_returns_400
✅ test_undo_completion_removes_log
✅ test_complete_nonexistent_habit_returns_404
✅ test_complete_archived_habit_returns_400
```

### 3.5 Streak Calculation
```
✅ test_first_completion_gives_streak_of_1
✅ test_consecutive_completions_increment_streak
✅ test_missed_day_resets_streak_to_0
✅ test_non_habit_day_does_not_break_streak
✅ test_best_streak_updates_when_current_exceeds
✅ test_streak_calculation_respects_timezone
✅ test_streak_calculated_from_logs_not_counter
```

### 3.6 Goal Management
```
✅ test_create_goal_succeeds
✅ test_associate_habit_with_goal
✅ test_goal_progress_derived_from_habits
✅ test_delete_goal_soft_deletes
```

### 3.7 Analytics
```
✅ test_completion_rate_calculated_correctly
✅ test_analytics_only_includes_owned_habits
✅ test_calendar_data_correct_for_period
```

### 3.8 Free Tier Enforcement
```
✅ test_free_user_habit_limit_enforced
✅ test_free_user_ai_features_blocked
✅ test_pro_user_all_features_accessible
```

---

## 4. Frontend Testing

### Framework
- **Jest** — Unit test runner
- **React Testing Library** — Component tests
- **Playwright** or **Cypress** — E2E tests (Phase 2)

### What to Test
- Form validation (client-side)
- Auth redirect behavior
- API client error handling
- Key component rendering

### Running Tests
```bash
cd frontend
npm test                    # Unit tests
npm run test:e2e            # E2E tests (when configured)
```

---

## 5. Test Database Setup

```python
# backend/tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.main import app
from httpx import AsyncClient

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
async def client(test_engine):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers(client):
    # Register and login a test user, return headers
    ...
```

---

## 6. Coverage Targets

| Layer | Target |
|-------|--------|
| Services (business logic) | > 85% |
| API endpoints | > 80% |
| Security paths | 100% |
| Frontend components | > 60% |

---

## 7. CI Integration (Future)

When CI is set up:
1. Run all backend tests on every PR
2. Fail PR if coverage drops below threshold
3. Run frontend tests on every PR
4. Deploy only if all tests pass

---

*Add new test cases here when new features are implemented.*
