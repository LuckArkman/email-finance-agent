from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models import ReviewQueueModel, InvoiceRecord, InvoiceStatus

class HumanReviewService:
    """
    HITL (Human-in-the-Loop) Dispatcher.
    Isolates documents that failed confidence thresholds and sends them to a review queue
    notifying frontends via WebSocket (simulated here via prints and DB states).
    """

    @staticmethod
    async def dispatch_to_review(session: AsyncSession, invoice_id: str, tenant_id: str, confidence_score: float, reason: str) -> Optional[ReviewQueueModel]:
        """
        Creates a ticket in the human review queue and updates the invoice status.
        """
        try:
            # 1. Update Invoice status immediately to stop it from going to payment/ERP export
            stmt = (
                update(InvoiceRecord)
                .where(InvoiceRecord.id == invoice_id)
                .values(status=InvoiceStatus.REVIEW_REQUIRED.value)
            )
            await session.execute(stmt)

            # 2. Add to HITL queue
            review_ticket = ReviewQueueModel(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                confidence_score=confidence_score,
                status="pending_review",
                reason=reason
            )
            session.add(review_ticket)
            
            await session.commit()
            
            # 3. Disparar notificação (WebSocket / Push Notification)
            HumanReviewService._send_websocket_alert(tenant_id, invoice_id, reason)
            
            return review_ticket
        except Exception as e:
            print(f"Failed to dispatch to human review: {e}")
            await session.rollback()
            return None

    @staticmethod
    def _send_websocket_alert(tenant_id: str, invoice_id: str, reason: str):
        """
        Placeholder for Socket.io / FastAPI WebSocket Broadcast.
        Would push real-time alerts to the Accounts Payable dashboard.
        """
        # Ex: manager.broadcast(f"New Document requires your attention! ID: {invoice_id}", room=tenant_id)
        print(f"[WebSocket Alert -> Tenant {tenant_id}] Document {invoice_id} is waiting for Human Review. Reason: {reason}")

    @staticmethod
    async def approve_document_manually(session: AsyncSession, queue_id: str, human_user_id: str, manual_overrides: Dict[str, Any] = None) -> bool:
        """
        Triggered when the human clicks "Approve" on the frontend after correcting fields.
        """
        try:
            # Fetch the queue item
            result = await session.execute(select(ReviewQueueModel).where(ReviewQueueModel.id == queue_id))
            queue_item = result.scalars().first()
            
            if not queue_item:
                return False
                
            queue_item.status = "approved"
            queue_item.assigned_to = human_user_id
            queue_item.resolved_at = datetime.utcnow()
            
            # Fetch invoice to apply overrides
            invoice_res = await session.execute(select(InvoiceRecord).where(InvoiceRecord.id == queue_item.invoice_id))
            invoice = invoice_res.scalars().first()
            
            if manual_overrides and invoice:
                # Apply human fixes (e.g. they fixed the total_amount because OCR got it wrong)
                for key, value in manual_overrides.items():
                    if hasattr(invoice, key):
                        setattr(invoice, key, value)
                        
                # Document is clean, restore natural status so it continues workflow
                invoice.status = InvoiceStatus.PENDING.value
            
            await session.commit()
            print(f"Human {human_user_id} resolved Exception Ticket {queue_id}.")
            return True
            
        except Exception as e:
            print(f"Error during manual approval: {e}")
            await session.rollback()
            return False
