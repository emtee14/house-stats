from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class StatsTaskRequest(BaseModel):
    stats: list[str]
    area: str
    area_type: str
    start_date: date | None = None
    end_date: date | None = None


class StatsTaskCreatedResponse(BaseModel):
    task_id: str
    status: str = "PENDING"


class StatsTaskResultResponse(BaseModel):
    task_id: UUID | str
    status: str
    result: dict | list | str | int | float | None = None
    error: str | None = None


class StatsMetadataResponse(BaseModel):
    supported_stats: list[str] = Field(default_factory=list)
