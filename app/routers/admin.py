from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import ConfigTable, TransactionLog

router = APIRouter()

class ConfigCreate(BaseModel):
    system_name: str
    base_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    route_name: str
    rate_limit: int

@router.get("/config")
def list_configs(db: Session = Depends(get_db)):
    """
    Lists all configuration entries.
    """
    return db.query(ConfigTable).all()

@router.post("/config")
def create_config(config_data: ConfigCreate, db: Session = Depends(get_db)):
    """
    Creates a new configuration entry.
    """
    existing = db.query(ConfigTable).filter(ConfigTable.route_name == config_data.route_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Route name already exists")

    new_config = ConfigTable(
        system_name=config_data.system_name,
        base_url=config_data.base_url,
        username=config_data.username,
        password=config_data.password,
        route_name=config_data.route_name,
        rate_limit=config_data.rate_limit
    )
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return {"message": "Config created successfully", "config": new_config}

@router.put("/config/{config_id}")
def update_config(config_id: int, config_data: ConfigCreate, db: Session = Depends(get_db)):
    """
    Updates an existing configuration entry.
    """
    config = db.query(ConfigTable).filter(ConfigTable.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    config.system_name = config_data.system_name
    config.base_url = config_data.base_url
    config.username = config_data.username
    config.password = config_data.password
    config.route_name = config_data.route_name
    config.rate_limit = config_data.rate_limit

    db.commit()
    db.refresh(config)
    return {"message": "Configuration updated", "config": config}

@router.delete("/config/{config_id}")
def delete_config(config_id: int, db: Session = Depends(get_db)):
    """
    Deletes a configuration entry.
    """
    config = db.query(ConfigTable).filter(ConfigTable.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    db.delete(config)
    db.commit()
    return {"message": "Configuration deleted"}

@router.get("/transactions")
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    """
    Lists recent transaction logs.
    """
    logs = (
        db.query(TransactionLog)
        .order_by(TransactionLog.id.desc())
        .limit(limit)
        .all()
    )
    return logs

@router.get("/transactions/summary")
def transactions_summary(db: Session = Depends(get_db)):
    """
    Provides an aggregated summary of transactions per route, showing total,
    success, and failed call counts.
    """
    summary_query = (
        db.query(
            TransactionLog.route_name,
            func.count(TransactionLog.id).label("total_calls"),
            func.sum(func.case([(TransactionLog.was_successful == True, 1)], else_=0)).label("success_calls"),
            func.sum(func.case([(TransactionLog.was_successful == False, 1)], else_=0)).label("failed_calls"),
        )
        .group_by(TransactionLog.route_name)
        .all()
    )

    result = []
    for row in summary_query:
        result.append({
            "route_name": row.route_name,
            "total_calls": row.total_calls,
            "success_calls": row.success_calls,
            "failed_calls": row.failed_calls
        })

    return result
