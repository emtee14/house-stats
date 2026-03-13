from typing import Dict

from app.stats.base import Statistic

import polars as pl

class AverageHouseTenancy(Statistic):
    name = "avg_house_tenancy"
    description = "Average tenancy for houses in that area"

    async def _compute(self, data: pl.DataFrame) -> Dict[str, float]:
        # compute tenancy durations per sales
        df = (
            data.sort("date")
            .group_by("houseid", maintain_order=True)
            .agg((pl.col("date") - pl.col("date").shift()).alias("tenancy"))
            .explode("tenancy")
            .filter(pl.col("tenancy").is_not_null())
        )

        # overall average
        result = {"all": df["tenancy"].mean()}

        # per type average
        df_type = (
            data.sort("date")
            .group_by(["houseid", "type"], maintain_order=True)
            .agg((pl.col("date") - pl.col("date").shift()).alias("tenancy"))
            .explode("tenancy")
            .filter(pl.col("tenancy").is_not_null())
            .group_by("type")
            .agg(pl.col("tenancy").mean().alias("avg_tenancy"))
        )

        result.update(dict(zip(df_type["type"], df_type["avg_tenancy"])))

        return result