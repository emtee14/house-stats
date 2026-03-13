from typing import Dict

from app.stats.base import Statistic

import polars as pl

class StandardDevHousePrice(Statistic):
    name = "std_house_price"
    description = "Standard deviation of sale price"

    async def _compute(self, data: pl.DataFrame) -> Dict[str, float]:
        df = data.group_by("type").agg(
            pl.col("price").std().alias("std_price")
        )

        result = {"all": data["price"].std()}
        result.update(dict(zip(df["type"], df["std_price"])))

        return result