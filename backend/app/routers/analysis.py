from typing import Any

from fastapi import APIRouter, Depends, Request

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.config import Settings, get_settings
from app.core.auth import get_current_api_key
from app.core.rate_limit import limiter
from app.models.api_key import ApiKey
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import run_competitor_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _analysis_rate_limit() -> str:
    """Evaluated per-request by slowapi, not at import time — importing this
    module must not require live config/credentials to be present."""
    return get_settings().analysis_rate_limit


@router.post("", response_model=AnalysisResponse)
@limiter.limit(_analysis_rate_limit)
async def analyze(
    request: Request,
    payload: AnalysisRequest,
    agent: Any = Depends(get_amazon_analysis_agent),
    settings: Settings = Depends(get_settings),
    api_key: ApiKey = Depends(get_current_api_key),
) -> AnalysisResponse:
    return await run_competitor_analysis(payload.question, payload.domain, agent, settings)
