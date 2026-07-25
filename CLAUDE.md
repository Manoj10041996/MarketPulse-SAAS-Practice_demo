# MarketPulse

MarketPulse is a SaaS product that runs an AI agent to scrape Amazon product
and pricing data via Oxylabs. That data is exposed to paying customers
through an authenticated REST API, backed by Supabase for auth and storage.

## Tech Stack

- **Backend**: Python 3.12, FastAPI, managed with [uv](https://docs.astral.sh/uv/)
- **Frontend**: React + TypeScript, built with Vite
- **Database / Auth**: Supabase (Postgres)
- **Scraping**: Oxylabs
- **AI**: OpenAI

## Folder Layout

```
backend/    FastAPI app (Python 3.12, uv-managed) — has its own CLAUDE.md
  app/      application code
frontend/   React + Vite + TypeScript app — has its own CLAUDE.md
supabase/
  migrations/  SQL migrations
docs/       project documentation
prompts/    prompt templates used by the AI agent
.claude/
  rules/    coding/security rules — some are path-scoped, see below
```

Run package commands from inside that package's directory, not the repo
root — `backend/CLAUDE.md` and `frontend/CLAUDE.md` cover build/test/run
specifics and load automatically once Claude touches files there.

## Running Locally

**Backend** (see `backend/CLAUDE.md` for details):

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`. Health check: `GET /health`.

**Frontend** (see `frontend/CLAUDE.md` for details):

```bash
cd frontend
npm install
npm run dev
```

## Rules

`.claude/rules/security.md` and `coding.md` apply everywhere.
`.claude/rules/python-fastapi.md` and `react-ui.md` are path-scoped —
they only load into context when Claude works with matching files
(`backend/**/*.py` and `frontend/**/*.{ts,tsx}` respectively), so
backend work doesn't pull in frontend conventions and vice versa.

## Self-Learning (Auto Memory)

Claude Code has an auto-memory feature (on by default) that lets Claude
save its own notes across sessions — build quirks, debugging insights,
preferences it's been corrected on — without anyone writing them by hand.
It's stored per-machine, not in this repo, so it isn't shared between
teammates the way `CLAUDE.md` and `.claude/rules/` are. If a correction
should apply to everyone, put it in `CLAUDE.md` or `.claude/rules/`
instead of leaving it to auto memory alone.

## Deployed Backend

Live on Google Cloud Run: **https://marketpulse-saas-33726424306.us-central1.run.app**

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check — returns `{"status": "ok"}` |

Every push to `main` redeploys this service automatically (see `.github/workflows/deploy.yml`).

## Golden Rules

- **Typed Python**: every function has type hints; Pydantic models for all API input/output.
- **Small functions**: one responsibility per function; prefer composition over long procedures.
- **No secrets in code**: all config comes from environment variables (see `.env.example`); never commit real credentials.
- **Tests for business logic**: any non-trivial logic (scraping, pricing, auth) needs tests — routers and glue code don't.
