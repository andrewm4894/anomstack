"""Request telemetry must preserve application behavior."""

import asyncio
from unittest.mock import Mock

import pytest

from anomstack.observability import ObservabilityMiddleware, configure_observability


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("POSTHOG_OBSERVABILITY_ENABLED", raising=False)
    assert configure_observability() is None


def test_response_is_preserved():
    client = Mock()
    messages = []

    async def send(message):
        messages.append(message)

    async def application(scope, receive, send):
        await send({"type": "http.response.start", "status": 204})
        await send({"type": "http.response.body", "body": b""})

    asyncio.run(
        ObservabilityMiddleware(application, client)(
            {"type": "http", "method": "GET", "path": "/"}, None, send
        )
    )
    assert messages[0]["status"] == 204
    assert messages[1]["body"] == b""
    client.capture_exception.assert_not_called()


def test_exception_is_captured_and_reraised():
    client = Mock()
    error = ValueError("controlled test")

    async def application(scope, receive, send):
        raise error

    with pytest.raises(ValueError, match="controlled test"):
        asyncio.run(
            ObservabilityMiddleware(application, client)(
                {"type": "http", "method": "GET", "path": "/"}, None, None
            )
        )
    client.capture_exception.assert_called_once_with(error, distinct_id="anomstack-demo-server")
