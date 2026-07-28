from unittest.mock import AsyncMock

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.main import app
from app.schemas.analysis import AgentAnalysisResult


def _override_agent():
    fake_agent = AsyncMock()
    fake_agent.ainvoke.return_value = {
        "structured_response": AgentAnalysisResult(summary="ok", products=[], warnings=[])
    }
    app.dependency_overrides[get_amazon_analysis_agent] = lambda: fake_agent


def test_analyze_without_api_key_returns_401(client):
    _override_agent()

    response = client.post("/analysis", json={"question": "valid question here"})

    assert response.status_code == 401


def test_analyze_with_garbage_api_key_returns_401(client):
    _override_agent()

    response = client.post(
        "/analysis",
        json={"question": "valid question here"},
        headers={"X-API-Key": "not-a-real-key"},
    )

    assert response.status_code == 401


def test_analyze_with_valid_api_key_returns_200(client):
    _override_agent()

    create_response = client.post("/auth/api-keys", json={"owner_label": "acme-co"})
    raw_key = create_response.json()["api_key"]

    response = client.post(
        "/analysis",
        json={"question": "valid question here"},
        headers={"X-API-Key": raw_key},
    )

    assert response.status_code == 200
