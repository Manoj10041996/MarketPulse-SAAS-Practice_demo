from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.api_key import ApiKey
from app.services.api_key_service import get_api_key_by_raw_key


async def get_current_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: AsyncSession = Depends(get_db_session),
) -> ApiKey:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Not authenticated")

    api_key = await get_api_key_by_raw_key(session, x_api_key)
    if api_key is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return api_key
