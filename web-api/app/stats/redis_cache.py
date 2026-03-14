import json
from typing import Any, Dict

import redis


class RedisAggCache:
    def __init__(self, redis_url: str) -> None:
        self._redis = redis.Redis.from_url(redis_url)

    def check_cache(self, aggregation: str, data_id: str) -> Dict[str, float] | None:
        result = self._redis.get(f"{data_id}-{aggregation}")
        if result is not None:
            return json.loads(result)

        return None

    def cache_agg(self, aggregation: str, data_id: str, data: Dict[str, Any]):
        self._redis.set(
            f"{data_id}-{aggregation}",
            json.dumps(data, default=str),
        )
