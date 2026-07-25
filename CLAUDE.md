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
backend/    FastAPI app (Python 3.12, uv-managed)
  app/      application code
frontend/   React + Vite + TypeScript app
supabase/
  migrations/  SQL migrations
docs/       project documentation
prompts/    prompt templates used by the AI agent
.claude/    Claude Code rules and project memory
```

## Running Locally

**Backend:**

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`. Health check: `GET /health`.

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

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
