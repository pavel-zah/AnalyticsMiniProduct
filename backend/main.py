import logging
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s - %(name)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("analytics-backend")

try:
    from src.api.router import router
    from src.core.config import settings
except ImportError as e:
    logger.error(f"Failed to import project modules: {e}")
    raise


def create_app() -> FastAPI:
    logger.info(f"Starting {settings.app_name} creation...")

    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("CORS middleware configured with allow_origins=['*']")

    app.include_router(router)
    logger.debug("Main router included")

    @app.get("/", tags=["System"])
    async def root():
        logger.debug("GET / called")
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
        }

    @app.get("/health", tags=["System"])
    async def health():
        return {"status": "ok"}

    logger.info("FastAPI app created successfully")
    return app


app = create_app()

if __name__ == "__main__":
    logger.info("Starting uvicorn server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5030,
        reload=True,
        log_level="debug",
    )
