import os
import tempfile

# Must happen before `app.main` (and anything it imports) is loaded: Settings
# and the DB engine are @lru_cache singletons, so the env var has to be in
# place before their first call anywhere in the test session — otherwise
# tests would write into the real dev marketpulse.db.
_TEST_DB_PATH = os.path.join(tempfile.mkdtemp(prefix="marketpulse-test-"), "test.db")
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_TEST_DB_PATH}")

import pytest
from sqlalchemy import delete
from sqlalchemy.exc import OperationalError
from fastapi.testclient import TestClient

from app.db.session import get_db_session
from app.main import app
from app.models.api_key import ApiKey


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def _clear_api_keys_table():
    """get_engine()/get_sessionmaker() are process-wide singletons, so rows
    written by one test's POST /auth/api-keys call would otherwise leak
    into later tests. Tests that never touch the app's shared engine (e.g.
    service-layer tests using their own isolated in-memory DB) won't have
    created the table yet — that's fine, nothing to clean up."""
    yield
    try:
        async for session in get_db_session():
            await session.execute(delete(ApiKey))
            await session.commit()
    except OperationalError:
        pass
