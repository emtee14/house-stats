from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.deps import get_current_user_with_api_token
from app.models.auth import User
from app.routes.schemas.stats import (
    StatsMetadataResponse,
    StatsTaskCreatedResponse,
    StatsTaskRequest,
    StatsTaskResultResponse,
)
from app.tasks.stats import SUPPORTED_SALES_STATS, get_task_result, run_sales_stats

router = APIRouter(tags=["Statistics"])


@router.get(
    "/sales",
    response_model=StatsMetadataResponse,
    summary="List supported sales statistics",
)
def get_supported_sales_stats(
    user: User = Depends(get_current_user_with_api_token),
) -> StatsMetadataResponse:
    return StatsMetadataResponse(supported_stats=sorted(SUPPORTED_SALES_STATS))


@router.post(
    "/sales/tasks",
    response_model=StatsTaskCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue sales statistics task",
)
def create_sales_stats_task(
    request: StatsTaskRequest,
    user: User = Depends(get_current_user_with_api_token),
) -> StatsTaskCreatedResponse:
    unsupported = sorted(set(request.stats) - set(SUPPORTED_SALES_STATS))
    if unsupported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"unsupported_stats": unsupported},
        )

    task = run_sales_stats.delay(
        stats=request.stats,
        area=request.area,
        area_type=request.area_type,
        start_date=request.start_date.isoformat() if request.start_date else None,
        end_date=request.end_date.isoformat() if request.end_date else None,
    )
    return StatsTaskCreatedResponse(task_id=task.id, status=task.status)


@router.get(
    "/sales/tasks/{task_id}",
    response_model=StatsTaskResultResponse,
    summary="Get sales statistics task result",
)
def get_sales_stats_task_result(
    task_id: UUID,
    user: User = Depends(get_current_user_with_api_token),
) -> StatsTaskResultResponse:
    task = get_task_result(task_id)
    result = None
    error = None

    if task.successful():
        result = task.result
    elif task.failed():
        error = str(task.result)

    return StatsTaskResultResponse(
        task_id=task_id,
        status=task.status,
        result=result,
        error=error,
    )
