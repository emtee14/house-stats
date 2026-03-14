from datetime import datetime, UTC

from sqlmodel import Session

from tests.common import *
from app.data.sales import SalesDataset

def test_sales_dataset(db_session: Session):
    dataset = SalesDataset(db_session)
    df = dataset.query("area", "LS",
                       datetime(1995, 1, 1), datetime.now(UTC))
    print(df)