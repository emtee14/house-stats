import json
from typing import Dict

import redis


class RedisAggCache:
    def __init__(self, redis_url: str) -> None:
        self._redis = redis.Redis.from_url(redis_url)

    def check_cache(self, aggregation: str, data_id: str) -> Dict[str, float] | None:
        result = self._redis.get(f"{data_id}-{aggregation}")
        if result is not None:
            return json.loads(result)

        return None
