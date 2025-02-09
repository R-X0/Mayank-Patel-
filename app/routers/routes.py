import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models import ConfigTable
from ..rate_limiter import RateLimiter
from ..utils import create_transaction_log

router = APIRouter()

@router.post("/{route_name}/{method_name}")
def dynamic_post_route(
    route_name: str,
    method_name: str,
    payload: Dict,
    db: Session = Depends(get_db)
):
    """
    POST endpoint that dynamically routes to an external accounting system.
    It checks for configuration, enforces rate limiting, performs the external POST,
    and logs the transaction.
    """
    # Fetch configuration for the given route.
    config = db.query(ConfigTable).filter(ConfigTable.route_name == route_name).first()
    if not config:
        raise HTTPException(status_code=404, detail="No configuration found for this route")

    # Check rate limit.
    limiter = RateLimiter(db=db, config=config)
    if not limiter.allow_request():
        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="POST",
            was_successful=False,
            detail="Rate limit exceeded"
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Construct target URL and perform external POST.
    target_url = f"{config.base_url}/{method_name}"
    try:
        resp = requests.post(
            target_url,
            json=payload,
            auth=(config.username, config.password) if config.username else None
        )
        resp.raise_for_status()

        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="POST",
            was_successful=True,
            detail="Success"
        )
        return resp.json()

    except requests.exceptions.RequestException as e:
        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="POST",
            was_successful=False,
            detail=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error calling {config.system_name}: {e}")

@router.get("/{route_name}/{method_name}")
def dynamic_get_route(
    route_name: str,
    method_name: str,
    db: Session = Depends(get_db)
):
    """
    GET endpoint that dynamically routes to an external accounting system.
    It checks for configuration, enforces rate limiting, performs the external GET,
    and logs the transaction.
    """
    # Fetch configuration for the given route.
    config = db.query(ConfigTable).filter(ConfigTable.route_name == route_name).first()
    if not config:
        raise HTTPException(status_code=404, detail="No configuration found for this route")

    # Check rate limit.
    limiter = RateLimiter(db=db, config=config)
    if not limiter.allow_request():
        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="GET",
            was_successful=False,
            detail="Rate limit exceeded"
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Construct target URL and perform external GET.
    target_url = f"{config.base_url}/{method_name}"
    try:
        resp = requests.get(
            target_url,
            auth=(config.username, config.password) if config.username else None
        )
        resp.raise_for_status()

        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="GET",
            was_successful=True,
            detail="Success"
        )
        return resp.json()

    except requests.exceptions.RequestException as e:
        create_transaction_log(
            db=db,
            system_name=config.system_name,
            route_name=route_name,
            request_method="GET",
            was_successful=False,
            detail=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Error calling {config.system_name}: {e}")
