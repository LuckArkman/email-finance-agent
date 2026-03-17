import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import BaseAPIConfig
from app.mongo import init_mongo_client, close_mongo_client
from app.api.websockets import EventBroadcaster
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from app.obfuscator import SensitiveDataFilter
from app.telemetry import TelemetryManager
from fastapi import Response

limiter = Limiter(key_func=get_remote_address)

# Initialize Sentry
TelemetryManager.setup_sentry()

# Setup logging with obfuscation filter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")
logger.addFilter(SensitiveDataFilter())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initialize MongoDB Client")
    await init_mongo_client()
    
    # Fire and forget the Redis listener loop
    redis_listener_task = asyncio.create_task(EventBroadcaster.listen_to_redis_events())
    
    yield
    # Shutdown
    print("Closing MongoDB Client")
    redis_listener_task.cancel()
    await close_mongo_client()

def create_fastapi_app() -> FastAPI:
    """Factory function to initialize and configure the FastAPI application."""
    settings = BaseAPIConfig.get_settings()
    from app.tenant import TenantSecurityMiddleware
    
    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version="1.0.0",
        lifespan=lifespan
    )
    
    app.add_middleware(TenantSecurityMiddleware)
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/health", tags=["Health"])
    def app_health_status() -> dict[str, str]:
        """Health check endpoint to verify API is running."""
        return {"status": "ok", "environment": settings.environment}

    @app.get("/metrics", tags=["Telemetry"])
    def get_app_metrics():
        """Prometheus metrics endpoint for Grafana scraping."""
        content, media_type = TelemetryManager.get_metrics_latest()
        return Response(content=content, media_type=media_type)

    from app.ingestion.webhooks import router as ingestion_router
    from app.api.auth import router as auth_router
    from app.api.invoices import router as invoices_router
    from app.api.analytics import router as analytics_router
    from app.api.websockets import router as websockets_router
    from app.api.settings import router as settings_router

    app.include_router(ingestion_router)
    app.include_router(auth_router)
    app.include_router(invoices_router)
    app.include_router(analytics_router)
    app.include_router(websockets_router)
    app.include_router(settings_router)

    return app

app = create_fastapi_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
