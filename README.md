# MarketPulse

An AI agent that scrapes Amazon via Oxylabs and exposes the data to
customers through an authenticated API.

See [`CLAUDE.md`](CLAUDE.md) for the full product summary, tech stack,
folder layout, and golden rules.

## Requirements

- Python >= 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js and npm

## Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`.

```bash
curl http://127.0.0.1:8000/health
```

```json
{"status": "ok"}
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Live Deployment

Backend is deployed on Google Cloud Run: **https://marketpulse-saas-33726424306.us-central1.run.app**

```bash
curl https://marketpulse-saas-33726424306.us-central1.run.app/health
```

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness check — returns `{"status": "ok"}` |

## Environment Variables

Copy `.env.example` to `.env` and fill in real values — see that file for
the full list (OpenAI, Oxylabs, Supabase, Postgres, JWT).

## Author

Manoj Kumar Yendluri
