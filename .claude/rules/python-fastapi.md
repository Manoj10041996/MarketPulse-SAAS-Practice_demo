---
paths:
  - "backend/**/*.py"
---

# Python / FastAPI Rules

- Type-hint everything. Every function signature (params and return type) is typed; no bare `dict`/`list` where a Pydantic model or dataclass fits better.
- Pydantic models for every request and response. Set `response_model` on each route; never return a raw dict or ORM object directly.
- Async for I/O-bound work. Routes and service functions that call the database, Oxylabs, or OpenAI are `async def`; never block the event loop with a synchronous network/file call inside one.
- Dependency injection over manual wiring. Shared concerns (DB session, current user, auth) go through FastAPI `Depends`, not global state or module-level singletons.
- One router per domain. Group endpoints by resource (`routers/products.py`, `routers/auth.py`, ...); each router only defines routes and calls a service — no business logic inline.
- Config via `pydantic-settings`. Read environment variables through a typed `Settings` object, not scattered `os.environ.get()` calls.
- Explicit errors. Raise `HTTPException` with the right status code and a clear message; never let an internal exception/stack trace leak to the client.
- No `print()`. Use the `logging` module so output is filterable and structured in production.
