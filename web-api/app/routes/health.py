from fastapi import APIRouter

from app.routes.schemas.health import HealthResponse

router = APIRouter(tags=["Miscellaneous"])


@router.get("/")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
