import time
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
        import asyncio
        
        tenant_id = retval.get("tenant_id", "unknown")
        print(f"Task {task_id} succeeded for tenant {tenant_id}")
        TelemetryManager.push_metric("invoice_processed", status="success", tenant_id=tenant_id)
        
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
    Simulates the heavy OCR and AI extraction pipeline.
    This runs asynchronously away from the main loop!
    """
    try:
        print(f"Starting OCR extraction for {document_url} (Invoice: {invoice_id})")
        # Simulate heavy processing...
        time.sleep(5)
        print("OCR complete")
        return {
            "status": "success", 
            "invoice_id": invoice_id, 
            "tenant_id": tenant_id,
            "mocked_total": 1500.50
        }
    except Exception as exc:
        print(f"Error processing OCR for {invoice_id}: {exc}")
        # Automatically retry task on specific errors
        raise self.retry(exc=exc)

def check_task_status(task_id: str):
    """Helper functional wrapper to query redis task results."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
