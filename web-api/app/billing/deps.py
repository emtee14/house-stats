from datetime import datetime, UTC

from fastapi import Depends, Request

from app.auth.deps import get_current_user
from app.db import get_session
from app.tasks.billing import log_token_usage as t_log_token_usage


def bill_tokens(token_cost: int):
    async def bill_dependency(
            request: Request,
            current_user = Depends(get_current_user),
    ):
        try:
            yield
        except Exception:
            pass
        else:
            endpoint = request.scope.get("endpoint")
            current_time = datetime.now(UTC)
            t_log_token_usage.delay(current_user.id, endpoint, current_time, token_cost)

    return bill_dependency