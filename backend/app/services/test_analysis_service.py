import pytest

from app.config import get_settings
from app.core.exceptions import AgentUnavailableError
from app.schemas.analysis import AgentAnalysisResult, ComparedProduct
from app.services.analysis_service import run_competitor_analysis


class _FakeAgent:
    def __init__(self, structured=None, raise_error=False):
        self._structured = structured
        self._raise_error = raise_error

    async def ainvoke(self, _messages):
        if self._raise_error:
            raise RuntimeError("boom")
        return {"structured_response": self._structured}


@pytest.mark.asyncio
async def test_run_competitor_analysis_success():
    structured = AgentAnalysisResult(
        summary="Product A leads on price, Product B on reviews.",
        products=[ComparedProduct(asin="B0A", title="Product A", price=19.99)],
        warnings=[],
    )
    agent = _FakeAgent(structured=structured)
    settings = get_settings()

    response = await run_competitor_analysis("compare A and B", None, agent, settings)

    assert response.summary == structured.summary
    assert response.products[0].asin == "B0A"
    assert response.domain == settings.default_marketplace_domain


@pytest.mark.asyncio
async def test_run_competitor_analysis_uses_explicit_domain():
    structured = AgentAnalysisResult(summary="ok", products=[], warnings=[])
    agent = _FakeAgent(structured=structured)
    settings = get_settings()

    response = await run_competitor_analysis("q", "co.uk", agent, settings)

    assert response.domain == "co.uk"


@pytest.mark.asyncio
async def test_agent_exception_becomes_agent_unavailable_error():
    agent = _FakeAgent(raise_error=True)
    settings = get_settings()

    with pytest.raises(AgentUnavailableError):
        await run_competitor_analysis("q", None, agent, settings)


@pytest.mark.asyncio
async def test_missing_structured_response_becomes_agent_unavailable_error():
    agent = _FakeAgent(structured=None)
    settings = get_settings()

    with pytest.raises(AgentUnavailableError):
        await run_competitor_analysis("q", None, agent, settings)
