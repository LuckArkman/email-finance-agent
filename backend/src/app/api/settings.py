from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import WebhookConfig, User
from app.security import SecurityDependencies

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])

class WebhookUpdateSchema(BaseModel):
    target_url: Optional[str] = None
    secret_key: Optional[str] = None
    is_active: bool = True

@router.get("/webhooks")
async def get_webhook_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Fetch the webhook configuration for the current tenant."""
    config = db.query(WebhookConfig).filter(WebhookConfig.tenant_id == current_user.tenant_id).first()
    if not config:
        return {"target_url": "", "secret_key": "", "is_active": True}
    return config

@router.post("/webhooks")
async def update_webhook_settings(
    payload: WebhookUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Update or create the webhook configuration for the current tenant."""
    config = db.query(WebhookConfig).filter(WebhookConfig.tenant_id == current_user.tenant_id).first()
    
    if not config:
        config = WebhookConfig(
            tenant_id=current_user.tenant_id,
            target_url=payload.target_url,
            secret_key=payload.secret_key,
            is_active=payload.is_active
        )
        db.add(config)
    else:
        config.target_url = payload.target_url
        config.secret_key = payload.secret_key
        config.is_active = payload.is_active
    
    db.commit()
    db.refresh(config)
    return config
