from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    status: str
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
