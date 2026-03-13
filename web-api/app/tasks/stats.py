from datetime import datetime

import asyncio

from sqlmodel import Session

from app.config import Config
from app.celery import celery_worker
from app.data.sales import SalesDataset
from app.stats.redis_cache import RedisAggCache

from app.stats.v1.sales.mean import MeanHousePrice
from app.stats.v1.sales.count import CountHousePrice, CountHouseTypes
from app.stats.v1.sales.most_expensive import MostExpensiveSale
from app.stats.v1.sales.pct_change import PctChangeHousePrice
from app.stats.v1.sales.sale_volume import SaleVolumeHousePrice
from app.stats.v1.sales.standard_dev import StandardDevHousePrice
from app.stats.v1.sales.tenancy import AverageHouseTenancy
from app.tasks.base_task import DatabaseTask


def run_stat(stat_cls, area: str, area_type: str, start: datetime, end: datetime, db_engine):

    dataset = SalesDataset(db_engine)
    cache = RedisAggCache(Config.REDIS_AGG_CACHE)

    data = dataset.query(
        area_type=area_type,
        area=area,
        start_date=start,
        end_date=end,
    )

    stat = stat_cls(cache)

    return asyncio.run(stat.compute(data))


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

