from fastapi import FastAPI

from app.routes.router import router as api_router
from app.config import Config


def create_app() -> FastAPI:
    app = FastAPI(
        title="House Stats API",
        version="0.1",
        openapi_tags=[
            {"name": "Authentication", "description": "Login and registration endpoints"},
            {"name": "Users", "description": "User management operations"},
            {"name": "Miscellaneous", "description": "Miscellaneous endpoints"},
        ],
        docs_url=None,
        redoc_url="/docs"
    )

    # ===== Routes ====
    app.include_router(api_router)

    return app
