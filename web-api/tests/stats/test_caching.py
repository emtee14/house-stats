import pytest

from tests.stats.common import TestCache
from app.stats.v1.sales.mean import MeanHousePrice

import polars as pl

@pytest.mark.asyncio
async def test_empty_cache():
    cache = TestCache()
    cache.cache_agg("mean_price","data-id", {"mean_price": 100_000})

    sales = pl.DataFrame({"price": [100_000, 200_000, 300_000]}), "data-id"

    stat = MeanHousePrice(cache)

    result = await stat.compute(sales)

    assert result["mean_price"] == 100_000