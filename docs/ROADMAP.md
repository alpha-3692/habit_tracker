# HabitForge — Project Roadmap

**Version:** 0.1.0  
**Last Updated:** 2026-09-01

---

## Milestone 0: Foundation ← CURRENT
**Goal:** Professional project structure, documentation, and tooling.

- [x] Git repository initialized
- [x] .gitignore and .env.example created
- [x] CLAUDE.md engineering rules
- [x] Documentation (PRD, ARCHITECTURE, DATABASE, API, UI/UX, SECURITY, TESTING)
- [ ] Backend project scaffold (FastAPI, SQLAlchemy, Alembic)
- [ ] Frontend project scaffold (Next.js, TypeScript, Tailwind)
- [ ] Initial database models
- [ ] Alembic migration setup
- [ ] Development environment working

---

## Milestone 1: Authentication
**Goal:** Secure user registration, login, and token management.

- [ ] User model and migration
- [ ] Password hashing with bcrypt
- [ ] JWT access + refresh token system
- [ ] POST /auth/register
- [ ] POST /auth/login
- [ ] POST /auth/refresh
- [ ] POST /auth/logout
- [ ] GET /users/me
- [ ] Protected route middleware
- [ ] Auth tests (registration, login, token validation)
- [ ] Frontend: Login page
- [ ] Frontend: Signup page
- [ ] Frontend: Auth state management
- [ ] Frontend: Protected route wrapper

---

## Milestone 2: Habits (Core)
**Goal:** Full habit CRUD with completion tracking.

- [ ] Habit model and migration
- [ ] Habit CRUD endpoints (GET, POST, PATCH, DELETE)
- [ ] Habit archive endpoint
- [ ] Habit completion endpoint (POST /habits/{id}/complete)
- [ ] Duplicate completion prevention
- [ ] Streak calculation service (derived from habit_logs)
- [ ] Free tier habit limit enforcement
- [ ] Habit tests (CRUD, completion, authorization)
- [ ] Streak tests (consecutive, missed days, frequency)
- [ ] Frontend: Habits list page
- [ ] Frontend: Create/edit habit form
- [ ] Frontend: Habit completion toggle

---

## Milestone 3: Dashboard
**Goal:** Functional daily dashboard.

- [ ] GET /dashboard endpoint
- [ ] Today's habits with completion status
- [ ] Daily progress calculation
- [ ] Streak display
- [ ] Frontend: Dashboard page
- [ ] Frontend: Today's habit list
- [ ] Frontend: Progress ring/bar
- [ ] Dashboard tests

---

## Milestone 4: Goals
**Goal:** Goal management with habit associations.

- [ ] Goal model and migration
- [ ] Goal CRUD endpoints
- [ ] Associate habits with goals
- [ ] Goal progress calculation
- [ ] Frontend: Goals page
- [ ] Frontend: Goal detail page
- [ ] Goal tests

---

## Milestone 5: Onboarding
**Goal:** Guided new user experience.

- [ ] Onboarding wizard (multi-step)
- [ ] Category selection
- [ ] Goal setup in onboarding
- [ ] Habit selection/creation in onboarding
- [ ] Mark onboarding as complete
- [ ] Redirect after first login
- [ ] Onboarding tests

---

## Milestone 6: Calendar & Analytics
**Goal:** Historical data visualization.

- [ ] GET /analytics/habits/{id} endpoint
- [ ] GET /analytics/calendar endpoint
- [ ] Frontend: Calendar page
- [ ] Frontend: Analytics page with charts
- [ ] Analytics tests

---

## Milestone 7: Achievements
**Goal:** Achievement system architecture and MVP achievements.

- [ ] Achievement and user_achievement models
- [ ] Achievement checking after habit completion
- [ ] GET /achievements endpoints
- [ ] Seed initial achievements
- [ ] Frontend: Achievements page
- [ ] Achievement tests

---

## Milestone 8: AI Features
**Goal:** AI habit suggestions and basic coaching.

- [ ] AI service with Claude API integration
- [ ] POST /ai/suggest-habits endpoint
- [ ] POST /ai/coach endpoint (Pro only)
- [ ] GET /ai/weekly-review endpoint (Pro only)
- [ ] Data minimization (send stats, not PII)
- [ ] AI rate limiting
- [ ] Frontend: AI habit suggestions in onboarding
- [ ] Frontend: AI Coach page (Pro)

---

## Milestone 9: Subscriptions
**Goal:** Subscription model and feature gating.

- [ ] Subscription model and migration
- [ ] Subscription status API
- [ ] Feature gating middleware
- [ ] Payment provider integration (TBD)
- [ ] Frontend: Pricing page
- [ ] Frontend: Upgrade flow
- [ ] Subscription tests

---

## Milestone 10: Polish & Launch Prep
**Goal:** Quality, performance, and production readiness.

- [ ] Landing page (public marketing site)
- [ ] Settings page
- [ ] Performance audit
- [ ] Accessibility audit
- [ ] Security review
- [ ] Full test suite passing
- [ ] API documentation (auto-generated from FastAPI)
- [ ] Deployment configuration
- [ ] Monitoring setup

---

## Future Milestones (Post-Launch)

### Mobile Apps
- [ ] React Native app or Native Android/iOS
- [ ] Push notifications
- [ ] Offline support

### Advanced Analytics
- [ ] Consistency score algorithm
- [ ] Failure pattern detection
- [ ] Best completion time analysis
- [ ] Weekly comparisons

### Social Features
- [ ] Habit challenges
- [ ] Friend accountability

### Integrations
- [ ] Fitness tracker integrations
- [ ] Calendar sync

---

*Milestones are completed sequentially. Do not start Milestone N+1 until Milestone N is stable and tested.*
