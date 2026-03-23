import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from app.config import BaseAPIConfig

# Create a custom registry for Prometheus
registry = CollectorRegistry()

# Define Prometheus metrics
INVOICE_PROCESSED_COUNT = Counter(
    "invoice_processed_total", 
    "Total number of invoices processed", 
    ["status", "tenant_id"],
    registry=registry
)

AI_EXTRACTION_LATENCY = Histogram(
    "ai_extraction_latency_seconds", 
    "Latencies of AI extraction in seconds", 
    ["tenant_id"],
    registry=registry
)

class TelemetryManager:
    """
    Handles MLOps observablity: Error tracking (Sentry) and Performance metrics (Prometheus).
    """
    
    @staticmethod
    def setup_sentry():
        settings = BaseAPIConfig.get_settings()
        
        # Pull from env or settings if available. 
        # For now, it's safer to only skip if it's the known internal placeholder or empty.
        dsn = getattr(settings, "sentry_dsn", "")
        
        if not dsn or "your-sentry-dsn" in dsn:
            print("Sentry DSN not provided or is placeholder. Skipping init.")
            return

        try:
            sentry_sdk.init(
                dsn=dsn,
                integrations=[FastApiIntegration()],
                traces_sample_rate=1.0,
                profiles_sample_rate=1.0,
                environment=settings.environment
            )
            print(f"Sentry initialized in - {settings.environment} mode.")
        except Exception as e:
            print(f"Failed to initialize Sentry: {e}")

    @staticmethod
    def capture_exception_sentry(exc: Exception):
        """Captures an exception and sends it to Sentry."""
        sentry_sdk.capture_exception(exc)

    @staticmethod
    def push_metric(metric_name: str, **labels):
        """Increments a counter or records a value in Prometheus."""
        if metric_name == "invoice_processed":
            INVOICE_PROCESSED_COUNT.labels(**labels).inc()
        elif metric_name == "ai_extraction_latency":
            # This would be a context manager in real usage, but for the manager:
            # AI_EXTRACTION_LATENCY.labels(**labels).observe(value)
            pass

    @staticmethod
    def get_metrics_latest():
        """Returns the latest Prometheus metrics in text format."""
        return generate_latest(registry), CONTENT_TYPE_LATEST
