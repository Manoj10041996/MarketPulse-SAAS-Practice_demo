from unittest.mock import AsyncMock, patch


def test_anthropic_key_check_valid(client):
    with patch(
        "app.routers.diagnostics.check_anthropic_key", new=AsyncMock(return_value=True)
    ):
        response = client.get("/diagnostics/anthropic-key")

    assert response.status_code == 200
    assert response.json() == {"valid": True}


def test_anthropic_key_check_invalid(client):
    with patch(
        "app.routers.diagnostics.check_anthropic_key", new=AsyncMock(return_value=False)
    ):
        response = client.get("/diagnostics/anthropic-key")

    assert response.status_code == 200
    assert response.json() == {"valid": False}
