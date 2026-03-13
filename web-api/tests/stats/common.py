from typing import Dict

from app.stats.cache import AggCache


class TestCache(AggCache):
    def __init__(self):
        self.cache = {}

    def check_cache(self, aggregation: str, data_id: str) -> Dict[str, float] | None:
        try:
            return self.cache[aggregation]
        except KeyError:
            return None

    def cache_agg(self, aggregation: str, data_id: str, data: Dict[str, float]):
        self.cache[aggregation] = data
