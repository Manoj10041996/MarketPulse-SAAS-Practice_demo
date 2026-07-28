from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.api_key import ApiKeyCreateRequest, ApiKeyCreateResponse
from app.services.api_key_service import create_api_key

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/api-keys", response_model=ApiKeyCreateResponse, status_code=201)
async def create_api_key_endpoint(
    payload: ApiKeyCreateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeyCreateResponse:
    row, raw_key = await create_api_key(session, payload.owner_label)
    return ApiKeyCreateResponse(
        id=row.id,
        owner_label=row.owner_label,
        api_key=raw_key,
        created_at=row.created_at,
    )
