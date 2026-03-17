from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import hmac
import hashlib
from app.tasks.ocr_tasks import enqueue_ocr_job

router = APIRouter(prefix="/api/v1/ingest", tags=["Ingestion"])

class IncomingWebhookSchema(BaseModel):
    reference_id: str
    document_url: str
    provider: str = "generic"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WebhookAuthenticator:
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key

    def verify_hmac_signature(self, payload: bytes, signature: str) -> bool:
        if not signature:
            return False
            
        # Example computes a sha256 HMAC
        expected_signature = hmac.new(
            self.secret_key,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)

# In a real scenario, this would be loaded from env vars
webhook_auth = WebhookAuthenticator(secret_key=b"this_is_a_secret_key_for_webhooks")

def handle_stripe_event(payload: Dict[str, Any]):
    """
    Especific function to handle stripe-like structures 
    (i.e extract the receipt_url from the event object).
    """
    doc_url = payload.get("data", {}).get("object", {}).get("receipt_url")
    return doc_url

@router.post("/webhook")
async def process_generic_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None, description="HMAC SHA256 Signature")
):
    """
    Criação de endpoint genérico /api/v1/ingest/webhook.
    Validação de assinaturas (HMAC).
    Sanitização de payload entrante.
    Encaminhamento do documento para fila de processamento.
    """
    raw_payload = await request.body()
    
    # 1. Validação de Assinatura (Segurança)
    # The requirement asks for HMAC verification
    if not webhook_auth.verify_hmac_signature(raw_payload, x_signature):
        raise HTTPException(status_code=401, detail="Invalid HMAC Signature")

    try:
        json_payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON Payload")

    # Sanitização: try to parse via Pydantic model
    try:
        body = IncomingWebhookSchema(**json_payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Unprocessable Entity: {str(e)}")

    # 2. Encaminhamento do documento para a fila assíncrona do Celery
    task = enqueue_ocr_job.delay(
        document_url=body.document_url, 
        invoice_id=body.reference_id,
        tenant_id="TENANT-MOCK-001" # In prod, this comes from auth/config
    )

    return {"status": "webhook_accepted", "message": "Dispatched to AI Queue", "task_id": task.id}
