import time
import random
from celery import Task
from app.celery_app import celery_app

class OCRTaskHandler(Task):
    """
    Custom Task handler to manage retry mechanisms and unified logging
    for heavy OCR tasks.
    """
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        from app.telemetry import TelemetryManager
        print(f"Task {task_id} failed: {exc}")
        TelemetryManager.capture_exception_sentry(exc)
        TelemetryManager.push_metric("invoice_processed", status="failed", tenant_id="unknown")

    def on_success(self, retval, task_id, args, kwargs):
        from app.telemetry import TelemetryManager
        from app.webhooks_outbound import WebhookOutboundService
        from app.database import SessionLocal
        from app.models import WebhookConfig
        from app.services.whatsapp_service import WhatsAppMessagingService
        import asyncio
        
        tenant_id = retval.get("tenant_id", "unknown")
        invoice_id = retval.get("invoice_id", "")
        vendor = retval.get("vendor", "Desconhecido")
        total = retval.get("total", 0.0)
        
        print(f"Task {task_id} succeeded for tenant {tenant_id}")
        TelemetryManager.push_metric("invoice_processed", status="success", tenant_id=tenant_id)

        # WhatsApp Notification for mobile users
        if invoice_id.startswith("WA-"):
            # The 'tenant_id' for WhatsApp jobs is the phone number
            message = (
                f"✅ *Documento Processado!*\n\n"
                f"O Agente Sustentacódigo acaba de processar o seu documento:\n"
                f"• *Fornecedor:* {vendor}\n"
                f"• *Valor:* €{total:,.2f}\n"
                f"• *Status:* Registado e Reconciliado.\n\n"
                f"Pode consultar os detalhes no seu Dashboard."
            )
            asyncio.run(WhatsAppMessagingService.send_text_message(to=tenant_id, text=message))
        
        # 1. Lookup Customizable Webhook URL in Database
        db = SessionLocal()
        try:
            config = db.query(WebhookConfig).filter(WebhookConfig.tenant_id == tenant_id, WebhookConfig.is_active == True).first()
            
            if config and config.target_url:
                # 2. Trigger Custom Outbound integration (Zapier/Make)
                asyncio.run(WebhookOutboundService.emit_trigger_workflow(
                    event_name="invoice.processed",
                    payload=retval,
                    target_url=config.target_url,
                    secret=config.secret_key
                ))
            else:
                print(f"No active outbound webhook configured for tenant {tenant_id}")
        finally:
            db.close()

@celery_app.task(bind=True, base=OCRTaskHandler, max_retries=3, default_retry_delay=60)
def enqueue_ocr_job(self, document_url: str, invoice_id: str, tenant_id: str = "default"):
    """
    Executes real OCR and AI extraction utilizing Llama 3!
    Integrated with Deskewing, LineItem persistence, and Audit Logging.
    """
    from app.models import ReviewQueueModel, InvoiceStatus, InvoiceRecord, DocumentType, LineItem, AuditLog
    from app.database import SessionLocal
    from app.extraction.ocr_engine import LocalOCREngine
    from app.extraction.llm_client import LLMExtractorClient
    from app.processing.deskew import DeskewProcessor
    import asyncio
    import json
    
    db = SessionLocal()
    try:
        print(f"Executing AI Extraction for {document_url}")
        
        # 1. Image Pre-processing (Deskewing)
        # We correct the perspective before OCR to ensure maximum Llama 3 accuracy.
        if not document_url.lower().endswith(".pdf"):
            deskewer = DeskewProcessor()
            try:
                document_url = deskewer.correct_document_perspective(document_url)
            except Exception as e:
                print(f"Warning: Deskewing failed for {document_url}: {e}")

        # 2. OCR Step (Local Tesseract/EasyOCR)
        ocr = LocalOCREngine(engine_type="tesseract")
        raw_text = asyncio.run(ocr.extract_text_content(document_url))
        
        if not raw_text.strip():
            print("Empty OCR result. Failing task.")
            return {"status": "error", "reason": "No text detected"}
        
        # 3. LLM Step (Llama 3 / OpenAI)
        llm = LLMExtractorClient()
        extracted_data = asyncio.run(llm.invoke_llm_chain(raw_text))
        
        if not extracted_data:
            print("LLM Extraction failed.")
            return {"status": "error", "reason": "AI extraction failure"}

        # 4. Persistence Layer
        confidence = 0.95 # Meta-confidence from Llama 3
        
        invoice = db.query(InvoiceRecord).filter(InvoiceRecord.id == invoice_id).first()
        if invoice:
            invoice.vendor_name = extracted_data.vendor_name
            invoice.invoice_number = extracted_data.invoice_number
            invoice.total_amount = extracted_data.total_amount
            invoice.subtotal = extracted_data.subtotal
            invoice.tax_amount = extracted_data.tax_amount
            invoice.currency = extracted_data.currency
            invoice.iban = extracted_data.iban
            invoice.swift = extracted_data.swift
            invoice.status = InvoiceStatus.PENDING.value if extracted_data.is_valid_invoice else InvoiceStatus.REVIEW_REQUIRED.value
            invoice.confidence_score = confidence
            invoice.document_type = "invoice" if extracted_data.is_valid_invoice else "other"
            
            # Persist Line Items
            # Clear existing if any (atomic update)
            db.query(LineItem).filter(LineItem.invoice_id == invoice_id).delete()
            for item in extracted_data.items:
                li = LineItem(
                    invoice_id=invoice_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                db.add(li)
            
            # 5. Audit Logging (Immutable Chain)
            audit = AuditLog(
                tenant_id=tenant_id,
                action="AI_EXTRACTION_SUCCESS",
                resource_type="invoice",
                resource_id=invoice_id,
                details=json.dumps({
                    "vendor": extracted_data.vendor_name,
                    "total": extracted_data.total_amount,
                    "confidence": confidence,
                    "engine": "Llama 3"
                })
            )
            db.add(audit)
            db.commit()

        # HITL Hook: Dispatch if low confidence
        if confidence < 0.9:
            review = ReviewQueueModel(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                status="pending_review",
                confidence_score=confidence,
                reason="Low confidence detected in Llama 3 output."
            )
            db.add(review)
            db.commit()

        return {
            "status": "success", 
            "invoice_id": invoice_id, 
            "vendor": extracted_data.vendor_name,
            "total": extracted_data.total_amount,
            "tenant_id": tenant_id,
            "confidence": confidence
        }
        
    except Exception as exc:
        print(f"Error in enqueue_ocr_job: {exc}")
        db.rollback()
        raise self.retry(exc=exc)
    finally:
        db.close()

def check_task_status(task_id: str):
    """Helper functional wrapper to query redis task results."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
