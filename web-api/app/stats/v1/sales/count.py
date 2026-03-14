from typing import Dict

from app.stats.base import Statistic

import polars as pl

class CountHousePrice(Statistic):
    name = "count_price"
    description = "Count the total sales"

    async def _compute(self, data: pl.DataFrame) -> Dict:
        # aggregate monthly counts for all types
        df_all = (
            data.sort("date")
            .group_by_dynamic("date", every="1mo")
            .agg(pl.len().alias("count"))
            .upsample("date", every="1mo")
        )

        result = {}

        for date, val in zip(df_all["date"], df_all["count"]):
            result[str(date)] = {"all": val}

        # compute counts per sales type
        for t, part in data.partition_by("type", as_dict=True).items():
            # partition_by returns tuple keys; unwrap to plain string
            if isinstance(t, tuple):
                t = t[0]
            df_type = (
                part.sort("date")
                .group_by_dynamic("date", every="1mo")
                .agg(pl.len().alias("count"))
                .upsample("date", every="1mo")
            )

            for date, val in zip(df_type["date"], df_type["count"]):
                key = str(date)
                result.setdefault(key, {"all": None})
                result[key][t] = val

        return result


class CountHouseTypes(Statistic):
    name = "count_house_types"
    description = "Count different types of houses"

    async def _compute(self, data: pl.DataFrame) -> Dict[str, int]:
        unique_data = data.unique(subset="houseid")

        df = unique_data.group_by("type").agg(
            pl.len().alias("count")
        )

        result = {"all": unique_data.height}
        result.update(dict(zip(df["type"], df["count"])))

        return result