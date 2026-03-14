import uuid
from types import SimpleNamespace

from fastapi.testclient import TestClient

from tests.common import *
from tests.auth.common import create_user, login_user


def test_create_sales_stats_task_dispatches_celery_job(
    client: TestClient,
    monkeypatch,
    create_user,
    login_user,
):
    create_user("stats@test.com", "Stats", "User", "Password")
    token = login_user("stats@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    captured = {}

    def fake_delay(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(id="task-123", status="PENDING")

    monkeypatch.setattr("app.routes.stats.run_sales_stats.delay", fake_delay)

    response = client.post(
        "/stats/sales/tasks",
        headers=headers,
        json={
            "stats": ["mean_price", "sale_volume"],
            "area": "SW1A",
            "area_type": "outcode",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        },
    )

    assert response.status_code == 202
    assert response.json() == {"task_id": "task-123", "status": "PENDING"}
    assert captured == {
        "stats": ["mean_price", "sale_volume"],
        "area": "SW1A",
        "area_type": "outcode",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
    }


def test_create_sales_stats_task_rejects_unknown_stat(
    client: TestClient,
    create_user,
    login_user,
):
    create_user("invalid-stats@test.com", "Stats", "User", "Password")
    token = login_user("invalid-stats@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/stats/sales/tasks",
        headers=headers,
        json={
            "stats": ["not_a_stat"],
            "area": "SW1A",
            "area_type": "outcode",
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": {"unsupported_stats": ["not_a_stat"]}}


def test_get_sales_stats_task_result_returns_success_payload(
    client: TestClient,
    monkeypatch,
    create_user,
    login_user,
):
    create_user("results@test.com", "Stats", "User", "Password")
    token = login_user("results@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}
    task_id = uuid.uuid4()

    fake_result = SimpleNamespace(
        status="SUCCESS",
        result={"results": {"mean_price": {"all": 123.0}}},
        successful=lambda: True,
        failed=lambda: False,
    )
    monkeypatch.setattr("app.routes.stats.get_task_result", lambda _: fake_result)

    response = client.get(f"/stats/sales/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "task_id": str(task_id),
        "status": "SUCCESS",
        "result": {"results": {"mean_price": {"all": 123.0}}},
        "error": None,
    }


def test_get_sales_stats_task_result_returns_failure_payload(
    client: TestClient,
    monkeypatch,
    create_user,
    login_user,
):
    create_user("failed-results@test.com", "Stats", "User", "Password")
    token = login_user("failed-results@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}
    task_id = uuid.uuid4()

    fake_result = SimpleNamespace(
        status="FAILURE",
        result=RuntimeError("boom"),
        successful=lambda: False,
        failed=lambda: True,
    )
    monkeypatch.setattr("app.routes.stats.get_task_result", lambda _: fake_result)

    response = client.get(f"/stats/sales/tasks/{task_id}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "task_id": str(task_id),
        "status": "FAILURE",
        "result": None,
        "error": "boom",
    }
