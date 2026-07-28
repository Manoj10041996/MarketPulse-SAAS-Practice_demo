import pytest
from pydantic import ValidationError

from app.agents.amazon_analysis_agent import get_amazon_analysis_agent
from app.config import Settings


def test_agent_is_a_singleton():
    agent_a = get_amazon_analysis_agent()
    agent_b = get_amazon_analysis_agent()
    assert agent_a is agent_b


def test_settings_fail_fast_on_missing_config(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.delenv("OXYLABS_USERNAME", raising=False)
    monkeypatch.delenv("OXYLABS_PASSWORD", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
