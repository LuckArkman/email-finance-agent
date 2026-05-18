from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import InvoiceRecord, Transaction, User, InvoiceStatus
from app.security import SecurityDependencies
from app.tenant import get_current_tenant
from app.processing.reconciliation import ReconciliationEngine

router = APIRouter(prefix="/api/v1/reconciliation", tags=["Reconciliation"])


class MatchRequest(BaseModel):
    transaction_id: str
    invoice_id: str


@router.get("/transactions")
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    tenant_id = get_current_tenant()
    result = await db.execute(select(Transaction).where(Transaction.tenant_id == tenant_id))
    return result.scalars().all()


@router.get("/suggestions")
async def list_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    tenant_id = get_current_tenant()
    tx_result = await db.execute(
        select(Transaction).where(Transaction.tenant_id == tenant_id, Transaction.is_reconciled == False)
    )
    invoice_result = await db.execute(
        select(InvoiceRecord).where(InvoiceRecord.tenant_id == tenant_id, InvoiceRecord.status != InvoiceStatus.PAID.value)
    )

    transactions = tx_result.scalars().all()
    invoices = invoice_result.scalars().all()

    suggestions: list[dict[str, Any]] = []
    engine = ReconciliationEngine()

    for tx in transactions:
        for invoice in invoices:
            if engine.rules.check_tolerance(float(tx.amount), float(invoice.total_amount)):
                confidence = 0.9 if tx.description and invoice.vendor_name and tx.description.lower().find(invoice.vendor_name.lower()) >= 0 else 0.75
                suggestions.append(
                    {
                        "id": f"{tx.id}:{invoice.id}",
                        "transaction_id": tx.id,
                        "invoice_id": invoice.id,
                        "confidence": confidence,
                        "vendor_name": invoice.vendor_name or tx.description or "Desconhecido",
                        "document_name": invoice.invoice_number or invoice.vendor_name or "Invoice",
                        "amount": float(invoice.total_amount),
                    }
                )

    return suggestions[:20]


@router.post("/match/{transaction_id}/{invoice_id}")
async def match_transaction_to_invoice(
    transaction_id: str,
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    tenant_id = get_current_tenant()

    tx_result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.tenant_id == tenant_id)
    )
    tx = tx_result.scalars().first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    invoice_result = await db.execute(
        select(InvoiceRecord).where(InvoiceRecord.id == invoice_id, InvoiceRecord.tenant_id == tenant_id)
    )
    invoice = invoice_result.scalars().first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    tx.invoice_id = invoice.id
    tx.is_reconciled = True
    invoice.status = InvoiceStatus.PAID.value

    await db.commit()
    return {"status": "success", "transaction_id": transaction_id, "invoice_id": invoice_id}
