from unittest.mock import AsyncMock

import pytest

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.clients.oxylabs import OxylabsAPIError
from app.core.auth import get_current_api_key
from app.core.exceptions import AgentUnavailableError
from app.main import app
from app.models.api_key import ApiKey
from app.schemas.analysis import AgentAnalysisResult, ComparedProduct


@pytest.fixture(autouse=True)
def _bypass_auth():
    """These tests are about agent/Oxylabs behavior, not auth — auth itself
    is covered separately in test_analysis_auth.py."""
    app.dependency_overrides[get_current_api_key] = lambda: ApiKey(
        owner_label="test", hashed_key="test"
    )
    yield
    app.dependency_overrides.pop(get_current_api_key, None)


def _override_agent(structured=None, side_effect=None):
    fake_agent = AsyncMock()
    if side_effect is not None:
        fake_agent.ainvoke.side_effect = side_effect
    else:
        fake_agent.ainvoke.return_value = {"structured_response": structured}
    app.dependency_overrides[get_amazon_analysis_agent] = lambda: fake_agent
    return fake_agent


def test_analyze_returns_200_with_expected_shape(client):
    structured = AgentAnalysisResult(
        summary="Product A is cheaper, Product B has more reviews.",
        products=[
            ComparedProduct(asin="B0A", title="Product A", price=19.99, currency="USD")
        ],
        warnings=[],
    )
    _override_agent(structured=structured)

    response = client.post("/analysis", json={"question": "compare wireless earbuds"})

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == structured.summary
    assert body["products"][0]["asin"] == "B0A"
    assert body["domain"] == "com"


def test_analyze_rejects_too_short_question(client):
    response = client.post("/analysis", json={"question": "ab"})
    assert response.status_code == 422


def test_analyze_rejects_bad_domain(client):
    response = client.post(
        "/analysis", json={"question": "valid question here", "domain": "???"}
    )
    assert response.status_code == 422


def test_analyze_returns_503_when_agent_fails(client):
    _override_agent(side_effect=RuntimeError("boom"))

    response = client.post("/analysis", json={"question": "valid question here"})

    assert response.status_code == 503


def test_analyze_returns_502_when_oxylabs_error_escapes(client):
    _override_agent(side_effect=OxylabsAPIError("upstream down"))

    response = client.post("/analysis", json={"question": "valid question here"})

    assert response.status_code == 502
