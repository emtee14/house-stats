from datetime import datetime, timedelta, UTC

import stripe
from sqlmodel import Session

from app.billing.payment_base import PaymentBase
from app.models.auth import User
from app.settings import Settings

METERING_EVENTS = ["api_requests"]


class StripePaymentAdapter(PaymentBase):
    def __init__(self, settings: Settings):
        self._settings = settings
        self._connect_sdk(settings.stripe_api_token)

    def _connect_sdk(self, token):
        self._client = stripe.StripeClient(token)
        self._client.v1.customers.list({"limit": 1})
        self._connected = True

    @property
    def connected(self):
        return self._connected

    def setup_user(self, user: User, session: Session):
        customer = self._client.v1.customers.create(
            {
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "metadata": {
                    "user_id": user.id,
                },
            }
        )

        subscription = self._client.v1.subscriptions.create(
            {
                "customer": customer.id,
                "items": [{"price": self._settings.stripe_token_product_id}],
                "billing_cycle_anchor": datetime.now(UTC) + timedelta(days=28),
                "collection_method": "charge_automatically",
                "trial_end": datetime.now(UTC) + timedelta(days=28),
            }
        )

        user.stripe_id = customer["id"]
        user.subscription_id = subscription["id"]

        session.commit()

    def log_new_billing_event(self, event_id, user_id, event_value) -> str:
        if event_id not in METERING_EVENTS:
            raise ValueError("Invalid event_id")

        meter_event = self._client.billing.meter_events.create(
            {
                "event_name": event_id,
                "payload": {
                    "value": event_value,
                    "stripe_customer_id": user_id,
                },
            }
        )

        return meter_event["identifier"]
