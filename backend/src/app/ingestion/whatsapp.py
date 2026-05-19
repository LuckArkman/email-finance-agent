from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
import os

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp Ingestion"])

class BaileysMediaPayload(BaseModel):
    file_path: str
    sender_phone: str
    message_id: str
    media_type: str

@router.post("/baileys/media")
async def handle_baileys_media(payload: BaileysMediaPayload):
    """
    Receives media notifications from the local Baileys bridge.
    The bridge has already downloaded the file to the shared volume (/tmp/uploads).
    """
    print(f"Received Baileys media webhook: {payload.file_path} from {payload.sender_phone}")
    
    if not os.path.exists(payload.file_path):
        print(f"Error: File not found at {payload.file_path}")
        return {"status": "error", "message": "File not found on shared volume"}

    # Trigger OCR and Llama 3 Extraction
    from app.tasks.ocr_tasks import enqueue_ocr_job
    
    # Generate a unique virtual ID based on the WhatsApp message ID
    invoice_id = f"WA-{payload.message_id}"
    
    # Dispatch the Celery task
    # We use the sender's phone number as the tenant_id for WhatsApp-originated docs
    enqueue_ocr_job.delay(
        document_url=payload.file_path, 
        invoice_id=invoice_id,
        tenant_id=payload.sender_phone
    )
    
    return {"status": "processed", "invoice_id": invoice_id}

