# HabitForge — API Specification

**Version:** v1  
**Base URL:** `/api/v1`  
**Auth:** Bearer JWT (except public endpoints)  
**Format:** JSON  
**Last Updated:** 2026-09-01

---

## 1. Conventions

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

### Standard Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

### Standard Success Response (list)
```json
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (not owner) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |

---

## 2. Authentication — `/auth`

### POST `/auth/register`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Jane Doe",
  "timezone": "Asia/Kolkata"
}
```

**Response 201:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "subscription_tier": "free",
    "onboarding_completed": false
  }
}
```

**Errors:** `409 EMAIL_ALREADY_EXISTS`, `422 VALIDATION_ERROR`

---

### POST `/auth/login`
Authenticate and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response 200:** Same as register response.

**Errors:** `401 INVALID_CREDENTIALS`, `403 ACCOUNT_INACTIVE`

---

### POST `/auth/refresh`
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### POST `/auth/logout`
🔒 Invalidate current session.

**Response 204:** No content.

---

### POST `/auth/forgot-password`
Request a password reset email (architecture ready, email optional for MVP).

**Request:**
```json
{ "email": "user@example.com" }
```

**Response 200:** Always returns success (prevents email enumeration).

---

### POST `/auth/reset-password`
Complete password reset with token.

**Request:**
```json
{
  "token": "reset_token",
  "new_password": "NewPassword123!"
}
```

---

## 3. Users — `/users`

### GET `/users/me`
🔒 Get current authenticated user profile.

**Response 200:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "janedoe",
  "full_name": "Jane Doe",
  "avatar_url": null,
  "timezone": "Asia/Kolkata",
  "subscription_tier": "free",
  "onboarding_completed": true,
  "created_at": "2026-09-01T00:00:00Z"
}
```

---

### PATCH `/users/me`
🔒 Update user profile.

**Request:**
```json
{
  "full_name": "Jane Smith",
  "timezone": "America/New_York"
}
```

---

### DELETE `/users/me`
🔒 Delete user account (soft delete, requires confirmation).

---

## 4. Goals — `/goals`

### GET `/goals`
🔒 Get all goals for authenticated user.

