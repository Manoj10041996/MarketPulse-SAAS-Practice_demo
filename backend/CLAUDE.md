# Backend (packages/backend)

FastAPI service, Python 3.12, managed with [uv](https://docs.astral.sh/uv/).

- Run dev server: `uv run uvicorn app.main:app --reload` (port 8000)
- Install/sync deps: `uv sync`
- Add a dependency: `uv add <package>`
- No test suite yet — when adding one, use `pytest` and keep tests next to the code they cover under `app/`.

Application code lives in `app/`. Routers stay thin and call into service
functions; see the repo-root `.claude/rules/python-fastapi.md` for the full
FastAPI conventions (loads automatically when you touch `.py` files here).
