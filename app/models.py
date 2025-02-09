from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class ConfigTable(Base):
    """
    Stores configuration details for each accounting system integration.
    Example:
      - system_name: 'tally'
      - base_url: 'http://localhost:8000/tally'
      - username: 'tally_user'
      - password: 'secret'
      - route_name: 'tally-route'
      - rate_limit: 100  (max requests per 24 hours)
    """
    __tablename__ = "config_table"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, unique=True, index=True)
    base_url = Column(String)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    route_name = Column(String, unique=True, index=True)
    rate_limit = Column(Integer, default=100)

class TransactionLog(Base):
    """
    Logs each API request (both successful and failed) with a timestamp.
    This table helps track the number of calls per route.
    """
    __tablename__ = "transaction_log"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String)
    route_name = Column(String)
    request_method = Column(String)
    was_successful = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    detail = Column(String, nullable=True)
