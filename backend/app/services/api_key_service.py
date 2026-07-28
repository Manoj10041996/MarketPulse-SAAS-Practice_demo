from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_raw_api_key, hash_api_key
from app.models.api_key import ApiKey


async def create_api_key(session: AsyncSession, owner_label: str) -> tuple[ApiKey, str]:
    """Creates and persists a new API key. Returns (row, raw_key) — the raw
    key is never stored and must be surfaced to the caller immediately;
    this is the only place it's ever available in plaintext."""
    raw_key = generate_raw_api_key()
    row = ApiKey(owner_label=owner_label, hashed_key=hash_api_key(raw_key))
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row, raw_key


async def get_api_key_by_raw_key(session: AsyncSession, raw_key: str) -> ApiKey | None:
    hashed = hash_api_key(raw_key)
    result = await session.execute(
        select(ApiKey).where(ApiKey.hashed_key == hashed, ApiKey.revoked_at.is_(None))
    )
    return result.scalar_one_or_none()
