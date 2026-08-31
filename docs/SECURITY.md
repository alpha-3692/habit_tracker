# HabitForge — Security Specification

**Version:** 0.1.0  
**Last Updated:** 2026-09-01

---

## 1. Authentication

### Password Handling
- Passwords are hashed using **bcrypt** (via `passlib`) with a cost factor of 12.
- Plaintext passwords are never stored, logged, or returned in API responses.
- Minimum password requirements: 8 characters (enforce server-side with Pydantic).

### JWT Tokens
- **Access Token:** Short-lived (default: 30 minutes), signed with HS256.
- **Refresh Token:** Longer-lived (default: 30 days), used only to get new access tokens.
- Secret key must be at least 64 bytes, randomly generated, stored in environment variable `SECRET_KEY`.
- Tokens are never stored in localStorage on the frontend (use httpOnly cookies or memory).
- Tokens must be included in `Authorization: Bearer <token>` header.

### Token Security
```python
# Generate a secure secret key
import secrets
secrets.token_hex(64)
```

---

## 2. Authorization

### Ownership Verification
**Every** API endpoint that operates on a resource (habit, goal, log) must verify:
1. The user is authenticated (valid JWT).
2. The resource exists.
3. The user OWNS the resource (user_id matches).

Failure modes:
- Missing token → `401 Unauthorized`
- Valid token, resource belongs to different user → `403 Forbidden` (never `404`)

### Implementation Pattern
```python
# In every service method that accesses user-owned resources:
async def get_habit(habit_id: UUID, current_user: User, db: Session):
    habit = db.get(Habit, habit_id)
    if not habit or habit.is_deleted:
        raise HabitNotFoundException()
    if habit.user_id != current_user.id:
        raise ForbiddenException()  # Do NOT expose that the resource exists
    return habit
```

---

## 3. API Security

### CORS
Configure CORS to only allow requests from known frontend origins.

```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
# Development: ["http://localhost:3000"]
# Production: ["https://habitforge.app"]
```

### Input Validation
- All request bodies validated with Pydantic schemas.
- Reject unexpected fields (use `model_config = ConfigDict(extra='forbid')`).
- Validate string lengths, enum values, date ranges.
- Sanitize text inputs to prevent XSS in stored content.

### Rate Limiting (Architecture Ready)
- Implement per-IP and per-user rate limits on authentication endpoints.
- AI endpoints must have stricter rate limits.
- Use middleware approach so it can be enabled/configured via environment.

### SQL Injection Protection
- Never use raw SQL string interpolation.
- All queries use SQLAlchemy ORM or parameterized queries.
- SQLAlchemy handles escaping automatically.

---

## 4. Secrets Management

### Rules
- All secrets in environment variables. Never in source code.
- `.env` file in `.gitignore`. Use `.env.example` with placeholder values.
- Do NOT log environment variables or configuration values.
- AI API key (`ANTHROPIC_API_KEY`) only accessible in backend services.
- Database URL only accessible in backend.
- Frontend only receives `NEXT_PUBLIC_*` prefixed variables (these are public by design).

### Required Secrets
| Variable | Location | Notes |
|---------|----------|-------|
| `SECRET_KEY` | Backend | JWT signing key, 64+ bytes |
| `DATABASE_URL` | Backend | Never in frontend |
| `ANTHROPIC_API_KEY` | Backend | Never in frontend |
| `GOOGLE_CLIENT_SECRET` | Backend | Future OAuth |

---

## 5. Error Handling

### External Error Responses
Never expose:
- Stack traces
- Internal error messages
- SQL errors
- File paths
- Library names and versions
- User existence (use consistent responses for login failures)

```python
# Good
{"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}

# Bad
{"error": "User with email user@example.com not found in database"}
```

### Internal Logging
Log the full error internally including:
- Request ID
- User ID (if authenticated)
- Error type and message
- Stack trace
- Timestamp

---

## 6. Data Privacy

### Minimum Data Collection
- Only collect data necessary for the product to function.
- Do not send unnecessary personal data to third parties (including AI providers).

### AI Data Minimization
When calling the Claude API:
- Send aggregated statistics, NOT raw habit logs with personal details.
- Do NOT send email addresses, full names, or other PII to the AI.
- Example: Send `{"habit": "Exercise", "completion_rate": 65, "streak": 3}` not the full user object.

### Data Retention
- Habit logs are user data — provide data export capability.
- On account deletion: soft delete user, schedule hard delete after 30 days (grace period).

---

## 7. Frontend Security

### XSS Prevention
- Next.js escapes React JSX output by default — do not use `dangerouslySetInnerHTML` unless absolutely necessary.
- Sanitize any user-provided content rendered as HTML.

### Token Storage
- Prefer httpOnly cookies for refresh tokens (not accessible to JavaScript).
- Access tokens can be stored in memory (React state/Zustand store) for single session.
- Avoid localStorage for sensitive tokens.

### CSRF Protection
- Use SameSite=Strict or SameSite=Lax cookie attributes.
- Include CSRF token if using cookie-based session auth.

---

## 8. Database Security

### Connection Security
- Use SSL for database connections in production.
- Database user should have minimum required permissions (no SUPERUSER).
- Connection pooling with appropriate limits.

### Data at Rest
- Managed PostgreSQL services typically encrypt at rest — use a managed service in production.

---

## 9. Security Checklist (Per Feature)

When implementing any new feature, verify:

- [ ] Endpoint requires authentication (unless explicitly public)
- [ ] Resource ownership is verified before read/write
- [ ] Input is validated with Pydantic schema
- [ ] No secrets in code or logs
- [ ] Error messages are safe for external exposure
- [ ] No PII sent to AI providers unnecessarily
- [ ] Rate limiting considered for high-risk endpoints
- [ ] Tests include authorization and ownership test cases

---

*Update this document when security controls change.*
