import polars as pl
import pytest
from datetime import datetime, timedelta

from app.stats.v1.sales.mean import MeanHousePrice
from app.stats.v1.sales.count import CountHousePrice, CountHouseTypes
from app.stats.v1.sales.most_expensive import MostExpensiveSale
from app.stats.v1.sales.pct_change import PctChangeHousePrice
from app.stats.v1.sales.sale_volume import SaleVolumeHousePrice
from app.stats.v1.sales.standard_dev import StandardDevHousePrice
from app.stats.v1.sales.tenancy import AverageHouseTenancy
from tests.stats.common import TestCache


@pytest.mark.asyncio
async def test_mean_house_price():
    cache = TestCache()

    sales = pl.DataFrame({
        "price": [100_000, 200_000, 300_000],
        "type": ["D", "D", "D"],
    }), "data-id"

    stat = MeanHousePrice(cache)

    result = await stat.compute(sales)

    assert result["all"] == 200_000
    assert result["D"] == 200_000


@pytest.mark.asyncio
async def test_count_house_price():
    cache = TestCache()

    sales = pl.DataFrame({
        "price": [100_000, 200_000, 300_000],
        "type": ["D", "D", "D"],
        "date": [datetime(2000,1,1), datetime(2000,1,1), datetime(2000,1,1)],
    }, schema={"date": pl.Date, "price": int, "type": str}), "data-id"

    stat = CountHousePrice(cache)
    result = await stat.compute(sales)

    assert result["2000-01-01"]["all"] == 3
    assert result["2000-01-01"]["D"] == 3

@pytest.mark.asyncio
async def test_std_house_price():
    cache = TestCache()

    sales = pl.DataFrame({
        "price": [100_000, 200_000, 300_000],
        "type": ["D", "D", "D"],
    }), "data-id"

    stat = StandardDevHousePrice(cache)

    result = await stat.compute(sales)

    assert result["all"] == 100_000
    assert result["D"] == 100_000


@pytest.mark.asyncio
async def test_pct_change_house_price_month():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000],
            "type": ["D","D","D"],
            "date": [datetime(2000, 1, 1), datetime(2001, 1, 1), datetime(2002, 1, 1)],
        },
        schema={"date": pl.Date, "price": int, "type": str},
    ), "data-id"

    stat = PctChangeHousePrice(cache)
    result = await stat.compute(sales)

    assert result["monthly"]["2001-01-01"]["all"] == 100
    assert result["monthly"]["2002-01-01"]["all"] == 50

@pytest.mark.asyncio
async def test_pct_change_house_price_quarter():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000],
            "type": ["D","D","D"],
            "date": [datetime(2000, 1, 1), datetime(2001, 1, 1), datetime(2002, 1, 1)],
        },
        schema={"date": pl.Date, "price": int, "type": str},
    ), "data-id"

    stat = PctChangeHousePrice(cache)
    result = await stat.compute(sales)

    assert result["quarterly"]["2001-01-01"]["all"] == 100
    assert result["quarterly"]["2002-01-01"]["all"] == 50

@pytest.mark.asyncio
async def test_pct_change_house_price_6mo():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000],
            "type": ["D","D","D"],
            "date": [datetime(2000, 1, 1), datetime(2001, 1, 1), datetime(2002, 1, 1)],
        },
        schema={"date": pl.Date, "price": int, "type": str},
    ), "data-id"

    stat = PctChangeHousePrice(cache)
    result = await stat.compute(sales)

    assert result["half_year"]["2001-01-01"]["all"] == 100
    assert result["half_year"]["2002-01-01"]["all"] == 50


@pytest.mark.asyncio
async def test_pct_change_house_price_year():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000],
            "type": ["D","D","D"],
            "date": [datetime(2000, 1, 1), datetime(2001, 1, 1), datetime(2002, 1, 1)],
        },
        schema={"date": pl.Date, "price": int, "type": str},
    ), "data-id"

    stat = PctChangeHousePrice(cache)
    result = await stat.compute(sales)

    assert result["yearly"]["2001-01-01"]["all"] == 100
    assert result["yearly"]["2002-01-01"]["all"] == 50

@pytest.mark.asyncio
async def test_house_type_count():
    cache = TestCache()

    sales = pl.DataFrame({
        "price": [100_000, 200_000, 300_000, 100_000, 100_000],
        "type": ["D", "D", "D", "D","S"],
        "houseid": ["house1","house2","house3","house1","house4"],
    },
    ), "data-id"

    stat = CountHouseTypes(cache)
    result = await stat.compute(sales)
    assert result["D"] == 3
    assert result["S"] == 1


@pytest.mark.asyncio
async def test_sales_volume():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000, 100_000, 100_000],
            "type": ["D", "D", "D", "S","S"],
            "date": [datetime(2001, 1, 1), datetime(2001, 1, 1), datetime(2002, 1, 1), datetime(2002, 1, 1),
                     datetime(2002, 1, 1)],
        },
        schema={"date": pl.Date, "price": int, "type": str},
    ), "data-id"

    stat = SaleVolumeHousePrice(cache)
    result = await stat.compute(sales)
    assert result["monthly"]["2001-01-01"]["all"] == 300_000
    assert result["monthly"]["2002-01-01"]["all"] == 500_000

    assert result["quarterly"]["2001-01-01"]["all"] == 300_000
    assert result["quarterly"]["2002-01-01"]["all"] == 500_000

    assert result["half_year"]["2001-01-01"]["all"] == 300_000
    assert result["half_year"]["2002-01-01"]["all"] == 500_000

    assert result["yearly"]["2001-01-01"]["all"] == 300_000
    assert result["yearly"]["2002-01-01"]["all"] == 500_000


@pytest.mark.asyncio
async def test_avg_house_tenancy():
    cache = TestCache()

    sales = pl.DataFrame({
            "price": [100_000, 200_000, 300_000, 100_000, 100_000, 100_000],
            "type": ["D", "D", "D", "D", "D", "D"],
            "date": [datetime(2001, 1, 1), datetime(2001, 1, 1),
                     datetime(2001, 1, 1), datetime(2002, 1, 1),
                     datetime(2002, 1, 1), datetime(2002, 1, 1)],
            "houseid": ["house1", "house2", "house3", "house1", "house2", "house3"],
        },
        schema={"date": pl.Date, "price": int, "type": str, "houseid": str},
    ), "data-id"

    stat = AverageHouseTenancy(cache)

    result = await stat.compute(sales)

    assert result["all"] == timedelta(days=365)
    assert result["D"] == timedelta(days=365)


@pytest.mark.asyncio
async def test_most_expensive():
    cache = TestCache()
    sales = pl.DataFrame({
        "price": [100_000, 200_000, 300_000, 100_000, 100_000, 100_000],
        "type": ["D", "D", "D", "D", "D", "S"],
    }), "data-id"

    stat = MostExpensiveSale(cache)

    result = await stat.compute(sales)

    assert result["D"] == 300_000
    assert result["S"] == 100_000