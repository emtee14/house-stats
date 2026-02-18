from fastapi import FastAPI

from app.routes.router import router as api_router
from app.config import Config


def create_app() -> FastAPI:
    app = FastAPI(
        title="House Stats API",
        version="0.1",
    )

    # ===== Routes ====
    app.include_router(api_router)

    return app
