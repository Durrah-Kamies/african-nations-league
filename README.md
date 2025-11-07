# African Nations League – Project Guide

Short, humanized notes for reviewers/students. This app simulates an African Nations League with team registration, bracket play, AI commentary, and analytics.

## What’s inside

- **Backend (Flask)** in `backend/`
  - `app.py`: JSON APIs, match simulator, knockout logic, AI hooks
  - `config.py`: Firebase + Gemini initialization
  - `ai_commentary.py`: AI preview/commentary/analysis with fallbacks
- **Frontend (React)** in `frontend/`
  - Pages: `HomePage`, `BracketPage`, `StandingsPage`, `TeamAnalyticsPage`, `RegisterPage`, `DashboardPage`, `MatchPage`, `LoginPage`
  - Global styles in `frontend/src/style.css`
- **Static styles** for legacy pages in `static/css/style.css`

## Setup

Prereqs:

- Python 3.10+
- Node 18+
- Firebase project with Firestore (or run without data)
- Optional: Gemini API key for AI features

### 1) Backend

Install:

```
pip install -r requirements.txt
```

Environment (choose one way for Firebase creds):

- Place `serviceAccountKey.json` at project root, or
- Set `FIREBASE_CONFIG_JSON` (entire JSON string), or
- Set individual vars: `FIREBASE_PROJECT_ID`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_CLIENT_EMAIL`

Optional Gemini:

- Set `GEMINI_API_KEY` to enable AI text (fallback used if missing)

Run:

```
python backend/app.py
# http://localhost:5000
```

### 2) Frontend

From `frontend/`:

```
npm install
npm start
# http://localhost:3000
```

## Common flows

- Login (demo): `admin@anl.com` / `admin123`
- Register teams: `/register`
- Create bracket: `/admin` (needs 8 teams)
- View bracket: `/tournament`
- Play/simulate matches: from `/admin` or the match page
- Golden Boot: `/standings`
- Team Analytics: `/analytics`

## APIs (samples)

- GET `/api/teams` — list teams
- POST `/api/teams` — create team (auto-generates squad + rating)
- GET `/api/matches` — list matches
- GET `/api/match/{id}` — match details
- GET `/api/match_preview/{id}` — AI preview (or fallback)
- GET `/api/player_analysis/{id}/{player}` — AI per-scorer analysis
- POST `/api/admin/create_tournament` — seed QFs
- POST `/api/admin/reset_tournament` — clear matches

## Notes

- Comments were added across files to explain intent and “why” without changing behavior
- Keep secrets out of source control; use environment variables or `.env`
- If Gemini key is missing, the app still works with friendly fallback text
