from pydantic import BaseModel
from datetime import date


class StatsRequest(BaseModel):
    stats: list[str]
    start_date: date | None = None
    end_date: date | None = None


class StatsResponse(BaseModel):
    version: str
    results: dict
    charged: int
