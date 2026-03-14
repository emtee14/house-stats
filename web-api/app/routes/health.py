from fastapi import APIRouter

from app.routes.schemas.health import HealthResponse

router = APIRouter(tags=["Miscellaneous"])


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns a simple status payload to confirm that the API is reachable.",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
