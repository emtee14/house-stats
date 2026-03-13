from typing import Dict

import polars as pl
from sqlalchemy import text


class BaseDataset:
    def __init__(self, db):
        self._engine = db

    def run_query(self, sql: str, parameters: Dict):
        with self._engine.connect() as conn:
            result = conn.execute(text(sql), parameters)
            columns = result.keys()
            rows = result.fetchall()

        return pl.DataFrame(rows, schema=columns)