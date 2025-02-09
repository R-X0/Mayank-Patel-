from sqlalchemy.orm import Session
from .models import TransactionLog

def create_transaction_log(db: Session, **kwargs):
    """
    Helper function to create and persist a transaction log entry.
    """
    log = TransactionLog(**kwargs)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
