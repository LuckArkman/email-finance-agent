from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import EmailAccount, User, Tenant, EmailMessage
from app.schemas import EmailAccountCreate, EmailAccountResponse, SimpleEmailDTO
from app.security import SecurityDependencies
from app.tenant import get_current_tenant
from app.tasks.email_tasks import sync_email_account_task
from sqlalchemy import desc

router = APIRouter(prefix="/api/v1/emails", tags=["Emails"])

@router.post("/accounts", response_model=EmailAccountResponse)
async def link_email_account(
    account_in: EmailAccountCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Links a new email account (Gmail, Outlook, IMAP) to the tenant.
    """
    tenant_id = get_current_tenant()
    
    new_account = EmailAccount(
        tenant_id=tenant_id,
        provider=account_in.provider,
        email_address=account_in.email_address,
        access_token=account_in.access_token,
        refresh_token=account_in.refresh_token
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    
    # Trigger Background Sync Task
    sync_email_account_task.delay(new_account.id)
    
    return new_account

@router.get("/accounts", response_model=List[EmailAccountResponse])
async def list_linked_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Lists all email accounts linked to the current tenant.
    """
    tenant_id = get_current_tenant()
    result = await db.execute(select(EmailAccount).where(EmailAccount.tenant_id == tenant_id))
    return result.scalars().all()

@router.get("/inbox", response_model=List[SimpleEmailDTO])
async def list_inbox_emails(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns all synchronized emails for the current tenant.
    """
    tenant_id = get_current_tenant()
    query = select(EmailMessage).where(EmailMessage.tenant_id == tenant_id).order_by(desc(EmailMessage.date))
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        SimpleEmailDTO(
            id=msg.id,
            subject=msg.subject or "No Subject",
            sender=msg.sender or "Unknown",
            date=msg.date.strftime("%Y-%m-%d %H:%M"),
            category=msg.category or "Non-Financial",
            snippet=msg.snippet or ""
        ) for msg in messages
    ]
