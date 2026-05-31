import os
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import InvoiceRecord, User, InvoiceStatus, DocumentSource
from app.security import SecurityDependencies
from app.tenant import get_current_tenant

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
    
    # Real flow: Save the file and dispatch task
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Verify the file was actually written
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise HTTPException(status_code=500, detail="File could not be saved to disk.")
    
    # Create the db record in PENDING state (with file reference)
    new_doc = InvoiceRecord(
        tenant_id=tenant_id,
        vendor_name="Pendente...",  # Will be updated by AI
        total_amount=0.0,
        status=InvoiceStatus.PENDING.value,
        source=DocumentSource.MANUAL.value,
        raw_document_url=file_path  # Physical file confirmed to exist
    )
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    # Dispatch OCR Task — only because file is confirmed on disk
    from app.tasks.ocr_tasks import enqueue_ocr_job
    enqueue_ocr_job.delay(
        document_url=file_path,
        invoice_id=new_doc.id,
        tenant_id=tenant_id
    )

    return {"message": "File uploaded and processed", "id": new_doc.id, "reconciled": new_doc.linked_to_id is not None}

@router.get("/queue")
async def get_processing_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns documents currently in 'OCR PENDENTE' state that have a real
    physical file attached. Documents extracted from email body text only
    (without attachments) are intentionally excluded from this view.
    """
    tenant_id = get_current_tenant()
    stmt = select(InvoiceRecord).where(
        and_(
            InvoiceRecord.tenant_id == tenant_id,
            InvoiceRecord.status == InvoiceStatus.PENDING.value,
            InvoiceRecord.raw_document_url.isnot(None),
        )
    ).limit(20)
    result = await db.execute(stmt)
    records = result.scalars().all()

    # Secondary filter: confirm the file actually exists on disk
    # (guards against orphan records from deleted files)
    valid_records = [
        r for r in records
        if r.raw_document_url and os.path.exists(r.raw_document_url)
    ]
    return valid_records
