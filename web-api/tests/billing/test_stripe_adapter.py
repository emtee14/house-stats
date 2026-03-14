import pytest

import stripe

from app.billing.stripe_adapter import StripePaymentAdapter
from tests.common import *

def test_initial_login(settings):
    try:
        stripe_adap = StripePaymentAdapter(settings)
    except stripe.error.AuthenticationError:
        pytest.fail("Authentication Error")

    assert stripe_adap.connected


def test_failed_login(settings):
    with pytest.raises(stripe.error.AuthenticationError) as exc_info:
        settings.stripe_api_token = "invalid_token"
        stripe_adap = StripePaymentAdapter(settings)
        assert not stripe_adap.connected
    assert exc_info.value.args[0].startswith("Invalid API Key provided:") is True
