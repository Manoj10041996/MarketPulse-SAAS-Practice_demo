import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.clients.oxylabs import OxylabsAPIError, get_oxylabs_client
from app.config import get_settings
from app.core.exceptions import AgentUnavailableError
from app.core.rate_limit import register_rate_limiting
from app.routers import analysis, health

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Validates required config (Oxylabs creds, LLM/Tavily keys) at process
    # startup, so a misconfigured deploy crash-loops visibly instead of
    # 500ing on a customer's first request. Also eagerly builds the
    # singleton client/agent to avoid first-request cold-start latency.
    get_settings()
    get_oxylabs_client()
    get_amazon_analysis_agent()
    yield


app = FastAPI(title="MarketPulse", lifespan=lifespan)

register_rate_limiting(app)

app.include_router(health.router)
app.include_router(analysis.router)


@app.exception_handler(OxylabsAPIError)
async def oxylabs_error_handler(_request: Request, exc: OxylabsAPIError) -> JSONResponse:
    logger.error("Oxylabs API error: %s", exc.message)
    return JSONResponse(
        status_code=502,
        content={"detail": "Upstream data provider error, please try again shortly."},
    )


@app.exception_handler(AgentUnavailableError)
async def agent_unavailable_handler(_request: Request, exc: AgentUnavailableError) -> JSONResponse:
    logger.error("Agent unavailable: %s", exc.message)
    return JSONResponse(status_code=503, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