**Query Params:** `status=active|completed|paused`, `page=1`, `per_page=20`

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Become better at DSA",
      "description": "...",
      "category": "coding",
      "status": "active",
      "target_date": "2026-12-31",
      "habit_count": 4,
      "completed_habits_today": 2,
      "created_at": "2026-09-01T00:00:00Z"
    }
  ],
  "meta": { "total": 3, "page": 1, "per_page": 20 }
}
```

---

### POST `/goals`
🔒 Create a new goal.

**Request:**
```json
{
  "title": "Become better at DSA",
  "description": "Practice consistently to master data structures",
  "category": "coding",
  "target_date": "2026-12-31"
}
```

**Response 201:** Full goal object.

---

### GET `/goals/{goal_id}`
🔒 Get a specific goal with its habits.

---

### PATCH `/goals/{goal_id}`
🔒 Update a goal.

---

### DELETE `/goals/{goal_id}`
🔒 Soft delete a goal.

---

## 5. Habits — `/habits`

### GET `/habits`
🔒 Get user's habits.

**Query Params:** `is_active=true`, `goal_id=uuid`, `category=coding`, `page=1`

**Response 200:**
```json
{
  "data": [
    {
      "id": "uuid",
      "goal_id": "uuid|null",
      "title": "Solve DSA Problems",
      "category": "coding",
      "frequency_type": "specific_days",
      "frequency_days": [1, 2, 3, 4, 5, 6],
      "target_value": 2,
      "target_unit": "problems",
      "is_active": true,
      "is_archived": false,
      "current_streak": 12,
      "best_streak": 18,
      "total_completions": 67,
      "completed_today": false,
      "start_date": "2026-07-01",
      "created_at": "2026-07-01T00:00:00Z"
    }
  ]
}
```

---

### POST `/habits`
🔒 Create a new habit.

**Request:**
```json
{
  "title": "Solve DSA Problems",
  "description": "Solve problems on LeetCode",
  "category": "coding",
  "goal_id": "uuid",
  "frequency_type": "specific_days",
  "frequency_days": [1, 2, 3, 4, 5, 6],
  "target_value": 2,
  "target_unit": "problems",
  "start_date": "2026-09-01",
  "color": "#6366f1"
}
```

**Response 201:** Full habit object.

**Errors:** `403 HABIT_LIMIT_EXCEEDED` (free tier)

---

### GET `/habits/{habit_id}`
🔒 Get a specific habit with full details.

---

### PATCH `/habits/{habit_id}`
🔒 Update a habit.

---

### DELETE `/habits/{habit_id}`
🔒 Soft delete a habit.

---

### POST `/habits/{habit_id}/complete`
🔒 Mark a habit as complete for today.

**Request:**
```json
{
  "value": 2,
  "notes": "Solved two medium problems today",
  "completed_date": "2026-09-01"
}
```

**Response 200:**
```json
{
  "log": {
    "id": "uuid",
    "habit_id": "uuid",
    "completed_date": "2026-09-01",
    "value": 2,
    "notes": "..."
  },
  "streak": {
    "current_streak": 13,
    "best_streak": 18,
    "total_completions": 68
  },
  "achievements_unlocked": []
}
```

**Errors:** `409 ALREADY_COMPLETED`, `400 FUTURE_DATE_NOT_ALLOWED`

---

### DELETE `/habits/{habit_id}/complete`
🔒 Undo today's completion (within allowed window).

---

### GET `/habits/{habit_id}/logs`
🔒 Get completion history for a habit.

**Query Params:** `start_date=2026-08-01`, `end_date=2026-09-01`

---

### PATCH `/habits/{habit_id}/archive`
🔒 Archive a habit (hides from dashboard but preserves history).

---

## 6. Dashboard — `/dashboard`

### GET `/dashboard`
🔒 Get aggregated daily dashboard view for the authenticated user in their local timezone.

**Response 200:**
```json
{
  "user": {
    "full_name": "Jane Doe",
    "current_date": "2026-09-01",
    "timezone": "Asia/Kolkata"
  },
  "today": {
    "total_expected_habits": 5,
    "completed_habits": 4,
    "completion_percentage": 80.0,
    "habits": [
      {
        "id": "uuid",
        "user_id": "uuid",
        "goal_id": "uuid|null",
        "title": "Solve DSA Problems",
        "description": "2 medium LeetCode problems",
        "category": "coding",
        "frequency_type": "daily",
        "frequency_days": null,
        "target_value": 2.0,
        "target_unit": "problems",
        "color": null,
        "icon": null,
        "start_date": "2026-08-01",
        "end_date": null,
        "is_active": true,
        "is_archived": false,
        "current_streak": 13,
        "best_streak": 18,
        "total_completions": 68,
        "completed_today": true,
        "order_index": 0,
        "created_at": "2026-08-01T10:00:00Z",
        "updated_at": "2026-09-01T10:00:00Z"
      }
    ]
  },
  "consistency_summary": {
    "total_active_habits": 5,
    "total_completions_all_time": 68,
    "best_streak_overall": 18
  }
}
```
  "weekly_summary": {
    "completion_rate": 78,
    "days": [
      { "date": "2026-08-26", "completion_percentage": 100 },
      { "date": "2026-08-27", "completion_percentage": 60 }
    ]
  }
}
```

---

## 7. Analytics — `/analytics`

### GET `/analytics/trends`
🔒 Aggregate habit consistency trends, momentum scoring, day-of-week breakdown, category performance, and deterministic behavioral insights.

**Query Params:** `days=30` (7 to 365, default 30)

**Response 200:**
```json
{
  "time_range_days": 30,
  "overall_consistency": 82.5,
  "total_habits_tracked": 4,
  "total_completions": 95,
  "momentum_score": 84,
  "weekly_trends": [
    {
      "week_start": "2026-08-01",
      "week_end": "2026-08-07",
      "expected": 28,
      "completed": 24,
      "percentage": 85.7
    }
  ],
  "day_of_week": [
    {
      "day_name": "Monday",
      "day_index": 0,
      "expected": 16,
      "completed": 15,
      "percentage": 93.8
    }
  ],
  "category_breakdown": [
    {
      "category": "coding",
      "habit_count": 2,
      "expected": 60,
      "completed": 54,
      "percentage": 90.0
    }
  ],
  "insights": [
    {
      "type": "best_day",
      "title": "Peak Consistency: Monday",
      "description": "You complete 93.8% of habits scheduled on Mondays.",
      "impact": "positive"
    }
  ]
}
```

---

### GET `/analytics/calendar`
🔒 Authoritative calendar data and completion percentages for history/heatmap view.

**Query Params:** `start_date=2026-08-01`, `end_date=2026-09-01`, `habit_id=uuid (optional)`

