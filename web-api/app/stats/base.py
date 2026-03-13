from abc import ABC, abstractmethod
from typing import Tuple, Dict

from app.stats.cache import AggCache

import polars as pl

class Statistic(ABC):
    name: str
    description: str

    deprecated: bool = False
    deprecated_in: str | None = None

    def __init__(self, cache: AggCache):
        self._cache = cache

    @abstractmethod
    async def _compute(self, data: pl.DataFrame) -> Dict:
        pass

    async def compute(self, data: Tuple[pl.DataFrame, str]):
        result = self._cache.check_cache(self.name, data[1])
        if result:
            return result
        else:
            return await self._compute(data[0])