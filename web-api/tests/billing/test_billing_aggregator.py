import random
from datetime import datetime, timedelta, UTC

import pytest

from app.billing.billing_aggregator import BillingAggregator
from app.billing.stripe_adapter import StripePaymentAdapter
from app.models.billing import Usage
from tests.common import db_session, engine, config
from tests.auth.common import create_user
from tests.billing.common import create_usage


def test_get_users(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    user_list = biller.get_users().all()

    create_usage(user=user, api_route="/users/", tokens=50, timestamp=datetime.now()-timedelta(minutes=1))

    user_list_after = biller.get_users().all()

    assert len(user_list) == 0
    assert len(user_list_after) == 1
    assert len(user_list) != len(user_list_after)
    assert user not in user_list
    assert user in user_list_after

def test_get_users_in_period(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John",
                       last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    timestamp = datetime.now(UTC)-timedelta(minutes=1)
    create_usage(user=user, api_route="/users/", tokens=50, timestamp=timestamp)

    user_list_before = biller.get_users(period_end=timestamp-timedelta(minutes=2)).all()
    user_list = biller.get_users().all()

    assert len(user_list) == 1
    assert len(user_list_before) == 0
    assert user_list != user_list_before
    assert user not in user_list_before
    assert user in user_list

def test_aggregate_no_items(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    with pytest.raises(ValueError) as e:
        _ = biller.aggregate_user_billing(user)

    assert str(e.value) == "User has no usage recorded"

def test_aggregate_with_items(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    bills = [50, 100, 150, 200]

    create_usage(user=user, api_route="/users/", tokens=bills[0], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[1], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[2], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[3], timestamp=datetime.now(UTC)-timedelta(minutes=2))

    ledger = biller.aggregate_user_billing(user)
    biller.update_usage_events(ledger)

    assert ledger.total_tokens == sum(bills)


def test_aggregate_items_in_window(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    current_time = datetime.now(UTC)

    bills = [50, 100, 150, 200]

    create_usage(user=user, api_route="/users/", tokens=bills[0], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[1], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[2], timestamp=datetime.now(UTC)-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills[3], timestamp=datetime.now(UTC)+timedelta(minutes=2))

    ledger = biller.aggregate_user_billing(user, upto=current_time)
    biller.update_usage_events(ledger)

    assert ledger.total_tokens == sum(bills)-bills[-1]

def test_aggregate_two_ledgers(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    current_time = datetime.now(UTC)

    bills_1 = [50, 100, 150, 200]

    create_usage(user=user, api_route="/users/", tokens=bills_1[0], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[1], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[2], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[3], timestamp=current_time-timedelta(minutes=2))

    bills_2 = [200, 12, 50, 25]

    create_usage(user=user, api_route="/users/", tokens=bills_2[0], timestamp=current_time + timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_2[1], timestamp=current_time + timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_2[2], timestamp=current_time + timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_2[3], timestamp=current_time + timedelta(minutes=2))

    ledger_1 = biller.aggregate_user_billing(user, upto=current_time)
    biller.update_usage_events(ledger_1)

    ledger_2 = biller.aggregate_user_billing(user, upto=current_time+timedelta(minutes=3))
    biller.update_usage_events(ledger_2)

    assert ledger_1.total_tokens == sum(bills_1)
    assert ledger_2.total_tokens == sum(bills_2)


def test_aggregate_two_ledgers_one_empty(db_session, create_user, create_usage):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    biller = BillingAggregator(db_session)

    current_time = datetime.now(UTC)

    bills_1 = [50, 100, 150, 200]

    create_usage(user=user, api_route="/users/", tokens=bills_1[0], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[1], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[2], timestamp=current_time-timedelta(minutes=2))
    create_usage(user=user, api_route="/users/", tokens=bills_1[3], timestamp=current_time-timedelta(minutes=2))


    ledger_1 = biller.aggregate_user_billing(user, upto=current_time)
    biller.update_usage_events(ledger_1)
    with pytest.raises(ValueError) as e:
        ledger_2 = biller.aggregate_user_billing(user, upto=current_time+timedelta(minutes=3))


    assert ledger_1.total_tokens == sum(bills_1)
    assert str(e.value) == "User has no usage recorded"


def test_aggregation_en_masse_single_user(create_user, create_usage, db_session, config):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")

    stripe_adap = StripePaymentAdapter(config.STRIPE_API_TOKEN)
    stripe_adap.setup_user(user, db_session)

    bills = [50, 100, 150, 200]

    usages = [
        create_usage(user=user, api_route="/users/", tokens=bills[0],
                     timestamp=datetime.now(UTC) - timedelta(minutes=2)),
        create_usage(user=user, api_route="/users/", tokens=bills[1],
                     timestamp=datetime.now(UTC) - timedelta(minutes=2)),
        create_usage(user=user, api_route="/users/", tokens=bills[2],
                     timestamp=datetime.now(UTC) - timedelta(minutes=2)),
        create_usage(user=user, api_route="/users/", tokens=bills[3],
                     timestamp=datetime.now(UTC) - timedelta(minutes=2))
    ]


    biller = BillingAggregator(db_session)

    agg_event = biller.aggregate_en_masse(billing_hour=datetime.now(UTC).hour+1)

    ledgers = agg_event.billing_ledgers
    cost_items = ledgers[0].cost_items

    for usage in usages:
        assert usage in cost_items


def test_aggregation_en_masse_multi_user(create_user, create_usage, db_session, config, seed="kjfnkjanfkjwnfkwaj"):
    user_1 = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")
    user_2 = create_user(email="test-1@example.com", first_name="John", last_name="Doe", password="Password123")
    user_3 = create_user(email="test-2@example.com", first_name="John", last_name="Doe", password="Password123")

    stripe_adap = StripePaymentAdapter(config.STRIPE_API_TOKEN)
    stripe_adap.setup_user(user_1, db_session)
    stripe_adap.setup_user(user_2, db_session)
    stripe_adap.setup_user(user_3, db_session)

    random.seed(seed)

    bills_1 = [random.randint(0,500) for i in range(50)]
    bills_2 = [random.randint(0, 500) for i in range(50)]
    bills_3 = [random.randint(0, 500) for i in range(50)]

    usages_1 = []
    usages_2 = []
    usages_3 = []

    for bill in bills_1:
        usages_1.append(
            create_usage(user=user_1, api_route="/users/", tokens=bill,
                         timestamp=datetime.now(UTC) - timedelta(minutes=10))
        )

    for bill in bills_2:
        usages_2.append(
            create_usage(user=user_2, api_route="/users/", tokens=bill,
                         timestamp=datetime.now(UTC) - timedelta(minutes=10))
        )

    for bill in bills_3:
        usages_3.append(
            create_usage(user=user_3, api_route="/users/", tokens=bill,
                         timestamp=datetime.now(UTC) - timedelta(minutes=10))
        )

    biller = BillingAggregator(db_session)

    agg_event = biller.aggregate_en_masse(billing_hour=datetime.now(UTC).hour+1)

    ledgers = agg_event.billing_ledgers
    for ledger in ledgers:
        match ledger.user_id:
            case user_1.id:
                for usage in usages_1:
                    assert usage in ledger.cost_items
            case user_2.id:
                for usage in usages_2:
                    assert usage in ledger.cost_items
            case user_3.id:
                for usage in usages_2:
                    assert usage in ledger.cost_items

