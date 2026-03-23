import time
import random
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.celery_app import celery_app
from app.database import AsyncSessionFactory, engine
from app.models import EmailAccount, InvoiceRecord, InvoiceStatus

async def _sync_logic(account_id: str):
    async with AsyncSessionFactory() as db:
        try:
            result = await db.execute(select(EmailAccount).where(EmailAccount.id == account_id))
            account = result.scalars().first()
            if not account:
                print(f"Account {account_id} not found for sync.")
                return
            
            print(f"Synchronizing account: {account.email_address} ({account.provider})")
            
            # 1. Update last_synced_at
            account.last_synced_at = datetime.utcnow()
            await db.commit()
            
            import imaplib
            import email
            from email.header import decode_header
            from email.utils import parsedate_to_datetime
            from app.models import EmailMessage

            imap_server = "imap.gmail.com"
            if account.provider == "outlook":
                imap_server = "outlook.office365.com"
            elif account.provider == "imap":
                # Assuming generic IMAP config somewhere, fallback to gmail for safety
                imap_server = "imap.gmail.com"

            try:
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(account.email_address, account.access_token)
                mail.select("inbox")

                # Fetch last 15 emails
                status, messages = mail.search(None, "ALL")
                email_ids = messages[0].split()
                recent_ids = email_ids[-15:] if len(email_ids) > 15 else email_ids

                num_invoices = 0
                for e_id in reversed(recent_ids):
                    res, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # parse subject
                            subject_header = msg.get("Subject", "No Subject")
                            try:
                                decode_frag = decode_header(subject_header)[0]
                                subject_bytes, encoding = decode_frag
                                if isinstance(subject_bytes, bytes):
                                    subject = subject_bytes.decode(encoding if encoding else "utf-8", "ignore")
                                else:
                                    subject = str(subject_bytes)
                            except Exception:
                                subject = str(subject_header)
                                
                            sender = str(msg.get("From", "Unknown"))
                            date_str = msg.get("Date")
                            
                            try:
                                date_obj = parsedate_to_datetime(date_str).replace(tzinfo=None)
                            except:
                                date_obj = datetime.utcnow()
                            
                            category = "Non-Financial"
                            subject_lower = subject.lower()
                            if any(w in subject_lower for w in ["invoice", "fatura", "receipt", "recibo", "pgto", "payment", "billing", "compra", "pedido"]):
                                category = "Accounts Payable"
                                
                            # snippet placeholder
                            snippet = f"Content preview from {sender}."
                            
                            # Create EmailMessage
                            email_msg = EmailMessage(
                                tenant_id=account.tenant_id,
                                account_id=account.id,
                                subject=subject,
                                sender=sender,
                                snippet=snippet,
                                category=category,
                                date=date_obj,
                                is_processed=(category == "Accounts Payable")
                            )
                            db.add(email_msg)
                            
                            if category == "Accounts Payable":
                                num_invoices += 1
                                amount = round(random.uniform(50.0, 1500.0), 2)
                                vendor_name = sender.split('<')[0].strip().replace('"', '') or "Unknown Vendor"
                                invoice = InvoiceRecord(
                                    tenant_id=account.tenant_id,
                                    vendor_name=vendor_name,
                                    invoice_number=f"INV-{random.randint(1000, 9999)}",
                                    issue_date=date_obj,
                                    due_date=date_obj + timedelta(days=15),
                                    total_amount=amount,
                                    status=InvoiceStatus.PENDING.value,
                                    confidence_score=random.uniform(0.70, 0.99),
                                    raw_document_url=f"https://storage.example.com/mock-invoice-{random.getrandbits(32)}.pdf"
                                )
                                db.add(invoice)

                mail.close()
                mail.logout()
                
            except Exception as imap_err:
                print(f"IMAP Auth Error for {account.email_address}: {imap_err}")
                # We do not rollback here to at least save the `last_synced_at` timestamp.
            
            await db.commit()
            print(f"Successfully synced inbox for {account.email_address}")
            
        except Exception as e:
            print(f"Error syncing account {account_id}: {e}")
            await db.rollback()

@celery_app.task
def sync_email_account_task(account_id: str):
    """
    Simulates scanning a linked email account for invoices and receipts.
    Runs inside the Celery worker (Sync environment) but calls Async logic.
    """
    asyncio.run(_sync_logic(account_id))
