# HabitForge — UI/UX Specification

**Version:** 0.1.0  
**Status:** Active  
**Last Updated:** 2026-09-01

---

## 1. Design Philosophy

HabitForge should feel like a **serious productivity tool for ambitious people**, not a gamified checklist app.

### Principles
- **Premium over flashy** — Clean, professional, trustworthy
- **Clarity first** — Every element earns its place
- **Motivating without being juvenile** — Data and progress, not badges and confetti
- **Accessible** — WCAG 2.1 AA minimum
- **Fast** — Perceived performance matters as much as actual performance

### Anti-Patterns to Avoid
- ❌ Excessive animations
- ❌ Childish badge systems
- ❌ Cluttered dashboards
- ❌ Gamification that trivializes goals
- ❌ Dark patterns in subscription flows

---

## 2. Visual Identity

### Color System

```
Primary:     #6366f1  (Indigo-500) — Brand, CTAs
Primary Dark: #4f46e5 (Indigo-600) — Hover states
Accent:      #8b5cf6  (Violet-500) — Highlights, streaks
Success:     #10b981  (Emerald-500) — Completions
Warning:     #f59e0b  (Amber-500)  — Warnings
Error:       #ef4444  (Red-500)    — Errors
Neutral-900: #111827              — Primary text
Neutral-600: #4b5563              — Secondary text
Neutral-200: #e5e7eb              — Borders
Neutral-50:  #f9fafb              — Surface backgrounds
White:       #ffffff              — Base
```

### Dark Mode (Default for MVP)
```
Background:  #0f0f0f — Page background
Surface:     #1a1a1a — Card backgrounds
Surface-2:   #242424 — Elevated surfaces
Border:      #2e2e2e — Borders
Text-1:      #f5f5f5 — Primary text
Text-2:      #a0a0a0 — Secondary text
Text-3:      #666666 — Muted text
```

### Typography
```
Font Family: Inter (Google Fonts)
Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

Scale:
- Display: 48px / 700 weight
- H1:      36px / 700 weight
- H2:      28px / 600 weight
- H3:      22px / 600 weight
- H4:      18px / 600 weight
- Body:    16px / 400 weight
- Small:   14px / 400 weight
- Caption: 12px / 400 weight
```

---

## 3. Component System

### Base Components
- `Button` (primary, secondary, ghost, danger, icon)
- `Input` (text, email, password, date, number)
- `Select` (single, multi)
- `Checkbox`
- `Toggle` (habit complete toggle)
- `Badge` (category, status, tier)
- `Card` (surface container)
- `Modal` / `Dialog`
- `Tooltip`
- `Avatar`
- `Progress` (linear, circular)
- `Skeleton` (loading states)
- `Toast` / `Notification`
- `Dropdown` / `Menu`

### Domain Components
- `HabitCard` — Displays habit with completion state
- `HabitToggle` — Large, satisfying completion button
- `StreakBadge` — Current streak display with flame icon
- `ProgressRing` — Circular progress for daily completion
- `GoalCard` — Goal with progress bar and habit list
- `CalendarGrid` — Month view with completion indicators
- `AnalyticsChart` — Line/bar chart for habit history
- `AchievementCard` — Achievement display (locked/unlocked)
- `AIMessage` — Chat bubble for AI coach

---

## 4. Page Specifications

### 4.1 Landing Page (`/`)

**Goal:** Convert visitors into signups

**Sections:**
1. Hero — Headline, subheadline, CTA (sign up free)
2. Problem — What fails with typical habit apps
3. Product Loop — Animated explanation of core loop
4. Features — Key differentiators (3-4 features)
5. Social Proof — Placeholder for testimonials
6. Pricing — Free vs Pro cards
7. Footer

**Copy:**
- Headline: "Build habits that actually stick."
- Subheadline: "HabitForge combines smart tracking with AI coaching to help you understand *why* you're failing — and fix it."

---

### 4.2 Auth Pages (`/login`, `/signup`)

- Centered card layout
- Email + password form
- "Continue with Google" (future, grayed out with "Coming soon" in MVP)
- Password strength indicator (signup)
- Link to terms and privacy

---

### 4.3 Onboarding Flow

Multi-step wizard after first signup:

**Step 1: Welcome**
- "What do you want to improve?"
- Category grid (icon + label cards)

