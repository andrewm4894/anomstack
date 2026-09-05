"""Opt-in PostHog error tracking and OpenTelemetry application logs."""

import atexit
import logging
import os
import time

_client = None


def configure_observability():
    """Initialize once per process; leave non-demo installations unchanged."""
    global _client
    if _client is not None:
        return _client
    key = os.getenv("POSTHOG_API_KEY")
    if not key or os.getenv("POSTHOG_OBSERVABILITY_ENABLED", "false").lower() != "true":
        return None

    from posthog import Posthog

    host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com").rstrip("/")
    _client = Posthog(
        key,
        host=host,
        enable_exception_autocapture=True,
        super_properties={"app": "anomstack", "environment": "demo"},
    )
    atexit.register(_client.shutdown)

    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.resources import Resource

    provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": "anomstack-dashboard",
                "deployment.environment.name": "demo",
            }
        )
    )
    provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(
                endpoint=f"{host}/i/v1/logs",
                headers={"Authorization": f"Bearer {key}"},
                timeout=5,
            )
        )
    )
    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    # Export application logs only, avoiding exporter recursion and SDK payload logs.
    for name in ("anomstack", "anomstack_dashboard"):
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    atexit.register(provider.shutdown)
    logging.getLogger("anomstack").info("PostHog observability initialized")
    return _client


class ObservabilityMiddleware:
    """Capture request failures without changing responses or recording request bodies."""

    def __init__(self, app, client):
        self.app = app
        self.client = client

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        started = time.monotonic()
        status = 500

        async def track_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, track_send)
        except Exception as exc:
            self.client.capture_exception(exc, distinct_id="anomstack-demo-server")
            raise
        finally:
            if scope.get("path") != "/health":
                route = scope.get("route")
                logging.getLogger("anomstack.http").log(
                    logging.ERROR if status >= 500 else logging.INFO,
                    "HTTP request completed",
                    extra={
                        "http.request.method": scope["method"],
                        "http.route": getattr(route, "path", "unmatched"),
                        "http.response.status_code": status,
                        "duration_ms": round((time.monotonic() - started) * 1000, 2),
                    },
                )
