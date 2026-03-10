import pytest

from app.models.billing import Usage
from tests.common import db_session, engine, config


@pytest.fixture
def create_usage(db_session):
    def _create_usage(user, api_route, tokens, timestamp):
        new_record = Usage(
            user_id=user.id,
            api_route=api_route,
            tokens=tokens,
            timestamp=timestamp,
        )
        db_session.add(new_record)
        db_session.commit()
        return new_record

    return _create_usage