**Step 2: Your Goal**
- Goal title input
- Goal description (optional)
- Target date (optional)

**Step 3: Suggested Habits** (if AI available)
- 4-6 habit suggestions based on goal
- Selectable cards
- "Add custom habit" option

**Step 4: Schedule**
- Frequency selection
- Reminder time (optional)

**Step 5: Ready**
- Summary of what they've set up
- "Go to Dashboard" CTA

---

### 4.4 Dashboard (`/app/dashboard`)

**Layout:** Sidebar (left) + Main content

**Sidebar:**
- Logo + brand
- Navigation links (Dashboard, Habits, Goals, Calendar, Analytics, Achievements, AI Coach)
- User avatar + subscription status
- Settings link

**Main Content:**
```
┌─────────────────────────────────────────────────────┐
│  Good morning, Jane 👋                              │
│  Monday, September 1st                              │
├──────────────────┬──────────────────────────────────┤
│  Today's Progress│  Current Streak                  │
│  ████████░░  80% │  🔥 13 days                     │
│  4 of 5 completed│  Best: 21 days                   │
├──────────────────┴──────────────────────────────────┤
│  Today's Habits                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ ✅ Solve DSA Problems    2 / 2 problems     │   │
│  │ ✅ Read                  30 / 30 mins       │   │
│  │ ✅ Exercise              1 / 1 session      │   │
│  │ ✅ Review mistakes       done               │   │
│  │ ⭕ Evening Journaling    —                  │   │
│  └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  Goals                    Weekly Summary            │
│  [Goal cards]             [Mini chart]              │
└─────────────────────────────────────────────────────┘
```

---

### 4.5 Habits (`/app/habits`)

**List view** with:
- Filter by category, status
- Sort by created date, streak, name
- Add habit button (FAB + header)
- Each habit card shows: name, streak, category, frequency, today's status

**Habit Detail (`/app/habits/[id]`):**
- Full habit info
- Quick complete button
- 3-month calendar view
- Streak stats
- Recent completions
- Edit / Archive / Delete actions

---

### 4.6 Goals (`/app/goals`)

- Goal cards with progress bars
- Associated habits list
- Create new goal form
- Goal detail with full habit breakdown

---

### 4.7 Calendar (`/app/calendar`)

- Full monthly calendar
- Color-coded day cells (completed %, missed, partial)
- Habit filter sidebar
- Click day → see that day's completions

---

### 4.8 Analytics (`/app/analytics`)

- Period selector (7d, 30d, 90d, 1y)
- Overall completion rate trend chart
- Per-habit cards with mini charts
- Day-of-week heatmap (best days)
- Consistency score (Pro)

---

### 4.9 AI Coach (`/app/ai-coach`) — Pro Only

- Chat interface
- Context sidebar (user's stats summary)
- Weekly review report card
- Pro upgrade prompt for Free users

---

### 4.10 Settings (`/app/settings`)

Sections:
- Profile (name, email, avatar, timezone)
- Notifications (reminder preferences)
- Subscription (current plan, upgrade CTA, billing portal)
- Account (change password, delete account, export data)

---

## 5. Responsive Design

| Breakpoint | Min Width | Layout |
|-----------|----------|--------|
| Mobile | 0px | Single column, bottom nav |
| Tablet | 768px | Collapsed sidebar, 2-col grid |
| Desktop | 1024px | Full sidebar, multi-col layout |
| Wide | 1280px | Max-width container, wider content |

**Mobile Dashboard:**
- Horizontal scrollable habit list
- Bottom navigation bar replacing sidebar
- Condensed stats at top

---

## 6. Interaction Patterns

### Habit Completion
- Large checkbox/toggle
- Satisfying animation on complete (subtle scale + color shift)
- Optimistic UI update → confirm with backend

### Streak Milestone
- Subtle celebration on 7, 30, 100-day milestones
- Non-intrusive toast notification

### Loading States
- Skeleton screens (not spinners) for main content
- Inline spinners only for button actions

### Error States
- Inline validation for forms
- Toast for API errors
- Full page error for unrecoverable states

---

## 7. Accessibility

- All interactive elements keyboard navigable
- Focus visible (custom focus ring)
- Color not the only indicator (icons + text)
- Minimum contrast ratio: 4.5:1 for body text
- ARIA labels on icon-only buttons
- Screen reader tested for main flows

---

*Update this document when UI patterns or pages change.*
