from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import TransactionLog, ConfigTable

class RateLimiter:
    def __init__(self, db: Session, config: ConfigTable):
        self.db = db
        self.config = config

    def allow_request(self) -> bool:
        """
        Simple rate limiting based on the number of requests in the past 24 hours.
        If the number of calls for a given route exceeds config.rate_limit,
        the request is rejected.
        """
        if not self.config.rate_limit:
            # No rate limit set; allow all requests.
            return True

        last_24h = datetime.now() - timedelta(hours=24)
        count_24h = (
            self.db.query(TransactionLog)
            .filter(
                TransactionLog.route_name == self.config.route_name,
                TransactionLog.timestamp >= last_24h
            )
            .count()
        )
        return count_24h < self.config.rate_limit
