from typing import Dict

from app.stats.base import Statistic
from app.stats.registry import register

import polars as pl


@register("v1", "mean_price")
class MeanHousePrice(Statistic):
    name = "mean_price"
    description = "Average sale price"

    async def _compute(self, data: pl.DataFrame) -> Dict:
        df = data.group_by("type").agg(
            pl.col("price").mean().alias("mean_price")
        )

        result = {"all": data["price"].mean()}
        result.update(dict(zip(df["type"], df["mean_price"])))

        return result
