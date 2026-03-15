from fastapi.testclient import TestClient

from app.models.housing_data import House, Postcode
from tests.auth.common import create_user, login_user
from tests.common import *


def test_house_postcode_route_logs_billing(
    client: TestClient,
    db_session,
    monkeypatch,
    create_user,
    login_user,
):
    create_user("billing-route@test.com", "Billing", "User", "Password")
    token = login_user("billing-route@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    db_session.add(Postcode(postcode="LS1 1AA", town="Leeds"))
    db_session.flush()
    db_session.add(
        House(
            houseid="house-1",
            paon="10",
            postcode="LS1 1AA",
            type="F",
        )
    )
    db_session.commit()

    captured = {}

    def fake_delay(user_id, endpoint, bill_time, token_cost):
        captured["user_id"] = str(user_id)
        captured["endpoint_name"] = endpoint
        captured["bill_time_type"] = type(bill_time).__name__
        captured["token_cost"] = token_cost

    monkeypatch.setattr("app.billing.deps.t_log_token_usage.delay", fake_delay)

    response = client.get("/houses/postcode/LS1 1AA", headers=headers)

    assert response.status_code == 200
    assert captured["endpoint_name"] == "get_houses_by_postcode"
    assert captured["bill_time_type"] == "datetime"
    assert captured["token_cost"] == 1


def test_create_sales_stats_task_logs_billing(
    client: TestClient,
    monkeypatch,
    create_user,
    login_user,
):
    create_user("billing-stats@test.com", "Billing", "User", "Password")
    token = login_user("billing-stats@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    task_calls = {}
    billing_calls = {}

    def fake_delay(**kwargs):
        task_calls.update(kwargs)
        return type("Task", (), {"id": "task-123", "status": "PENDING"})()

    def fake_bill_delay(user_id, endpoint, bill_time, token_cost):
        billing_calls["endpoint_name"] = endpoint
        billing_calls["bill_time_type"] = type(bill_time).__name__
        billing_calls["token_cost"] = token_cost

    monkeypatch.setattr("app.routes.stats.run_sales_stats.delay", fake_delay)
    monkeypatch.setattr("app.billing.deps.t_log_token_usage.delay", fake_bill_delay)

    response = client.post(
        "/stats/sales/tasks",
        headers=headers,
        json={
            "stats": ["mean_price"],
            "area": "SW1A",
            "area_type": "outcode",
        },
    )

    assert response.status_code == 202
    assert task_calls == {
        "stats": ["mean_price"],
        "area": "SW1A",
        "area_type": "outcode",
        "start_date": None,
        "end_date": None,
    }
    assert billing_calls["endpoint_name"] == "create_sales_stats_task"
    assert billing_calls["bill_time_type"] == "datetime"
    assert billing_calls["token_cost"] == 5
