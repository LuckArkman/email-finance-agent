import base64
import json
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import BaseAPIConfig
from app.database import get_db
from app.models import EmailAccount, EmailMessage, User
from app.schemas import EmailAccountCreate, EmailAccountResponse, SimpleEmailDTO
from app.security import SecurityDependencies
from app.tasks.email_tasks import sync_email_account_task
from app.tenant import get_current_tenant

router = APIRouter(prefix="/api/v1/emails", tags=["Emails"])


def _encode_state(payload: dict[str, str]) -> str:
    raw = json.dumps(payload).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def _decode_state(state: str) -> dict[str, str]:
    raw = base64.urlsafe_b64decode(state.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


async def _upsert_email_account(
    db: AsyncSession,
    tenant_id: str,
    provider: str,
    email_address: str,
    access_token: str | None,
    refresh_token: str | None,
) -> EmailAccount:
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.tenant_id == tenant_id,
            EmailAccount.provider == provider,
            EmailAccount.email_address == email_address,
        )
    )
    account = result.scalars().first()

    if account is None:
        account = EmailAccount(
            tenant_id=tenant_id,
            provider=provider,
            email_address=email_address,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        db.add(account)
    else:
        account.access_token = access_token
        account.refresh_token = refresh_token
        account.is_active = True

    await db.commit()
    await db.refresh(account)
    return account


def _provider_auth_url(provider: str, email: str, user: User) -> str:
    settings = BaseAPIConfig.get_settings()
    state = _encode_state(
        {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "email": email,
            "provider": provider,
        }
    )

    if provider == "google":
        if not settings.google_client_id:
            raise HTTPException(status_code=400, detail="Google OAuth not configured in backend.")
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    if provider == "outlook":
        if not settings.microsoft_client_id:
            raise HTTPException(status_code=400, detail="Microsoft OAuth not configured in backend.")
        params = {
            "client_id": settings.microsoft_client_id,
            "redirect_uri": settings.microsoft_redirect_uri,
            "response_type": "code",
            "response_mode": "query",
            "scope": "offline_access openid profile email https://graph.microsoft.com/Mail.Read",
            "state": state,
        }
        return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"

    raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")


async def _exchange_google_code(code: str) -> dict[str, str]:
    settings = BaseAPIConfig.get_settings()
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def _exchange_outlook_code(code: str) -> dict[str, str]:
    settings = BaseAPIConfig.get_settings()
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "client_id": settings.microsoft_client_id,
                "client_secret": settings.microsoft_client_secret,
                "code": code,
                "redirect_uri": settings.microsoft_redirect_uri,
                "grant_type": "authorization_code",
                "scope": "offline_access openid profile email https://graph.microsoft.com/Mail.Read",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


@router.get("/link/google")
async def google_auth_redirect(
    email: str = Query(..., min_length=3),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """Returns the Google OAuth URL for the selected mailbox."""
    return {"auth_url": _provider_auth_url("google", email, current_user)}


@router.get("/link/outlook")
async def outlook_auth_redirect(
    email: str = Query(..., min_length=3),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """Returns the Microsoft OAuth URL for the selected mailbox."""
    return {"auth_url": _provider_auth_url("outlook", email, current_user)}


@router.get("/callback/google")
async def google_auth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Completes Google OAuth, stores the tokens, and starts mailbox sync.
    """
    decoded = _decode_state(state)
    token_data = await _exchange_google_code(code)
    account = await _upsert_email_account(
        db=db,
        tenant_id=decoded["tenant_id"],
        provider="google",
        email_address=decoded["email"],
        access_token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
    )
    sync_email_account_task.delay(account.id)

    settings = BaseAPIConfig.get_settings()
    redirect_url = f"{settings.frontend_base_url}/email-link?linked=1&provider=google&email={decoded['email']}"
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback/outlook")
async def outlook_auth_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Completes Microsoft OAuth, stores the tokens, and starts mailbox sync.
    """
    decoded = _decode_state(state)
    token_data = await _exchange_outlook_code(code)
    account = await _upsert_email_account(
        db=db,
        tenant_id=decoded["tenant_id"],
        provider="outlook",
        email_address=decoded["email"],
        access_token=token_data.get("access_token"),
        refresh_token=token_data.get("refresh_token"),
    )
    sync_email_account_task.delay(account.id)

    settings = BaseAPIConfig.get_settings()
    redirect_url = f"{settings.frontend_base_url}/email-link?linked=1&provider=outlook&email={decoded['email']}"
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/accounts", response_model=EmailAccountResponse)
async def link_email_account(
    account_in: EmailAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """
    Links a generic IMAP mailbox or stores pre-fetched tokens and starts sync.
    """
    tenant_id = get_current_tenant()
    account = await _upsert_email_account(
        db=db,
        tenant_id=tenant_id,
        provider=account_in.provider,
        email_address=account_in.email_address,
        access_token=account_in.access_token,
        refresh_token=account_in.refresh_token,
    )
    sync_email_account_task.delay(account.id)
    return account


@router.get("/accounts", response_model=List[EmailAccountResponse])
async def list_linked_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """Lists all email accounts linked to the current tenant."""
    tenant_id = get_current_tenant()
    result = await db.execute(select(EmailAccount).where(EmailAccount.tenant_id == tenant_id))
    return result.scalars().all()


@router.get("/inbox", response_model=List[SimpleEmailDTO])
async def list_inbox_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """Returns all synchronized emails for the current tenant."""
    tenant_id = get_current_tenant()
    query = select(EmailMessage).where(EmailMessage.tenant_id == tenant_id).order_by(desc(EmailMessage.date))
    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        SimpleEmailDTO(
            id=msg.id,
            subject=msg.subject or "No Subject",
            sender=msg.sender or "Unknown",
            date=msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "N/A",
            category=msg.category or "Non-Financial",
            snippet=msg.snippet or "",
        )
        for msg in messages
    ]
