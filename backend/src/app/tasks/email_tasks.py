import asyncio
import base64
import html
import os
import re
import shutil
from datetime import datetime, timedelta
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
from typing import Any

import httpx
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy import select

from app.celery_app import celery_app
from app.config import BaseAPIConfig
from app.database import AsyncSessionFactory
from app.models import (
    EmailAccount, EmailMessage, InvoiceRecord, InvoiceStatus,
    TenantSettings, DocumentType, DocumentSource
)

# ─── Constants ──────────────────────────────────────────────────────────────

ATTACHMENT_DIR = "/tmp/email_attachments"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

SUPPORTED_ATTACHMENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/tiff",
    "image/bmp",
    "image/gif",
}

# ─── Utility helpers ─────────────────────────────────────────────────────────

def _decode_header_value(value: str | None) -> str:
    if not value:
        return ""

    parts: list[str] = []
    for text, charset in decode_header(value):
        if isinstance(text, bytes):
            parts.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts).strip()


def _extract_amount(text: str) -> float:
    patterns = [
        r"(?:EUR|€)\s?([0-9]{1,3}(?:[.,\s][0-9]{3})*(?:[.,][0-9]{2}))",
        r"(?:USD|\$)\s?([0-9]{1,3}(?:[.,\s][0-9]{3})*(?:[.,][0-9]{2}))",
        r"([0-9]{1,3}(?:[.,\s][0-9]{3})*(?:[.,][0-9]{2}))\s?(?:EUR|€|USD|\$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_value = match.group(1).replace(" ", "")
            if raw_value.count(",") > 0 and raw_value.count(".") > 0:
                if raw_value.rfind(",") > raw_value.rfind("."):
                    raw_value = raw_value.replace(".", "").replace(",", ".")
                else:
                    raw_value = raw_value.replace(",", "")
            else:
                raw_value = raw_value.replace(",", ".")
            try:
                return float(raw_value)
            except ValueError:
                continue
    return 0.0


def _extract_snippet(text: str, limit: int = 220) -> str:
    normalized = " ".join(text.split())
    return html.unescape(normalized[:limit])


def _extract_gmail_body(payload: dict) -> str:
    """Recursively extracts plain-text body from a Gmail message payload."""
    mime_type = payload.get("mimeType", "")
    parts = payload.get("parts", [])

    # Leaf node with data
    if not parts:
        body_data = payload.get("body", {}).get("data", "")
        if body_data and mime_type == "text/plain":
            try:
                return base64.urlsafe_b64decode(body_data + "==").decode("utf-8", errors="replace")
            except Exception:
                return ""
        # If it's HTML and no plain text found, strip tags as fallback
        if body_data and mime_type == "text/html":
            try:
                raw_html = base64.urlsafe_b64decode(body_data + "==").decode("utf-8", errors="replace")
                clean = re.sub(r"<[^>]+>", " ", raw_html)
                return html.unescape(" ".join(clean.split()))
            except Exception:
                return ""
        return ""

    # Prefer text/plain in multipart
    plain_text = ""
    for part in parts:
        if part.get("mimeType") == "text/plain":
            plain_text += _extract_gmail_body(part)
    if plain_text:
        return plain_text

    # Fall back to any recursive part
    for part in parts:
        result = _extract_gmail_body(part)
        if result:
            return result
    return ""


def _classify_email(subject: str, body: str, sender: str) -> str:
    text = f"{subject} {body} {sender}".lower()
    if any(word in text for word in ["invoice", "fatura", "bill", "cobrança", "cobranca"]):
        return "Accounts Payable"
    if any(word in text for word in ["receipt", "recibo", "payment received", "paid"]):
        return "Receipt"
    return "Non-Financial"


# ─── Attachment extraction ────────────────────────────────────────────────────

def _save_gmail_attachments(
    service,
    message_id: str,
    payload: dict,
    tenant_id: str,
) -> list[dict]:
    """
    Recursively walks Gmail message payload to extract and save supported
    file attachments to disk.

    Returns a list of dicts: [{ "filename": str, "path": str, "mime_type": str }]
    """
    attachments = []

    def _walk(part: dict):
        mime_type = part.get("mimeType", "")
        filename = part.get("filename", "")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        if filename and mime_type in SUPPORTED_ATTACHMENT_TYPES and attachment_id:
            try:
                att_data = service.users().messages().attachments().get(
                    userId="me",
                    messageId=message_id,
                    id=attachment_id,
                ).execute()
                file_bytes = base64.urlsafe_b64decode(att_data["data"] + "==")
                safe_filename = re.sub(r"[^\w.\-]", "_", filename)
                dest_dir = os.path.join(ATTACHMENT_DIR, tenant_id)
                os.makedirs(dest_dir, exist_ok=True)
                file_path = os.path.join(dest_dir, f"{message_id}_{safe_filename}")
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                attachments.append({
                    "filename": filename,
                    "path": file_path,
                    "mime_type": mime_type,
                })
                print(f"Saved Gmail attachment: {file_path}")
            except Exception as e:
                print(f"Failed to save Gmail attachment '{filename}': {e}")

        for sub_part in part.get("parts", []):
            _walk(sub_part)

    _walk(payload)
    return attachments


def _save_imap_attachments(msg, message_id: str, tenant_id: str) -> list[dict]:
    """
    Extracts and saves supported IMAP email attachments to disk.

    Returns a list of dicts: [{ "filename": str, "path": str, "mime_type": str }]
    """
    attachments = []

    if not msg.is_multipart():
        return attachments

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        content_type = part.get_content_type()
        filename = part.get_filename()

        if filename and "attachment" in content_disposition and content_type in SUPPORTED_ATTACHMENT_TYPES:
            try:
                file_bytes = part.get_payload(decode=True)
                if not file_bytes:
                    continue
                safe_filename = re.sub(r"[^\w.\-]", "_", _decode_header_value(filename))
                dest_dir = os.path.join(ATTACHMENT_DIR, tenant_id)
                os.makedirs(dest_dir, exist_ok=True)
                file_path = os.path.join(dest_dir, f"{message_id}_{safe_filename}")
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                attachments.append({
                    "filename": safe_filename,
                    "path": file_path,
                    "mime_type": content_type,
                })
                print(f"Saved IMAP attachment: {file_path}")
            except Exception as e:
                print(f"Failed to save IMAP attachment '{filename}': {e}")

    return attachments


async def _save_outlook_attachments(
    client: httpx.AsyncClient,
    message_id: str,
    access_token: str,
    tenant_id: str,
) -> list[dict]:
    """
    Fetches and saves Microsoft Graph API attachments for an Outlook message.

    Returns a list of dicts: [{ "filename": str, "path": str, "mime_type": str }]
    """
    attachments = []
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    try:
        response = await client.get(
            f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments",
            headers=headers,
        )
        if response.status_code != 200:
            return attachments

        for att in response.json().get("value", []):
            if att.get("@odata.type") != "#microsoft.graph.fileAttachment":
                continue
            content_type = att.get("contentType", "")
            filename = att.get("name", "")
            content_bytes_b64 = att.get("contentBytes", "")

            if content_type in SUPPORTED_ATTACHMENT_TYPES and filename and content_bytes_b64:
                try:
                    file_bytes = base64.b64decode(content_bytes_b64)
                    safe_filename = re.sub(r"[^\w.\-]", "_", filename)
                    dest_dir = os.path.join(ATTACHMENT_DIR, tenant_id)
                    os.makedirs(dest_dir, exist_ok=True)
                    file_path = os.path.join(dest_dir, f"{message_id}_{safe_filename}")
                    with open(file_path, "wb") as f:
                        f.write(file_bytes)
                    attachments.append({
                        "filename": safe_filename,
                        "path": file_path,
                        "mime_type": content_type,
                    })
                    print(f"Saved Outlook attachment: {file_path}")
                except Exception as e:
                    print(f"Failed to save Outlook attachment '{filename}': {e}")
    except Exception as e:
        print(f"Failed to fetch Outlook attachments for message {message_id}: {e}")

    return attachments


# ─── DB helpers ─────────────────────────────────────────────────────────────

async def _store_email_record(
    db,
    account: EmailAccount,
    external_message_id: str | None,
    subject: str,
    sender: str,
    snippet: str,
    body_text: str,
    received_at: datetime,
) -> EmailMessage:
    result = await db.execute(
        select(EmailMessage).where(
            EmailMessage.account_id == account.id,
            EmailMessage.external_message_id == external_message_id,
        )
    )
    email_message = result.scalars().first()

    if email_message is None:
        email_message = EmailMessage(
            tenant_id=account.tenant_id,
            account_id=account.id,
            external_message_id=external_message_id,
            subject=subject,
            sender=sender,
            snippet=snippet,
            body=body_text,
            category=_classify_email(subject, body_text, sender),
            date=received_at,
            is_processed=False,
        )
        db.add(email_message)
    else:
        email_message.subject = subject
        email_message.sender = sender
        email_message.snippet = snippet
        email_message.body = body_text
        email_message.category = _classify_email(subject, body_text, sender)
        email_message.date = received_at

    return email_message


async def _get_tenant_iva_settings(db, tenant_id: str) -> tuple[float, str]:
    """Returns (iva_rate, currency) from TenantSettings or safe defaults."""
    result = await db.execute(
        select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
    )
    settings = result.scalars().first()
    if settings:
        return settings.iva_rate, settings.currency
    return 0.23, "EUR"  # Default PT values


# ─── LLM Processing ─────────────────────────────────────────────────────────

async def _process_email_with_llm(
    db,
    account: EmailAccount,
    email_message: EmailMessage,
    body_text: str,
    received_at: datetime,
    attachment_path: str | None = None,
    attachment_filename: str | None = None,
) -> None:
    """
    Full LLM extraction pipeline.

    If attachment_path is provided, the invoice record will link to the
    physical file and be shown as an OCR-pending document.

    If no attachment is provided, extraction runs purely on email body text —
    no file is registered and no OCR task is enqueued.

    Steps:
    1. Load tenant IVA settings
    2. Call Llama3 with RAG-structured prompt
    3. Create/update InvoiceRecord with IVA breakdown
    4. If attachment exists, link raw_document_url and enqueue OCR task
    5. Auto-reconcile payment receipts with existing invoices
    6. Mark as overdue if due_date < today
    """
    from app.extraction.llm_client import LLMExtractorClient

    iva_rate, currency = await _get_tenant_iva_settings(db, account.tenant_id)

    # Build the text to analyze:
    # - If we have an attachment, enrich the LLM prompt with email context (subject, sender, body)
    # - If no attachment, use the full email body as the primary source
    text_to_analyze = f"Subject: {email_message.subject}\nFrom: {email_message.sender}\n\n{body_text or email_message.snippet or ''}"
    if len(text_to_analyze.strip()) < 30:
        return

    try:
        client = LLMExtractorClient()
        extracted = await client.invoke_llm_chain(
            raw_text=text_to_analyze,
            tenant_iva_rate=iva_rate,
            currency=currency,
        )
    except Exception as e:
        print(f"LLM extraction failed for email {email_message.id}: {e}")
        extracted = None

    if not extracted or not extracted.is_valid_invoice:
        # Update email category even if not a valid financial doc
        if extracted:
            email_message.category = extracted.document_type
        return

    # Update email category from LLM
    email_message.category = extracted.document_type

    # Determine invoice status
    today = datetime.utcnow()
    due_date_obj = None
    if extracted.due_date:
        try:
            due_date_obj = datetime.strptime(extracted.due_date, "%Y-%m-%d")
        except Exception:
            pass
    if not due_date_obj:
        due_date_obj = received_at + timedelta(days=30)

    # Determine initial status
    if extracted.document_type == DocumentType.PAYMENT_RECEIPT.value:
        invoice_status = InvoiceStatus.PAID.value
    elif due_date_obj < today and extracted.document_type == DocumentType.ACCOUNTS_PAYABLE.value:
        invoice_status = InvoiceStatus.RECONCILIATION.value
    else:
        invoice_status = InvoiceStatus.PENDING.value

    # Issue date parsing
    issue_date_obj = received_at
    if extracted.issue_date:
        try:
            issue_date_obj = datetime.strptime(extracted.issue_date, "%Y-%m-%d")
        except Exception:
            pass

    # Upsert InvoiceRecord
    result = await db.execute(
        select(InvoiceRecord).where(
            InvoiceRecord.tenant_id == account.tenant_id,
            InvoiceRecord.invoice_number == (extracted.invoice_number or email_message.external_message_id),
        )
    )
    invoice = result.scalars().first()

    vendor_name = extracted.vendor_name or (
        email_message.sender.split("<")[0].strip().replace('"', '') or email_message.sender
    )

    if invoice is None:
        invoice = InvoiceRecord(
            tenant_id=account.tenant_id,
            document_type=extracted.document_type,
            vendor_name=vendor_name,
            invoice_number=extracted.invoice_number or email_message.external_message_id,
            issue_date=issue_date_obj,
            due_date=due_date_obj,
            currency=currency,
            iva_rate=extracted.iva_rate or iva_rate,
            net_amount=extracted.net_amount,
            iva_amount=extracted.iva_amount,
            subtotal=extracted.net_amount,
            tax_amount=extracted.iva_amount,
            total_amount=extracted.total_amount,
            status=invoice_status,
            payment_reference=extracted.payment_reference,
            iban=extracted.iban,
            swift=extracted.swift,
            confidence_score=0.85 if extracted.total_amount > 0 else 0.60,
            # Only set the file path if there's an actual physical attachment
            raw_document_url=attachment_path,
            source=DocumentSource.EMAIL.value,
        )
        db.add(invoice)
    else:
        invoice.document_type = extracted.document_type
        invoice.vendor_name = vendor_name
        invoice.due_date = due_date_obj
        invoice.currency = currency
        invoice.iva_rate = extracted.iva_rate or iva_rate
        if extracted.total_amount > 0:
            invoice.net_amount = extracted.net_amount
            invoice.iva_amount = extracted.iva_amount
            invoice.subtotal = extracted.net_amount
            invoice.tax_amount = extracted.iva_amount
            invoice.total_amount = extracted.total_amount
        invoice.payment_reference = extracted.payment_reference or invoice.payment_reference
        invoice.status = invoice_status
        # Only update file path if we now have an attachment (don't overwrite existing)
        if attachment_path and not invoice.raw_document_url:
            invoice.raw_document_url = attachment_path

    await db.flush()  # Get the ID without committing

    # Enqueue OCR task only if there is a real physical file
    if attachment_path and os.path.exists(attachment_path):
        from app.tasks.ocr_tasks import enqueue_ocr_job
        enqueue_ocr_job.delay(
            document_url=attachment_path,
            invoice_id=invoice.id,
            tenant_id=account.tenant_id,
        )
        print(f"Enqueued OCR job for attachment: {attachment_path} → invoice {invoice.id}")
    else:
        print(f"No physical attachment for email {email_message.id} — OCR task NOT enqueued (body-text extraction only).")

    # Vector Store Indexing (ChromaDB)
    # For body-text emails: the full email body is the primary content.
    # For attachment emails: a lightweight index is created now; the OCR task
    # will upsert a richer version after extracting text from the file.
    try:
        from app.services.vector_store import VectorStoreService
        await VectorStoreService.index_invoice(
            invoice=invoice,
            raw_text=text_to_analyze,
            tenant_id=account.tenant_id,
        )
    except Exception as ve:
        print(f"[VectorStore] Warning: async indexing failed for invoice {invoice.id}: {ve}")
        # Non-critical — do not fail the email processing pipeline

    # Auto-reconciliation for payment receipts
    if extracted.document_type == DocumentType.PAYMENT_RECEIPT.value and extracted.linked_invoice_number:
        await _try_auto_reconcile(db, account.tenant_id, invoice, extracted.linked_invoice_number)



async def _try_auto_reconcile(db, tenant_id: str, receipt_invoice: InvoiceRecord, linked_number: str) -> None:
    """
    Attempts to match a payment receipt with an existing accounts_payable invoice.
    If match found with high confidence, marks the payable as PAID.
    """
    result = await db.execute(
        select(InvoiceRecord).where(
            InvoiceRecord.tenant_id == tenant_id,
            InvoiceRecord.invoice_number == linked_number,
            InvoiceRecord.document_type == DocumentType.ACCOUNTS_PAYABLE.value,
        )
    )
    payable = result.scalars().first()

    if payable:
        # Check amount tolerance ±5%
        if receipt_invoice.total_amount > 0:
            tolerance = abs(payable.total_amount - receipt_invoice.total_amount) / max(payable.total_amount, 0.01)
            if tolerance <= 0.05:  # Within 5%
                payable.status = InvoiceStatus.PAID.value
                payable.linked_to_id = receipt_invoice.id
                print(f"Auto-reconciled: receipt {receipt_invoice.id} → invoice {payable.id} (tolerance: {tolerance:.1%})")
            else:
                payable.status = InvoiceStatus.REVIEW_REQUIRED.value
                print(f"Reconciliation review needed: amount mismatch {tolerance:.1%} for invoice {payable.invoice_number}")
        else:
            # No amount but reference matches — mark as review
            payable.status = InvoiceStatus.REVIEW_REQUIRED.value


# ─── Provider sync functions ─────────────────────────────────────────────────

async def _sync_google_account(db, account: EmailAccount):
    settings = BaseAPIConfig.get_settings()
    creds = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        account.access_token = creds.token

    service = build("gmail", "v1", credentials=creds)
    response = service.users().messages().list(userId="me", maxResults=25, q="in:inbox").execute()
    messages = response.get("messages", [])

    for item in messages:
        message = service.users().messages().get(
            userId="me",
            id=item["id"],
            format="full",
        ).execute()

        payload = message.get("payload", {})
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        subject = _decode_header_value(headers.get("subject"))
        sender = _decode_header_value(headers.get("from"))
        date_header = headers.get("date")
        received_at = datetime.utcnow()
        if date_header:
            try:
                received_at = parsedate_to_datetime(date_header).replace(tzinfo=None)
            except Exception:
                pass

        body_text = _extract_gmail_body(payload)
        snippet = _extract_snippet(message.get("snippet", "") or body_text)

        email_message = await _store_email_record(
            db,
            account,
            external_message_id=message.get("id"),
            subject=subject or "No Subject",
            sender=sender or account.email_address,
            snippet=snippet,
            body_text=body_text,
            received_at=received_at,
        )

        # Extract attachments from Gmail
        attachments = _save_gmail_attachments(
            service=service,
            message_id=message["id"],
            payload=payload,
            tenant_id=account.tenant_id,
        )

        if attachments:
            # Process each attachment as a separate invoice record
            for att in attachments:
                await _process_email_with_llm(
                    db, account, email_message, body_text or snippet, received_at,
                    attachment_path=att["path"],
                    attachment_filename=att["filename"],
                )
        else:
            # No attachments — process body text only (no OCR task, no file record)
            await _process_email_with_llm(
                db, account, email_message, body_text or snippet, received_at,
                attachment_path=None,
                attachment_filename=None,
            )


async def _sync_outlook_account(db, account: EmailAccount):
    settings = BaseAPIConfig.get_settings()
    token_payload: dict[str, Any] = {}

    async with httpx.AsyncClient(timeout=20.0) as client:
        if account.refresh_token:
            token_response = await client.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data={
                    "client_id": settings.microsoft_client_id,
                    "client_secret": settings.microsoft_client_secret,
                    "refresh_token": account.refresh_token,
                    "grant_type": "refresh_token",
                    "scope": "offline_access openid profile email https://graph.microsoft.com/Mail.Read",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            account.access_token = token_payload.get("access_token", account.access_token)
        else:
            token_payload["access_token"] = account.access_token

        access_token = token_payload.get("access_token", account.access_token)
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$top=500&$orderby=receivedDateTime desc",
            headers=headers,
        )
        response.raise_for_status()

        for message in response.json().get("value", []):
            subject = message.get("subject") or "No Subject"
            sender = message.get("from", {}).get("emailAddress", {}).get("address") or account.email_address
            received_at_raw = message.get("receivedDateTime")
            received_at = datetime.utcnow()
            if received_at_raw:
                try:
                    received_at = datetime.fromisoformat(received_at_raw.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    pass

            snippet = _extract_snippet(message.get("bodyPreview", ""))
            body_text = message.get("body", {}).get("content", "")

            if body_text and "<" in body_text and ">" in body_text:
                try:
                    from bs4 import BeautifulSoup
                    body_text = BeautifulSoup(body_text, "html.parser").get_text(separator="\n", strip=True)
                except ImportError:
                    pass

            if not body_text:
                body_text = snippet

            email_message = await _store_email_record(
                db,
                account,
                external_message_id=message.get("id"),
                subject=subject,
                sender=sender,
                snippet=snippet,
                body_text=body_text,
                received_at=received_at,
            )

            # Check if email has attachments
            has_attachments = message.get("hasAttachments", False)
            if has_attachments:
                attachments = await _save_outlook_attachments(
                    client=client,
                    message_id=message["id"],
                    access_token=access_token,
                    tenant_id=account.tenant_id,
                )
                if attachments:
                    for att in attachments:
                        await _process_email_with_llm(
                            db, account, email_message, body_text, received_at,
                            attachment_path=att["path"],
                            attachment_filename=att["filename"],
                        )
                    continue

            # No valid attachments — process body only
            await _process_email_with_llm(
                db, account, email_message, body_text, received_at,
                attachment_path=None,
                attachment_filename=None,
            )


async def _sync_imap_account(db, account: EmailAccount):
    import imaplib
    import email

    imap_server = "imap.gmail.com"
    if account.provider == "outlook":
        imap_server = "outlook.office365.com"

    password = account.refresh_token or account.access_token
    if not password:
        raise ValueError("Generic IMAP accounts require a password or app password.")

    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(account.email_address, password)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split() if status == "OK" and messages and messages[0] else []
    recent_ids = email_ids[-500:] if len(email_ids) > 500 else email_ids

    for e_id in reversed(recent_ids):
        res, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if not isinstance(response_part, tuple):
                continue

            msg = message_from_bytes(response_part[1])
            subject = _decode_header_value(msg.get("Subject"))
            sender = _decode_header_value(msg.get("From")) or account.email_address
            date_str = msg.get("Date")
            received_at = datetime.utcnow()
            if date_str:
                try:
                    received_at = parsedate_to_datetime(date_str).replace(tzinfo=None)
                except Exception:
                    pass

            # Extract body (text only, not attachments)
            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body_text += part.get_payload(decode=True).decode(errors="ignore")
                        except Exception:
                            pass
            else:
                try:
                    body_text = msg.get_payload(decode=True).decode(errors="ignore")
                except Exception:
                    body_text = ""

            snippet = _extract_snippet(body_text or subject)
            external_message_id = _decode_header_value(msg.get("Message-ID")) or e_id.decode("utf-8", errors="ignore")

            email_message = await _store_email_record(
                db,
                account,
                external_message_id=external_message_id,
                subject=subject or "No Subject",
                sender=sender,
                snippet=snippet,
                body_text=body_text,
                received_at=received_at,
            )

            # Extract IMAP attachments
            attachments = _save_imap_attachments(
                msg=msg,
                message_id=external_message_id,
                tenant_id=account.tenant_id,
            )

            if attachments:
                for att in attachments:
                    await _process_email_with_llm(
                        db, account, email_message, body_text, received_at,
                        attachment_path=att["path"],
                        attachment_filename=att["filename"],
                    )
            else:
                await _process_email_with_llm(
                    db, account, email_message, body_text, received_at,
                    attachment_path=None,
                    attachment_filename=None,
                )

    mail.close()
    mail.logout()


# ─── Celery Task ─────────────────────────────────────────────────────────────

async def _sync_logic(account_id: str):
    async with AsyncSessionFactory() as db:
        try:
            result = await db.execute(select(EmailAccount).where(EmailAccount.id == account_id))
            account = result.scalars().first()
            if not account:
                print(f"Account {account_id} not found for sync.")
                return

            print(f"Synchronizing account: {account.email_address} ({account.provider})")

            if account.provider == "google":
                await _sync_google_account(db, account)
            elif account.provider == "outlook":
                await _sync_outlook_account(db, account)
            else:
                await _sync_imap_account(db, account)

            account.last_synced_at = datetime.utcnow()
            await db.commit()
            print(f"Successfully synced inbox for {account.email_address}")
        except Exception as e:
            print(f"Error syncing account {account_id}: {e}")
            await db.rollback()


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task
def sync_email_account_task(account_id: str):
    """
    Synchronizes a linked email account and stores inbox messages locally.
    """
    _run_async(_sync_logic(account_id))
