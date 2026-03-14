from typing import Dict
import polars as pl

from app.stats.base import Statistic


class SaleVolumeHousePrice(Statistic):
    name = "sale_volume"
    description = "Total sales volume for time periods 1mo, 3mo, 6mo, and 12mo"

    async def _compute(self, data: pl.DataFrame) -> Dict:
        periods = {
            "monthly": "1mo",
            "quarterly": "3mo",
            "half_year": "6mo",
            "yearly": "12mo",
        }

        result = {}

        for name, every in periods.items():
            # total volume for all types
            df_all = (
                data.sort("date")
                .group_by_dynamic("date", every=every)
                .agg(pl.col("price").sum().alias("volume"))
                .upsample("date", every=every)
            )

            period_dict = {}

            for date, volume in zip(df_all["date"], df_all["volume"]):
                period_dict[str(date)] = {"all": volume}

            # add type-specific values
            for row in (
                data.sort("date")
                .group_by_dynamic("date", every=every, by="type")
                .agg(pl.col("price").sum().alias("volume"))
            ).iter_rows(named=True):
                date = str(row["date"])
                t = row["type"]
                v = row["volume"]
                period_dict.setdefault(date, {"all": None})
                period_dict[date][t] = v

            result[name] = period_dict

        return result
