from datetime import datetime

import stripe
from sqlmodel import Session

from app.billing.payment_base import PaymentBase
from app.models.auth import User

METERING_EVENTS = ["api_requests"]

class StripePaymentAdapter(PaymentBase):
    def __init__(self, token):
        self._connect_sdk(token)

    def _connect_sdk(self, token):
        self._client = stripe.StripeClient(token)
        self._client.v1.customers.list({"limit": 1})
        self._connected = True

    @property
    def connected(self):
        return self._connected

    def setup_user(self, user: User, session: Session):
        customer = self._client.v1.customers.create({
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "metadata": {
                "user_id": user.id,
            }
        })
        today = datetime.today()

        subscription = self._client.v1.subscriptions.create({
            "customer": customer.id,
            "items": [
                {"price": "price_1T1vV3IZoGcblMblif2jz5sc"}
            ],
            "billing_cycle_anchor": datetime(day=28, month=today.month, year=today.year),
            "collection_method": "charge_automatically"
        })

        user.stripe_id = customer["id"]
        user.subscription_id = subscription["id"]

        session.commit()


    def log_new_billing_event(self, event_id, user_id, event_value) -> str:
        if event_id not in METERING_EVENTS:
            raise ValueError("Invalid event_id")

        meter_event = self._client.billing.meter_events.create({
            "event_name": event_id,
            "payload": {
                "value": event_value,
                "stripe_customer_id": user_id,
            }
        })

        return meter_event["identifier"]
