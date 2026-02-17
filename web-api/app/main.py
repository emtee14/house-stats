from fastapi import FastAPI

from routes.router import router as api_router
from config import Config


def create_app() -> FastAPI:
    app = FastAPI(
        title="House Stats API",
        version="0.1",
    )

    # ===== Routes ====
    app.include_router(api_router)

    return app


app = create_app()

app