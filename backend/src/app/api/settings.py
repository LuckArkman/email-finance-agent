from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import WebhookConfig, TenantSettings, User
from app.security import SecurityDependencies

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


class WebhookUpdateSchema(BaseModel):
    target_url: Optional[str] = None
    secret_key: Optional[str] = None
    is_active: bool = True


class FiscalSettingsSchema(BaseModel):
    iva_rate: float = Field(default=0.23, ge=0.0, le=1.0, description="IVA rate as decimal (e.g. 0.23 for 23%)")
    currency: str = Field(default="EUR", description="Currency code (EUR, GBP, etc.)")
    fiscal_name: Optional[str] = Field(None, description="Company fiscal name or NIF")
    fiscal_country: str = Field(default="PT", description="Fiscal country code")


@router.get("/webhooks")
async def get_webhook_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Fetch the webhook configuration for the current tenant."""
    result = await db.execute(select(WebhookConfig).where(WebhookConfig.tenant_id == current_user.tenant_id))
    config = result.scalars().first()

    if not config:
        return {"target_url": "", "secret_key": "", "is_active": True}
    return config


@router.post("/webhooks")
async def update_webhook_settings(
    payload: WebhookUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Update or create the webhook configuration for the current tenant."""
    result = await db.execute(select(WebhookConfig).where(WebhookConfig.tenant_id == current_user.tenant_id))
    config = result.scalars().first()

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

    await db.commit()
    await db.refresh(config)
    return config


@router.get("/fiscal")
async def get_fiscal_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Fetch the fiscal/tax configuration for the current tenant (IVA rate, currency)."""
    result = await db.execute(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    )
    settings = result.scalars().first()

    if not settings:
        # Return defaults if not yet configured
        return {
            "iva_rate": 0.23,
            "currency": "EUR",
            "fiscal_name": None,
            "fiscal_country": "PT"
        }
    return {
        "iva_rate": settings.iva_rate,
        "currency": settings.currency,
        "fiscal_name": settings.fiscal_name,
        "fiscal_country": settings.fiscal_country,
    }


@router.post("/fiscal")
async def update_fiscal_settings(
    payload: FiscalSettingsSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """Update or create the fiscal configuration for the current tenant."""
    result = await db.execute(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    )
    settings = result.scalars().first()

    if not settings:
        settings = TenantSettings(
            tenant_id=current_user.tenant_id,
            iva_rate=payload.iva_rate,
            currency=payload.currency,
            fiscal_name=payload.fiscal_name,
            fiscal_country=payload.fiscal_country,
        )
        db.add(settings)
    else:
        settings.iva_rate = payload.iva_rate
        settings.currency = payload.currency
        settings.fiscal_name = payload.fiscal_name
        settings.fiscal_country = payload.fiscal_country

    await db.commit()
    await db.refresh(settings)
    return {
        "iva_rate": settings.iva_rate,
        "currency": settings.currency,
        "fiscal_name": settings.fiscal_name,
        "fiscal_country": settings.fiscal_country,
    }
