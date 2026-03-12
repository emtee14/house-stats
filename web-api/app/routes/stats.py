from fastapi import APIRouter, Depends

from app.billing.deps import bill_tokens
from app.routes.deps import get_data_access
from app.routes.schemas.stats import StatsRequest, StatsResponse

router = APIRouter()


@router.get("/area_summary")
async def stats(
    request: StatsRequest,
    data_access=Depends(get_data_access),
    _=Depends(bill_tokens(5)),
) -> StatsResponse:
    return StatsResponse(version="v1", results={"test": "results"}, charged=5)
