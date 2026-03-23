import os
import shutil
import random
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import InvoiceRecord, User, InvoiceStatus, DocumentSource, DocumentType
from app.security import SecurityDependencies
from app.tenant import get_current_tenant
from app.api.websockets import EventBroadcaster

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Uploads a document (PDF, PNG, JPG) to the system for OCR and cross-referencing.
    """
    tenant_id = get_current_tenant()
    
    # Save the file locally
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Mock OCR Extraction Logic
    is_receipt = "recibo" in file.filename.lower() or "comprovante" in file.filename.lower()
    doc_type = DocumentType.RECEIPT.value if is_receipt else DocumentType.INVOICE.value
    
    # Simulate finding some common vendors from the images
    vendors = ["EDP Comercial", "Worten Equipamentos", "Águas do Porto", "Detergentes PT", "Uber Ride", "AWS"]
    vendor_name = random.choice(vendors)
    amount = round(random.uniform(10.0, 500.0), 2)
    
    new_doc = InvoiceRecord(
        tenant_id=tenant_id,
        vendor_name=vendor_name,
        total_amount=amount,
        issue_date=datetime.utcnow(),
        status=InvoiceStatus.PENDING.value,
        source=DocumentSource.MANUAL.value,
        document_type=doc_type,
        confidence_score=random.uniform(0.85, 0.99),
        raw_document_url=f"/api/v1/documents/view/{file.filename}"
    )
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    # Cross-Reference (Agent Intelligence)
    # Find a corresponding invoice if this is a receipt
    if doc_type == DocumentType.RECEIPT.value:
        # Look for a pending invoice from EMAIL with same vendor and amount (within +/- 5%)
        stmt = select(InvoiceRecord).where(
            InvoiceRecord.tenant_id == tenant_id,
            InvoiceRecord.vendor_name == vendor_name,
            InvoiceRecord.source == DocumentSource.EMAIL.value,
            InvoiceRecord.total_amount.between(amount * 0.95, amount * 1.05),
            InvoiceRecord.linked_to_id == None
        )
        result = await db.execute(stmt)
        match = result.scalars().first()
        
        if match:
            new_doc.linked_to_id = match.id
            new_doc.status = InvoiceStatus.PAID.value
            match.status = InvoiceStatus.PAID.value
            await db.commit()
            
            # Broadcast event to UI
            await EventBroadcaster.publish_event(
                tenant_id, "document_reconciled", 
                {"receipt_id": new_doc.id, "invoice_id": match.id}
            )

    return {"message": "File uploaded and processed", "id": new_doc.id, "reconciled": new_doc.linked_to_id is not None}

@router.get("/queue")
async def get_processing_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns documents currently in 'OCR PENDENTE' or 'A ANALISAR' state.
    """
    tenant_id = get_current_tenant()
    stmt = select(InvoiceRecord).where(
        InvoiceRecord.tenant_id == tenant_id,
        InvoiceRecord.status == InvoiceStatus.PENDING.value
    ).limit(10)
    result = await db.execute(stmt)
    return result.scalars().all()
