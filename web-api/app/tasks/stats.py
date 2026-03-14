import asyncio
import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from uuid import UUID

from celery.result import AsyncResult
from sqlmodel import Session

from app.celery import celery_worker
from app.data.sales import SalesDataset
from app.settings import get_settings
from app.stats.redis_cache import RedisAggCache
from app.stats.v1.sales.count import CountHousePrice, CountHouseTypes
from app.stats.v1.sales.mean import MeanHousePrice
from app.stats.v1.sales.most_expensive import MostExpensiveSale
from app.stats.v1.sales.pct_change import PctChangeHousePrice
from app.stats.v1.sales.sale_volume import SaleVolumeHousePrice
from app.stats.v1.sales.standard_dev import StandardDevHousePrice
from app.stats.v1.sales.tenancy import AverageHouseTenancy
from app.tasks.base_task import DatabaseTask

settings = get_settings()

SALES_STAT_CLASSES = {
    MeanHousePrice.name: MeanHousePrice,
    SaleVolumeHousePrice.name: SaleVolumeHousePrice,
    CountHousePrice.name: CountHousePrice,
    CountHouseTypes.name: CountHouseTypes,
    MostExpensiveSale.name: MostExpensiveSale,
    PctChangeHousePrice.name: PctChangeHousePrice,
    StandardDevHousePrice.name: StandardDevHousePrice,
    AverageHouseTenancy.name: AverageHouseTenancy,
}
SUPPORTED_SALES_STATS = frozenset(SALES_STAT_CLASSES)


def run_stat(stat_cls, area: str, area_type: str,
             start: datetime, end: datetime, db_session: Session):
    dataset = SalesDataset(db_session)
    cache = RedisAggCache(settings.redis_agg_cache)
    data_id = dataset.build_data_id(area_type, area, start, end)
    stat = stat_cls(cache)

    cached = cache.check_cache(stat.name, data_id)
    if cached is not None:
        return cached

    data = dataset.query(
        area_type=area_type,
        area=area,
        start_date=start,
        end_date=end,
    )

    return asyncio.run(stat.compute(data))


def _parse_task_datetime(value: str | None, default: datetime) -> datetime:
    if value is None:
        return default
    return datetime.fromisoformat(value)

def get_task_result(task_id: str) -> AsyncResult:
    return AsyncResult(str(task_id), app=celery_worker)


@celery_worker.task(name="stats.run_sales_stats", base=DatabaseTask)
def run_sales_stats(
    stats: list[str],
    area: str,
    area_type: str,
    start_date: str | None = None,
    end_date: str | None = None,
    session: Session = None,
) -> dict[str, Any]:
    start = _parse_task_datetime(start_date, datetime.min)
    end = _parse_task_datetime(end_date, datetime.max)

    results = {}
    for stat_name in stats:
        stat_cls = SALES_STAT_CLASSES[stat_name]
        results[stat_name] = run_stat(stat_cls, area, area_type, start, end, session)

    return {
        "results": results,
        "area": area,
        "area_type": area_type,
        "start_date": start_date,
        "end_date": end_date,
    }


@celery_worker.task(name="stats.mean_house_price", base=DatabaseTask)
def mean_house_price(area, area_type, start, end, session: Session = None,):
    return run_stat(MeanHousePrice, area, area_type, start, end, session)


@celery_worker.task(name="stats.sale_volume", base=DatabaseTask)
def sale_volume(area, area_type, start, end, session: Session = None,):
    return run_stat(SaleVolumeHousePrice, area, area_type, start, end, session)


@celery_worker.task(name="stats.count_house_price", base=DatabaseTask)
def count_house_price(area, area_type, start, end, session: Session = None):
    return run_stat(CountHousePrice, area, area_type, start, end, session)


@celery_worker.task(name="stats.count_house_types", base=DatabaseTask)
def count_house_types(area, area_type, start, end, session: Session = None):
    return run_stat(CountHouseTypes, area, area_type, start, end, session)


@celery_worker.task(name="stats.most_expensive_sale", base=DatabaseTask)
def most_expensive_sale(area, area_type, start, end, session: Session = None):
    return run_stat(MostExpensiveSale, area, area_type, start, end, session)


@celery_worker.task(name="stats.pct_change_house_price", base=DatabaseTask)
def pct_change_house_price(area, area_type, start, end, session: Session = None):
    return run_stat(PctChangeHousePrice, area, area_type, start, end, session)


@celery_worker.task(name="stats.standard_dev_house_price", base=DatabaseTask)
def standard_dev_house_price(area, area_type, start, end, session: Session = None):
    return run_stat(StandardDevHousePrice, area, area_type, start, end, session)


@celery_worker.task(name="stats.average_house_tenancy", base=DatabaseTask)
def average_house_tenancy(area, area_type, start, end, session: Session = None):
    return run_stat(AverageHouseTenancy, area, area_type, start, end, session)
