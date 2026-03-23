from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import ReviewQueueModel, User, InvoiceRecord, InvoiceStatus
from app.schemas import ReviewItemResponse, ReviewResolveRequest
from app.security import SecurityDependencies
from app.tenant import get_current_tenant

router = APIRouter(prefix="/api/v1/review", tags=["Human-in-the-loop"])

@router.get("/queue", response_model=List[ReviewItemResponse])
async def list_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Lists all documents waiting for human approval for the current tenant.
    """
    tenant_id = get_current_tenant()
    
    # Joins with InvoiceRecord to get vendor and total
    query = select(
        ReviewQueueModel.id,
        ReviewQueueModel.invoice_id,
        ReviewQueueModel.tenant_id,
        ReviewQueueModel.status,
        ReviewQueueModel.confidence_score,
        ReviewQueueModel.reason,
        ReviewQueueModel.created_at,
        InvoiceRecord.vendor_name,
        InvoiceRecord.total_amount
    ).join(
        InvoiceRecord, ReviewQueueModel.invoice_id == InvoiceRecord.id
    ).where(
        ReviewQueueModel.tenant_id == tenant_id,
        ReviewQueueModel.status == "pending_review"
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    # Convert to schema
    return [
        ReviewItemResponse(
            id=r.id,
            invoice_id=r.invoice_id,
            tenant_id=r.tenant_id,
            status=r.status,
            confidence_score=r.confidence_score,
            reason=r.reason,
            created_at=r.created_at,
            vendor_name=r.vendor_name,
            total_amount=r.total_amount
        ) for r in rows
    ]

@router.post("/resolve/{review_id}")
async def resolve_review(
    review_id: str,
    req: ReviewResolveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Approves or rejects a document in the review queue.
    """
    tenant_id = get_current_tenant()
    
    # 1. Fetch review item
    result = await db.execute(select(ReviewQueueModel).where(ReviewQueueModel.id == review_id, ReviewQueueModel.tenant_id == tenant_id))
    review_item = result.scalars().first()
    
    if not review_item:
        raise HTTPException(status_code=404, detail="Review item not found")
        
    # 2. Update status
    review_item.status = req.action # approved / rejected
    review_item.resolved_at = datetime.utcnow()
    review_item.assigned_to = current_user.id
    review_item.reason = req.notes or review_item.reason
    
    # 3. Update related Invoice status
    invoice_new_status = InvoiceStatus.PENDING.value if req.action == "approve" else InvoiceStatus.OVERDUE.value # or another logic
    await db.execute(
        update(InvoiceRecord).where(InvoiceRecord.id == review_item.invoice_id).values(status=invoice_new_status)
    )
    
    await db.commit()
    return {"status": "success", "message": f"Document {req.action} successfully"}
