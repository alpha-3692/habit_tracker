# HabitForge — Product Requirements Document (PRD)

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-09-01  
**Author:** HabitForge Product Team

---

## 1. Executive Summary

HabitForge is an AI-powered consistency coach that helps users turn goals into sustainable daily habits, understand their behavior, and improve consistency over time.

This is NOT another basic checkbox habit tracker. HabitForge differentiates through behavioral intelligence, AI-driven coaching, and a feedback loop that improves user consistency rather than just recording it.

### North Star Metric
**Weekly Active Users who complete at least 3 habits.**

### Core Product Loop
```
Goal → Habits → Daily Execution → Tracking → Analytics → Behavioral Insights → Recovery → Improved Consistency
```

---

## 2. Problem Statement

Most people who want to build habits fail within the first 30 days. Existing apps either:
- Are too simple (checklist apps with no intelligence)
- Are too gamified (feel juvenile for professional users)
- Lack insight (track but don't explain *why* you're failing)
- Don't recover well (miss one day, lose all motivation)

HabitForge solves this by combining rigorous tracking with AI-powered behavioral analysis in a professional, premium interface.

---

## 3. Target Users

### Primary Persona: The Ambitious Professional
- Age: 22–40
- Goals: Career growth, fitness, learning, personal development
- Pain: Starts habits, loses momentum, doesn't understand why
- Need: A serious tool that respects their intelligence

### Secondary Persona: The Student Builder
- Age: 18–26
- Goals: Academic performance, coding skills, consistency
- Pain: Procrastination, inconsistent study habits, no feedback loop
- Need: Structure + insight without feeling like a game for children

---

## 4. Platform Strategy

**Phase 1 (Current):** Web Application (Next.js)  
**Phase 2 (Future):** Android App  
**Phase 3 (Future):** iOS App  

The backend is designed as a platform-independent API. All clients share the same backend, database, authentication, and business logic.

---

## 5. MVP Feature Set

### 5.1 Authentication
| Feature | Priority | Notes |
|---------|----------|-------|
| Sign up (email + password) | P0 | bcrypt password hashing |
| Login | P0 | JWT access + refresh tokens |
| Logout | P0 | Token invalidation |
| Protected routes | P0 | JWT middleware |
| Password reset (email flow) | P1 | Architecture ready, email optional for MVP |
| Google OAuth | P2 | Architecture prepared, implementation deferred |

### 5.2 Onboarding
| Feature | Priority | Notes |
|---------|----------|-------|
| Category selection | P0 | Fitness, Study, Coding, Reading, Sleep, Productivity, Career, Personal Growth, Other |
| Goal setup wizard | P0 | Name, description, deadline, category |
| AI habit suggestions | P1 | Based on goal description |
| Habit selection from suggestions | P1 | |
| Schedule/preference setup | P0 | Frequency, reminder time |

### 5.3 Goals
| Feature | Priority | Notes |
|---------|----------|-------|
| Create goal | P0 | |
| Edit goal | P0 | |
| Delete goal | P0 | Soft delete |
| Set deadline | P0 | |
| Associate habits with goal | P0 | |
| View goal progress | P0 | Derived from associated habits |

### 5.4 Habits
| Feature | Priority | Notes |
|---------|----------|-------|
| Create habit | P0 | |
| Edit habit | P0 | |
| Archive habit | P0 | Soft archive |
| Delete habit | P0 | |
| Set frequency | P0 | Daily, specific days, weekdays, weekends |
| Set target + unit | P0 | "2 problems", "60 minutes", "10 pages" |
| Set category | P0 | |
| Set start date | P0 | |
| Configure reminders | P1 | Time-based reminders |
| Mark habit complete | P0 | With optional notes/quantity |
| Track historical progress | P0 | |

### 5.5 Habit Completion & Streaks
| Feature | Priority | Notes |
|---------|----------|-------|
| Complete habit (POST) | P0 | Backend validates and records |
| Streak calculation (backend) | P0 | Cannot be gamed by client |
| Current streak | P0 | |
| Best streak | P0 | |
| Total completions | P0 | |
| Completion percentage | P0 | |
| Duplicate completion prevention | P0 | |
| Timezone awareness | P0 | |

### 5.6 Dashboard
| Feature | Priority | Notes |
|---------|----------|-------|
| Daily greeting | P0 | |
| Today's progress (%) | P0 | |
| Today's habits list | P0 | With completion toggles |
| Current streak display | P0 | |
| Goals summary | P0 | |
| Quick actions | P0 | |
| Weekly progress summary | P1 | |

### 5.7 Calendar View
| Feature | Priority | Notes |
|---------|----------|-------|
| Monthly calendar | P0 | Completed/missed day indicators |
| Habit-specific calendar | P0 | |
| Streak visualization | P1 | |

### 5.8 Analytics
| Feature | Priority | Notes |
|---------|----------|-------|
| Per-habit completion rate | P0 | |
| Per-habit streak stats | P0 | |
| Per-habit completion history | P0 | |
| Overall consistency score | P1 | Backend calculated |
| Weekly comparison | P2 | |
| Best completion times | P2 | |
| Weakest days analysis | P2 | |

### 5.9 Achievements
| Feature | Priority | Notes |
|---------|----------|-------|
| Achievement data model | P0 | Ready for MVP |
| First Habit achievement | P1 | |
| 7-day streak achievement | P1 | |
| 30-day streak achievement | P1 | |
| 100 completions achievement | P1 | |
| Achievement display | P1 | |

### 5.10 AI Features
| Feature | Priority | Notes |
|---------|----------|-------|
| AI habit suggestions (onboarding) | P1 | Claude API via backend |
| AI coach chat | P2 | Context-aware, structured data |
| Weekly AI review | P2 | Automated behavioral summary |
| Failure pattern analysis | P3 | Long-term data required |

### 5.11 Settings
| Feature | Priority | Notes |
|---------|----------|-------|
| Profile management | P0 | |
| Notification preferences | P1 | |
| Timezone setting | P0 | |
| Account deletion | P1 | |
| Export data | P2 | |

---

## 6. Monetization Model

### Free Tier
- Up to 5 active habits
- Basic tracking and streaks
- Calendar view (30 days history)
- Basic analytics

### Pro Tier
- Unlimited habits
- Full analytics history
- AI Coach
- AI Weekly Review
- Behavioral insights
- Advanced history
- Priority support

### Subscription States
`free` | `trial` | `pro_active` | `pro_cancelled` | `pro_expired`

---

## 7. Non-Goals (MVP)

- Social features / sharing
- Habit challenges with other users
- Push notifications (mobile)
- Offline mode
- White-labeling
- Custom habit templates marketplace

---

## 8. Success Criteria

| Metric | MVP Target |
|--------|-----------|
| User can sign up and create first habit | <3 minutes |
| Dashboard loads | <1 second |
| Streak accuracy | 100% (backend validated) |
| Core API test coverage | >80% |
| Mobile-responsive UI | All authenticated pages |

---

## 9. Future Considerations

- Mobile apps (React Native or native)
- Team/workplace habits
- Integration with fitness trackers
- Habit marketplace
- Coach marketplace
- Enterprise plans

---

*Document maintained by product team. Update when requirements change.*
