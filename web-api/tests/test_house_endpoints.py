from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from app.models.housing_data import EpcCertificate, House, Postcode, Sale
from tests.auth.common import create_user, login_user
from tests.common import *


def test_get_houses_by_postcode_returns_houseids(
    client: TestClient,
    db_session,
    create_user,
    login_user,
):
    create_user("houses@test.com", "House", "User", "Password")
    token = login_user("houses@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    db_session.add(Postcode(postcode="LS1 1AA", town="Leeds"))
    db_session.flush()
    db_session.add(
        House(
            houseid="house-1",
            paon="10",
            saon="Flat 2",
            postcode="LS1 1AA",
            type="F",
        )
    )
    db_session.add(
        House(
            houseid="house-2",
            paon="12",
            saon=None,
            postcode="LS1 1AA",
            type="T",
        )
    )
    db_session.flush()
    db_session.commit()

    response = client.get("/houses/postcode/LS11AA", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "postcode": "LS11AA",
        "houses": [
            {
                "houseid": "house-1",
                "paon": "10",
                "saon": "Flat 2",
                "postcode": "LS1 1AA",
                "type": "F",
            },
            {
                "houseid": "house-2",
                "paon": "12",
                "saon": None,
                "postcode": "LS1 1AA",
                "type": "T",
            },
        ],
    }


def test_get_house_details_returns_sales_and_linked_epcs(
    client: TestClient,
    db_session,
    create_user,
    login_user,
):
    create_user("house-detail@test.com", "House", "User", "Password")
    token = login_user("house-detail@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    db_session.add(Postcode(postcode="LS1 1AA", town="Leeds"))
    db_session.flush()
    db_session.add(
        House(
            houseid="house-1",
            paon="10",
            saon="Flat 2",
            postcode="LS1 1AA",
            type="F",
        )
    )
    db_session.flush()
    db_session.add(
        Sale(
            tui="sale-2",
            price=250000,
            date=datetime(2023, 5, 1, tzinfo=UTC),
            new=False,
            freehold=False,
            ppd_cat="A",
            houseid="house-1",
        )
    )
    db_session.add(
        Sale(
            tui="sale-1",
            price=200000,
            date=datetime(2020, 5, 1, tzinfo=UTC),
            new=False,
            freehold=False,
            ppd_cat="A",
            houseid="house-1",
        )
    )
    db_session.add(
        EpcCertificate(
            lmk_key="epc-1",
            address1="Flat 2",
            address2="10",
            postcode="LS1 1AA",
            current_energy_rating="C",
            potential_energy_rating="B",
            property_type="Flat",
            lodgement_date=date(2024, 1, 10),
            total_floor_area=72.5,
            uprn=123456789,
        )
    )
    db_session.add(
        EpcCertificate(
            lmk_key="epc-2",
            address1="99",
            postcode="LS1 1AA",
            current_energy_rating="D",
        )
    )
    db_session.commit()

    response = client.get("/houses/house-1", headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "houseid": "house-1",
        "paon": "10",
        "saon": "Flat 2",
        "postcode": "LS1 1AA",
        "type": "F",
        "previous_sales": [
            {
                "tui": "sale-2",
                "price": 250000,
                "date": "2023-05-01T00:00:00Z",
                "new": False,
                "freehold": False,
                "ppd_cat": "A",
            },
            {
                "tui": "sale-1",
                "price": 200000,
                "date": "2020-05-01T00:00:00Z",
                "new": False,
                "freehold": False,
                "ppd_cat": "A",
            },
        ],
        "linked_epcs": [
            {
                "lmk_key": "epc-1",
                "address1": "Flat 2",
                "address2": "10",
                "address3": None,
                "postcode": "LS1 1AA",
                "current_energy_rating": "C",
                "potential_energy_rating": "B",
                "property_type": "Flat",
                "lodgement_date": "2024-01-10",
                "total_floor_area": 72.5,
                "uprn": 123456789,
            }
        ],
    }


def test_get_house_details_returns_404_for_unknown_house(
    client: TestClient,
    create_user,
    login_user,
):
    create_user("missing-house@test.com", "House", "User", "Password")
    token = login_user("missing-house@test.com", "Password")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/houses/does-not-exist", headers=headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "House not found"}
