import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.services.api_key_service import create_api_key, get_api_key_by_raw_key


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as s:
        yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_api_key_stores_hash_not_raw(session):
    row, raw_key = await create_api_key(session, "acme-co")

    assert row.owner_label == "acme-co"
    assert row.hashed_key != raw_key
    assert raw_key.startswith("mp_")


@pytest.mark.asyncio
async def test_get_api_key_by_raw_key_finds_match(session):
    _, raw_key = await create_api_key(session, "acme-co")

    found = await get_api_key_by_raw_key(session, raw_key)

    assert found is not None
    assert found.owner_label == "acme-co"


@pytest.mark.asyncio
async def test_get_api_key_by_raw_key_rejects_wrong_key(session):
    await create_api_key(session, "acme-co")

    found = await get_api_key_by_raw_key(session, "mp_not-the-real-key")

    assert found is None


@pytest.mark.asyncio
async def test_get_api_key_by_raw_key_rejects_revoked_key(session):
    row, raw_key = await create_api_key(session, "acme-co")
    row.revoked_at = row.created_at
    await session.commit()

    found = await get_api_key_by_raw_key(session, raw_key)

    assert found is None
