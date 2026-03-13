from datetime import datetime, UTC

from tests.common import config, engine
from app.data.sales import SalesDataset

def test_sales_dataset(engine):
    dataset = SalesDataset(engine)
    df = dataset.query("area", "LS",
                       datetime(1995, 1, 1), datetime.now(UTC))
    print(df)