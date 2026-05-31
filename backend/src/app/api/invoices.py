from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from pydantic import BaseModel

from app.database import get_db
from app.models import User, InvoiceRecord, InvoiceStatus
from app.security import SecurityDependencies
from app.tenant import filter_by_tenant

router = APIRouter(prefix="/api/v1/invoices", tags=["Invoices"])

# Schemas
class InvoiceResponseSchema(BaseModel):
    id: str
    vendor_name: Optional[str]
    invoice_number: Optional[str]
    issue_date: Optional[datetime]
    due_date: Optional[datetime]
    document_type: Optional[str]
    net_amount: float
    iva_rate: float
    iva_amount: float
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    status: str
    payment_reference: Optional[str]
    confidence_score: float
    raw_document_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InvoiceUpdateSchema(BaseModel):
    status: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    due_date: Optional[datetime] = None
    document_type: Optional[str] = None


from collections import defaultdict
from sqlalchemy import and_

@router.get("/calendar")
async def get_calendar_invoices(
    year: int = Query(..., description="Year (e.g. 2026)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns invoices grouped by due_date day for a given month/year.
    Used by the calendar view to show bills due on each specific day.
    Format: { "2026-05-26": [invoice, ...], "2026-05-30": [invoice, ...] }
    """
    from datetime import date
    import calendar

    # Build date range for the month
    first_day = datetime(year, month, 1)
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = datetime(year, month, last_day_num, 23, 59, 59)

    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord)).where(
        and_(
            InvoiceRecord.due_date >= first_day,
            InvoiceRecord.due_date <= last_day,
        )
    ).order_by(InvoiceRecord.due_date)

    result = await db.execute(query)
    invoices = result.scalars().all()

    # Group by day key: YYYY-MM-DD
    grouped: dict = defaultdict(list)
    for inv in invoices:
        if inv.due_date:
            day_key = inv.due_date.strftime("%Y-%m-%d")
            grouped[day_key].append(InvoiceResponseSchema.model_validate(inv))

    return dict(grouped)


@router.post("/mark-overdue", summary="Mark overdue invoices")
async def mark_overdue_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Marks all pending/review invoices past their due_date as overdue (reconciliation).
    Normally called by a Celery daily cron, but also available as manual trigger.
    """
    today = datetime.utcnow()
    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord)).where(
        and_(
            InvoiceRecord.due_date < today,
            InvoiceRecord.status.in_(["pending", "review_required"]),
        )
    )
    result = await db.execute(query)
    invoices = result.scalars().all()

    count = 0
    for inv in invoices:
        inv.status = "reconciliation"
        count += 1

    await db.commit()
    return {"marked_overdue": count}


@router.get("", response_model=Dict[str, Any])
async def read_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status (e.g. pending, paid)"),
    sort_by: str = Query("created_at", description="Field to sort by, defaults to created_at"),
    sort_desc: bool = Query(True, description="Sort descending"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Lista todas as faturas do Tenant com paginação, filtros e ordenação segura 
    protegida pelo Middleware RLS (Row Level Security).
    """

    # Base query relying on our RLS function
    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord))

    if status_filter:
        query = query.where(InvoiceRecord.status == status_filter)

    # Sort
    order_col = getattr(InvoiceRecord, sort_by, InvoiceRecord.created_at)
    if sort_desc:
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(order_col)

    # Calculate Total
    count_query = filter_by_tenant(InvoiceRecord, select(func.count(InvoiceRecord.id)))
    if status_filter:
         count_query = count_query.where(InvoiceRecord.status == status_filter)
         
    total_res = await db.execute(count_query)
    total_items = total_res.scalar_one()

    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    invoices = result.scalars().all()

    # Convert to schema
    data = [InvoiceResponseSchema.model_validate(inv) for inv in invoices]
    
    return {
        "data": data,
        "total": total_items,
        "skip": skip,
        "limit": limit
    }

@router.get("/{invoice_id}", response_model=InvoiceResponseSchema)
async def read_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Traz uma fatura específica através do ID com restrição de visibilidade RLS.
    """
    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord).where(InvoiceRecord.id == invoice_id))
    result = await db.execute(query)
    invoice = result.scalars().first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found or you don't have permissions to view it.")

    return invoice

@router.get("/{invoice_id}/file")
async def read_invoice_file(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns the actual raw document file for the invoice.
    """
    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord).where(InvoiceRecord.id == invoice_id))
    result = await db.execute(query)
    invoice = result.scalars().first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found or you don't have permissions to view it.")
        
    if not invoice.raw_document_url or not os.path.exists(invoice.raw_document_url):
        raise HTTPException(status_code=404, detail="The physical file is missing or was never uploaded.")

    # Serves the file
    return FileResponse(invoice.raw_document_url)

@router.post("/manual", response_model=InvoiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_invoice_manually(
    payload: InvoiceUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Permite o cadastro manual de faturas inserindo-as diretamente no banco.
    """
    new_invoice = InvoiceRecord(
        tenant_id=current_user.tenant_id,
        vendor_name=payload.vendor_name,
        total_amount=payload.total_amount if payload.total_amount is not None else 0.0,
        status=payload.status if payload.status else InvoiceStatus.PENDING.value
    )
    
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    return new_invoice

@router.put("/{invoice_id}", response_model=InvoiceResponseSchema)
async def update_invoice_status(
    invoice_id: str,
    payload: InvoiceUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Atualiza metadados ou status da fatura. Por exemplo: Frontend marcando "Pago".
    """
    query = filter_by_tenant(InvoiceRecord, select(InvoiceRecord).where(InvoiceRecord.id == invoice_id))
    result = await db.execute(query)
    invoice = result.scalars().first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(invoice, key, value)

    await db.commit()
    await db.refresh(invoice)
    
    return invoice
