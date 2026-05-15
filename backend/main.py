import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("[STARTUP] Starting application initialization...")
print("=" * 80)

try:
    print("[STARTUP] Importing router...")
    from src.api import router
    print("[STARTUP] Router imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import router: {e}")
    import traceback
    traceback.print_exc()
    raise

try:
    print("[STARTUP] Importing settings...")
    from src.core.config import settings
    print(f"[STARTUP] Settings imported: app_name={settings.app_name}")
except Exception as e:
    print(f"[ERROR] Failed to import settings: {e}")
    import traceback
    traceback.print_exc()
    raise


def create_app() -> FastAPI:
    print("[STARTUP] Creating FastAPI app...")
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    print(f"[DEBUG] FastAPI app created: {settings.app_name} v{settings.app_version}")

    # Add CORS middleware
    print("[DEBUG] Adding CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (adjust for production)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print(f"[DEBUG] CORS middleware added - allow_origins=['*']")

    print("[DEBUG] Including router...")
    app.include_router(router.router)
    print(f"[DEBUG] Router included with prefix: /v1")

    @app.get("/")
    async def root():
        print("[DEBUG] GET / called")
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
        }
    
    @app.get("/health")
    async def health():
        print("[DEBUG] GET /health called")
        return {"status": "ok"}

    print("[STARTUP] FastAPI app created successfully")
    return app


print("[STARTUP] Calling create_app()...")
try:
    app = create_app()
    print("[STARTUP] ✓ App created successfully")
except Exception as e:
    print(f"[ERROR] Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    raise

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("[STARTUP] Starting uvicorn server...")
    print("=" * 80)

    uvicorn.run(
        "main:app",
        host="localhost",
        port=5030,
        reload=True,
        log_level="debug",
    )
