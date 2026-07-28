from fastapi import APIRouter, Request

from app.clients.anthropic_diagnostics import check_anthropic_key
from app.config import get_settings
from app.core.rate_limit import limiter
from app.schemas.diagnostics import AnthropicKeyCheckResponse

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.get("/anthropic-key", response_model=AnthropicKeyCheckResponse)
@limiter.limit("5/minute")
async def anthropic_key_check(request: Request) -> AnthropicKeyCheckResponse:
    settings = get_settings()
    valid = await check_anthropic_key(settings.anthropic_api_key)
    return AnthropicKeyCheckResponse(valid=valid)
