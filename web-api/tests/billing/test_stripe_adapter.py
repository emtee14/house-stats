import pytest

import stripe

from app.billing.stripe_adapter import StripePaymentAdapter
from tests.common import config

def test_initial_login(config):
    try:
        stripe_adap = StripePaymentAdapter(config.STRIPE_API_TOKEN)
    except stripe.error.AuthenticationError:
        pytest.fail("Authentication Error")

    assert stripe_adap.connected


def test_failed_login():
    with pytest.raises(stripe.error.AuthenticationError) as exc_info:
        stripe_adap = StripePaymentAdapter("invalid_api_key")
        assert not stripe_adap.connected
    assert exc_info.value.args[0].startswith("Invalid API Key provided:") is True
