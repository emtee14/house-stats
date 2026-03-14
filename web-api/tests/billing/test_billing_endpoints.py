from datetime import datetime, timedelta
from dateutil.tz import UTC
from fastapi.testclient import TestClient
from urllib.parse import urlencode

from tests.common import *
from tests.auth.common import create_user, login_user

from app.models.billing import Usage, BillingLedger
from app.models.auth import User


def test_get_api_usage_e2e(client: TestClient, db_session, create_user, login_user):

    # Create a user
    user: User = create_user("usage@test.com", "test", "user", "Password")


    token = login_user("usage@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(UTC)

    # Insert usage records
    usage1 = Usage(
        user_id=user.id,
        api_route="/stats/mean",
        tokens=5,
        timestamp=now - timedelta(hours=1),
    )

    usage2 = Usage(
        user_id=user.id,
        api_route="/stats/count",
        tokens=3,
        timestamp=now - timedelta(minutes=30),
    )

    db_session.add(usage1)
    db_session.add(usage2)
    db_session.commit()

    query = {
        "start": (now - timedelta(hours=2)).isoformat(),
        "end":  now.isoformat()
    }
    query_string = urlencode(query)

    # Call endpoint
    response = client.get(
        f"/billing/api-usage?{query_string}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    routes = {item["api_route"] for item in data}

    assert "/stats/mean" in routes
    assert "/stats/count" in routes


def test_get_billing_history_e2e(client: TestClient, db_session, create_user, login_user):
    # Create a user
    user: User = create_user("billing@test.com", "test", "user", "Password")

    token = login_user("billing@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(UTC)

    # Create some billing ledger entries
    ledger1 = BillingLedger(
        user_id=user.id,
        total_tokens=100,
        period_start=now - timedelta(days=60),
        period_end=now - timedelta(days=30),
        timestamp=now - timedelta(days=30),
        stripe_event_id="evt_123",
    )

    ledger2 = BillingLedger(
        user_id=user.id,
        total_tokens=150,
        period_start=now - timedelta(days=30),
        period_end=now,
        timestamp=now,
        stripe_event_id="evt_456",
    )

    db_session.add(ledger1)
    db_session.add(ledger2)
    db_session.commit()

    # Call endpoint
    response = client.get("/billing/billing/history", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    # Should be ordered by period_end desc
    assert data[0]["total_tokens"] == 150
    assert data[1]["total_tokens"] == 100
    assert data[0]["stripe_event_id"] == "evt_456"


def test_get_current_billing_period_e2e(client: TestClient, db_session, create_user, login_user):
    # Create a user
    user: User = create_user("current@test.com", "test", "user", "Password")

    token = login_user("current@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(UTC)

    # Add some usage for current period
    usage = Usage(
        user_id=user.id,
        api_route="/stats/test",
        tokens=25,
        timestamp=now - timedelta(days=5),
    )

    db_session.add(usage)
    db_session.commit()

    # Call endpoint
    response = client.get("/billing/billing/current-period", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert "current_period_tokens" in data
    assert "period_start" in data
    assert "period_end" in data
    assert data["current_period_tokens"] == 25


def test_get_usage_summary_e2e(client: TestClient, db_session, create_user, login_user):
    # Create a user
    user: User = create_user("summary@test.com", "test", "user", "Password")

    token = login_user("summary@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(UTC)

    # Add usage records
    usages = [
        Usage(user_id=user.id, api_route="/stats/mean", tokens=10, timestamp=now - timedelta(days=5)),
        Usage(user_id=user.id, api_route="/stats/mean", tokens=15, timestamp=now - timedelta(days=3)),
        Usage(user_id=user.id, api_route="/stats/count", tokens=5, timestamp=now - timedelta(days=1)),
    ]

    for usage in usages:
        db_session.add(usage)
    db_session.commit()

    # Call endpoint
    response = client.get("/billing/billing/usage/summary?days=7", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert data["total_tokens"] == 30
    assert data["total_requests"] == 3
    assert data["average_tokens_per_request"] == 10.0
    assert data["period_days"] == 7
    assert len(data["top_routes"]) > 0


def test_get_usage_trends_e2e(client: TestClient, db_session, create_user, login_user):
    # Create a user
    user: User = create_user("trends@test.com", "test", "user", "Password")

    token = login_user("trends@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(UTC)

    # Add usage records for different days
    usages = [
        Usage(user_id=user.id, api_route="/stats/test", tokens=10, timestamp=now - timedelta(days=2)),
        Usage(user_id=user.id, api_route="/stats/test", tokens=20, timestamp=now - timedelta(days=1)),
        Usage(user_id=user.id, api_route="/stats/test", tokens=15, timestamp=now - timedelta(days=1)),
    ]

    for usage in usages:
        db_session.add(usage)
    db_session.commit()

    start_date = (now - timedelta(days=3)).isoformat()
    end_date = now.isoformat()
    query = {
        "start": (now - timedelta(days=3)).isoformat(),
        "end": now.isoformat()
    }
    query_string = urlencode(query)

    response = client.get(f"/billing/billing/usage/trends?{query_string}", headers=headers)

    assert response.status_code == 200

    data = response.json()

    assert "trends" in data
    trends = data["trends"]

    # Should have data for 2 days
    assert len(trends) >= 2

    # Check that days are in order and have correct totals
    day1_found = False
    day2_found = False
    for trend in trends:
        if trend["date"] == (now - timedelta(days=2)).date().isoformat():
            assert trend["tokens"] == 10
            assert trend["requests"] == 1
            day1_found = True
        elif trend["date"] == (now - timedelta(days=1)).date().isoformat():
            assert trend["tokens"] == 35  # 20 + 15
            assert trend["requests"] == 2
            day2_found = True

    assert day1_found and day2_found
