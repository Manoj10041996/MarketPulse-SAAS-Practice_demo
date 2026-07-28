import logging
from typing import Any

from app.clients.oxylabs import OxylabsAPIError
from app.config import Settings
from app.core.exceptions import AgentUnavailableError
from app.schemas.analysis import AgentAnalysisResult, AnalysisResponse
from app.tools.amazon_tools import reset_request_counters

logger = logging.getLogger(__name__)


async def run_competitor_analysis(
    question: str,
    domain: str | None,
    agent: Any,
    settings: Settings,
) -> AnalysisResponse:
    resolved_domain = domain or settings.default_marketplace_domain

    reset_request_counters()

    message = f"Marketplace domain: {resolved_domain}\n\nQuestion: {question}"

    try:
        result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})
    except OxylabsAPIError:
        # Tools are expected to catch this themselves and return an error
        # string to the agent — this only fires if one somehow escapes
        # that layer. Treated as a distinct upstream-provider failure
        # (502), not a generic agent failure (503).
        logger.exception("OxylabsAPIError escaped the tool layer")
        raise
    except Exception as exc:  # noqa: BLE001 - intentional broad catch at the boundary
        logger.exception("Amazon analysis agent invocation failed")
        raise AgentUnavailableError() from exc

    structured: AgentAnalysisResult | None = result.get("structured_response")
    if structured is None:
        logger.error("Agent invocation returned no structured_response: %r", result)
        raise AgentUnavailableError()

    return AnalysisResponse(
        question=question,
        domain=resolved_domain,
        summary=structured.summary,
        products=structured.products,
        warnings=structured.warnings,
    )
