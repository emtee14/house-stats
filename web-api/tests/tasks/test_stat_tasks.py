import pytest
from datetime import datetime
import polars as pl

from app.tasks.stats import (
    mean_house_price,
    sale_volume,
    count_house_price,
    count_house_types,
    most_expensive_sale,
    pct_change_house_price,
    standard_dev_house_price,
    average_house_tenancy,
)


class FakeDataset:
    def __init__(self, *_):
        pass

    @staticmethod
    def build_data_id(*_):
        return "test-data-id"

    def query(self, **_):
        df = pl.DataFrame(
            {
                "price": [100000, 200000, 300000],
                "type": ["D", "D", "S"],
                "date": [
                    datetime(2000, 1, 1),
                    datetime(2000, 2, 1),
                    datetime(2000, 3, 1),
                ],
                "houseid": [1, 1, 2],
            }
        )

        return df, "test-data-id"


class FakeCache:
    def __init__(self, *_):
        pass

    def check_cache(self, *_):
        return None

    def cache_agg(self, *_):
        return None


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):

    from app.tasks import stats

    monkeypatch.setattr(stats, "SalesDataset", FakeDataset)
    monkeypatch.setattr(stats, "RedisAggCache", FakeCache)


AREA = "LS1"
AREA_TYPE = "postcode"
START = datetime(1999, 1, 1)
END = datetime(2005, 1, 1)


def test_mean_house_price_task():
    result = mean_house_price(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)
    print(result)


def test_sale_volume_task():
    result = sale_volume(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_count_house_price_task():
    result = count_house_price(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_count_house_types_task():
    result = count_house_types(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_most_expensive_sale_task():
    result = most_expensive_sale(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_pct_change_house_price_task():
    result = pct_change_house_price(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_standard_dev_house_price_task():
    result = standard_dev_house_price(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)


def test_average_house_tenancy_task():
    result = average_house_tenancy(AREA, AREA_TYPE, START, END, session=None)
    assert isinstance(result, dict)
