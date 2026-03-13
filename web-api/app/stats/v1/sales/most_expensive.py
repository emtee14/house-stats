from typing import Dict

from app.stats.base import Statistic
from app.stats.registry import register

import polars as pl


@register("v1", "most_expensive_sale")
class MostExpensiveSale(Statistic):
    name = "most_expensive_sale"
    description = "Most expensive sale"

    async def _compute(self, data: pl.DataFrame) -> Dict[str, float]:
        df = data.group_by("type").agg(
            pl.col("price").max().alias("max_price")
        )

        result = dict(
            zip(
                df["type"],
                df["max_price"]
            )
        )

        return result