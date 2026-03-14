from abc import ABC, abstractmethod
from typing import Dict


class AggCache(ABC):
    @abstractmethod
    def check_cache(self, aggregation: str, data_id: str) -> Dict[str, float] | None:
        pass

    @abstractmethod
    def cache_agg(self, aggregation: str, data_id: str, data: Dict[str, float]):
        pass