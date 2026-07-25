# Coding Rules

- FastAPI routers stay thin. Routers parse the request and call a service function; business logic lives in `app/services`, not in route handlers.
- Pydantic models for all I/O. Every endpoint has a typed request model (where applicable) and a typed response model — no raw dicts crossing the API boundary.
- React components stay small and typed. One component, one responsibility; props are typed, no `any`.
- Conventional commits. Commit messages follow `type(scope): summary` (e.g. `feat(backend): add pricing endpoint`, `fix(frontend): correct login redirect`).
