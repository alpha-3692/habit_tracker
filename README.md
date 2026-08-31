# HabitForge

> **An AI-powered consistency coach that helps users turn goals into sustainable daily habits, understand their behavior, and improve consistency.**

HabitForge combines intelligent habit tracking with AI-driven behavioral analysis and recovery support in a modern, professional SaaS experience.

---

## 🌟 Key Features

- **Goal-to-Habit Architecture**: Link daily actionable habits directly to long-term goals.
- **Authoritative Backend Streaks**: Reliable, history-derived streak calculations that handle custom schedules, skipped days, and timezones.
- **Daily Dashboard**: Rapid progress tracking, streak indicators, and actionable overviews.
- **Analytics & Calendar**: Deep-dive consistency metrics, habit calendars, and behavioral trends.
- **AI Consistency Coach**: Context-aware guidance powered by Claude (via backend) for habit suggestions and weekly reviews.
- **Platform-Independent API**: Versioned REST API (`/api/v1/`) designed to power both web and future native mobile apps (iOS & Android).

---

## 🏗️ Architecture & Tech Stack

- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.x, Alembic, Pydantic v2, JWT Auth, bcrypt
- **Database**: PostgreSQL 15+ (with SQLite support for in-memory testing)
- **AI Engine**: Anthropic Claude API (server-side only)

---

## 📁 Repository Structure

```
habit_tracker/
├── docs/                     # Source of truth documentation
│   ├── PRD.md                # Product Requirements Document
│   ├── ARCHITECTURE.md       # Full System Architecture
│   ├── DATABASE.md           # Schema, ERD, and Streak Logic
│   ├── API.md                # API Specification & Endpoints
│   ├── UI_UX.md              # Design System & Page Specs
│   ├── SECURITY.md           # Security & OWASP Guidelines
│   ├── TESTING.md            # Testing Strategy & Test Cases
│   ├── ROADMAP.md            # Milestone Roadmap
│   └── DECISIONS.md          # Architecture Decision Records (ADRs)
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/v1/           # Version 1 REST API endpoints
│   │   ├── core/             # Configuration, Database, Security & Deps
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic Schemas (Request/Response)
│   │   ├── services/         # Business Logic Layer
│   │   └── repositories/     # Database Access Layer
│   ├── alembic/              # Database Migrations
│   ├── tests/                # Pytest Test Suite
│   └── requirements.txt
├── frontend/                 # Next.js Application
│   ├── src/
│   │   ├── app/              # App Router Pages
│   │   ├── components/       # Reusable UI & Domain Components
│   │   ├── lib/              # API Client & Utilities
│   │   └── types/            # TypeScript Interfaces
│   └── package.json
├── CLAUDE.md                 # Engineering Rules for AI Agents
├── .env.example              # Environment Variable Template
└── README.md
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run migrations
alembic upgrade head

# Start API Server
uvicorn app.main:app --reload --port 8000
```

Backend will be live at `http://localhost:8000` (OpenAPI docs at `http://localhost:8000/docs`).

### 2. Run Backend Tests

```bash
cd backend
pytest -v
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be live at `http://localhost:3000`.

---

## 🔒 Engineering Guidelines

Before modifying code, please consult:
1. [CLAUDE.md](file:///c:/Users/asus/OneDrive/Desktop/habit_tracker/CLAUDE.md) — Mandatory agent guidelines
2. [docs/ARCHITECTURE.md](file:///c:/Users/asus/OneDrive/Desktop/habit_tracker/docs/ARCHITECTURE.md) — System boundaries & standards
3. [docs/API.md](file:///c:/Users/asus/OneDrive/Desktop/habit_tracker/docs/API.md) — API schemas and contracts