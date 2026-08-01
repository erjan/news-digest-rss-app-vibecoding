from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine

from .log import log
from .settings import settings

_tracing_provider_configured = False
_sqlalchemy_instrumented = False


def configure_tracing(app: FastAPI, async_engine: AsyncEngine) -> None:
    """Configure OpenTelemetry tracing for FastAPI and SQLAlchemy."""
    if not settings.otel_enabled:
        return

    global _tracing_provider_configured, _sqlalchemy_instrumented

    if not _tracing_provider_configured:
        resource = Resource.create({"service.name": settings.otel_service_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint,
            insecure=settings.otel_exporter_otlp_insecure,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracing_provider_configured = True
        log.info(
            "otel_provider_configured",
            service_name=settings.otel_service_name,
            otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        )

    if not _sqlalchemy_instrumented:
        SQLAlchemyInstrumentor().instrument(engine=async_engine.sync_engine)
        _sqlalchemy_instrumented = True
        log.info("otel_sqlalchemy_instrumented")

    if not getattr(app.state, "otel_fastapi_instrumented", False):
        FastAPIInstrumentor.instrument_app(app)
        app.state.otel_fastapi_instrumented = True
        log.info("otel_fastapi_instrumented")
