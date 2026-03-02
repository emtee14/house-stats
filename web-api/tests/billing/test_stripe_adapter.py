import pytest
import os

import stripe
from dotenv import load_dotenv

from app.billing.stripe_adapter import StripePaymentAdapter


@pytest.fixture
def stripe_api_key():
    print(os.getcwd())
    load_dotenv("../.env.dev")
    api_key = os.environ.get('STRIPE_API_TOKEN')
    return api_key


def test_initial_login(stripe_api_key):
    if stripe_api_key is None:
        pytest.fail("Stripe API key not set")

    try:
        stripe_adap = StripePaymentAdapter(stripe_api_key)
    except stripe.error.AuthenticationError:
        pytest.fail("Authentication Error")

    assert stripe_adap.connected == True

def test_failed_login():
    with pytest.raises(stripe.error.AuthenticationError) as exc_info:
        stripe_adap = StripePaymentAdapter("invalid_api_key")
        assert stripe_adap.connected == False
    assert exc_info.value.args[0].startswith("Invalid API Key provided:") is True


if __name__ == "__main__":
    stripe_api_key = os.environ.get('STRIPE_API_KEY')
