from typing import Any

from fastapi import APIRouter, Depends, Request

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import run_competitor_analysis

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponse)
@limiter.limit(get_settings().analysis_rate_limit)
async def analyze(
    request: Request,
    payload: AnalysisRequest,
    agent: Any = Depends(get_amazon_analysis_agent),
    settings: Settings = Depends(get_settings),
) -> AnalysisResponse:
    return await run_competitor_analysis(payload.question, payload.domain, agent, settings)
