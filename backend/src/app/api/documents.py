import os
import shutil
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
    
    # Create the db record in PENDING state
    new_doc = InvoiceRecord(
        tenant_id=tenant_id,
        vendor_name="Pendente...", # Will be updated by IA
        total_amount=0.0,
        status=InvoiceStatus.PENDING.value,
        source=DocumentSource.MANUAL.value,
        raw_document_url=file_path # Local path for the worker
    )
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    # 3. Dispatch AI Task
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
    Returns documents currently in 'OCR PENDENTE' or 'A ANALISAR' state.
    """
    tenant_id = get_current_tenant()
    stmt = select(InvoiceRecord).where(
        InvoiceRecord.tenant_id == tenant_id,
        InvoiceRecord.status == InvoiceStatus.PENDING.value
    ).limit(10)
    result = await db.execute(stmt)
    return result.scalars().all()
