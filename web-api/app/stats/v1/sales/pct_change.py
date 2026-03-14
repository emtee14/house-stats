from typing import Dict
import polars as pl

from app.stats.base import Statistic


class PctChangeHousePrice(Statistic):
    name = "pct_change_price"
    description = "The percent change of a sales price"

    async def _compute(self, data: pl.DataFrame) -> Dict[str, float]:
        periods = {
            "monthly": "1mo",
            "quarterly": "3mo",
            "half_year": "6mo",
            "yearly": "12mo",
        }

        result = {}

        for name, every in periods.items():
            # compute for all types combined
            df_all = self._calc_period_perc(data, every)

            period_dict = {}

            for date, val in zip(df_all["date"], df_all["pct_change"]):
                period_dict[str(date)] = {"all": val}

            # compute per type
            for t, part in data.partition_by("type", as_dict=True).items():
                if isinstance(t, tuple):
                    t = t[0]
                df_type = self._calc_period_perc(part, every)

                for date, val in zip(df_type["date"], df_type["pct_change"]):
                    key = str(date)
                    period_dict.setdefault(key, {"all": None})
                    period_dict[key][t] = val

            result[name] = period_dict

        return result


    def _calc_period_perc(self, df: pl.DataFrame, every: str) -> pl.DataFrame:
        df = (
            df.sort("date")
                .group_by_dynamic("date", every=every)
                .agg(pl.col("price").mean().alias("price"))
                .upsample("date", every=every)
        )

        periods_per_year = {
            "1mo": 12,
            "3mo": 4,
            "6mo": 2,
            "12mo": 1,
        }

        lag = periods_per_year[every]

        df = df.with_columns(
            (
                (pl.col("price") / pl.col("price").shift(lag) - 1) * 100
            ).alias("pct_change")
        )

        return df
