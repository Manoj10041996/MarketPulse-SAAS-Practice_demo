from unittest.mock import AsyncMock, patch

import pytest
from anthropic import AuthenticationError

from app.clients.anthropic_diagnostics import check_anthropic_key


def _fake_auth_error() -> AuthenticationError:
    import httpx

    request = httpx.Request("GET", "https://api.anthropic.com/v1/models")
    response = httpx.Response(401, request=request, json={"error": {"message": "invalid"}})
    return AuthenticationError("invalid", response=response, body=None)


@pytest.mark.asyncio
async def test_check_anthropic_key_returns_true_on_success():
    with patch("app.clients.anthropic_diagnostics.AsyncAnthropic") as mock_cls:
        mock_client = mock_cls.return_value
        mock_client.models.list = AsyncMock(return_value=None)

        result = await check_anthropic_key("sk-ant-test")

    assert result is True


@pytest.mark.asyncio
async def test_check_anthropic_key_returns_false_on_auth_error():
    with patch("app.clients.anthropic_diagnostics.AsyncAnthropic") as mock_cls:
        mock_client = mock_cls.return_value
        mock_client.models.list = AsyncMock(side_effect=_fake_auth_error())

        result = await check_anthropic_key("sk-ant-invalid")

    assert result is False