---

## 8. Achievements — `/achievements`

### GET `/achievements`
🔒 Get complete system achievement catalog.

**Response 200:**
```json
[
  {
    "id": "uuid",
    "code": "streak_7",
    "title": "7-Day Streak",
    "description": "Maintained a streak for 7 consecutive days",
    "icon": "flame",
    "category": "streak",
    "criteria_type": "streak",
    "criteria_value": 7,
    "is_active": true
  }
]
```

---

### GET `/achievements/me`
🔒 Get authenticated user's achievements with unlock status and deterministic progress metrics.

**Response 200:**
```json
[
  {
    "id": "uuid",
    "code": "streak_7",
    "title": "7-Day Streak",
    "description": "Maintained a streak for 7 consecutive days",
    "icon": "flame",
    "category": "streak",
    "criteria_type": "streak",
    "criteria_value": 7,
    "is_unlocked": true,
    "unlocked_at": "2026-09-01T12:00:00Z",
    "progress": 7,
    "target": 7,
    "progress_percentage": 100.0
  },
  {
    "id": "uuid",
    "code": "streak_30",
    "title": "30-Day Streak",
    "description": "Maintained a streak for 30 consecutive days",
    "icon": "flame",
    "category": "streak",
    "criteria_type": "streak",
    "criteria_value": 30,
    "is_unlocked": false,
    "unlocked_at": null,
    "progress": 7,
    "target": 30,
    "progress_percentage": 23.3
  }
]
```

---

## 9. Reminders — `/reminders`

### POST `/reminders`
🔒 Create a new time-based reminder for a habit.

**Request:**
```json
{
  "habit_id": "uuid",
  "reminder_time": "08:00:00",
  "days_of_week": [0, 1, 2, 3, 4],
  "is_active": true
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "habit_id": "uuid",
  "habit_title": "Study DSA",
  "habit_category": "coding",
  "user_id": "uuid",
  "reminder_time": "08:00:00",
  "days_of_week": [0, 1, 2, 3, 4],
  "is_active": true,
  "created_at": "2026-09-01T12:00:00Z",
  "updated_at": "2026-09-01T12:00:00Z"
}
```

---

### GET `/reminders`
🔒 List all reminders configured by the authenticated user.

**Query Params:** `is_active=true|false (optional)`

**Response 200:** Array of `ReminderPublic` objects.

---

### GET `/reminders/next`
🔒 Get the next upcoming reminder occurrence for the current user.

**Response 200:**
```json
{
  "reminder_id": "uuid",
  "habit_id": "uuid",
  "habit_title": "Study DSA",
  "habit_category": "coding",
  "reminder_time": "08:00:00",
  "next_occurrence": "Tomorrow at 08:00"
}
```

---

### GET `/reminders/{id}`
🔒 Get a specific reminder by ID.

---

### PATCH `/reminders/{id}`
🔒 Update reminder time, days of week, or active state.

---

### DELETE `/reminders/{id}`
🔒 Delete a reminder.

---

## 10. AI — `/ai`

> All AI endpoints are rate-limited and Pro-only (or limited for Free).

### POST `/ai/suggest-habits`
🔒 Get AI habit suggestions for a goal.

**Request:**
```json
{
  "goal_description": "I want to become good at DSA and land a software engineering job",
  "category": "coding",
  "time_available_per_day": 120
}
```

**Response 200:**
```json
{
  "suggestions": [
    {
      "title": "Solve LeetCode Problems",
      "description": "Focus on medium-difficulty problems",
      "target_value": 2,
      "target_unit": "problems",
      "frequency_type": "specific_days",
      "frequency_days": [1, 2, 3, 4, 5]
    }
  ]
}
```

---

### POST `/ai/coach`
🔒 Send message to AI coach (Pro only).

**Request:**
```json
{
  "message": "I keep failing to study consistently. What should I do?",
  "context_window": 7
}
```

---

### GET `/ai/weekly-review`
🔒 Get AI-generated weekly review (Pro only).

---

## 10. Subscriptions — `/subscriptions`

### GET `/subscriptions/me`
🔒 Get current user's subscription status.

---

### POST `/subscriptions/checkout`
🔒 Create checkout session (future payment integration).

---

### POST `/subscriptions/portal`
🔒 Access customer billing portal (future).

---

## 11. Health Check

### GET `/health`
Public endpoint for service health.

**Response 200:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-09-01T00:00:00Z"
}
```

---

*Update this document when adding or changing endpoints.*
