from fastapi import FastAPI
from app.config import BaseAPIConfig

def create_fastapi_app() -> FastAPI:
    """Factory function to initialize and configure the FastAPI application."""
    settings = BaseAPIConfig.get_settings()
    
    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version="1.0.0"
    )

    @app.get("/health", tags=["Health"])
    def app_health_status() -> dict[str, str]:
        """Health check endpoint to verify API is running."""
        return {"status": "ok", "environment": settings.environment}

    return app

app = create_fastapi_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
