from typing import Dict

import polars as pl
from sqlalchemy import text
from sqlmodel import Session


class BaseDataset:
    def __init__(self, session: Session):
        self._session = session

    def run_query(self, sql: str, parameters: Dict):
        result = self._session.execute(text(sql), parameters)
        columns = list(result.keys())
        rows = result.fetchall()

        return pl.DataFrame(rows, schema=columns)