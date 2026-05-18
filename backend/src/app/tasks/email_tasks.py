import asyncio
import re
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
from app.models import EmailAccount, EmailMessage, InvoiceRecord, InvoiceStatus


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
    return normalized[:limit]


def _classify_email(subject: str, body: str, sender: str) -> str:
    text = f"{subject} {body} {sender}".lower()
    if any(word in text for word in ["invoice", "fatura", "bill", "cobrança", "cobranca"]):
        return "Accounts Payable"
    if any(word in text for word in ["receipt", "recibo", "payment received", "paid"]):
        return "Receipt"
    return "Non-Financial"


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
            category=_classify_email(subject, body_text, sender),
            date=received_at,
            is_processed=False,
        )
        db.add(email_message)
    else:
        email_message.subject = subject
        email_message.sender = sender
        email_message.snippet = snippet
        email_message.category = _classify_email(subject, body_text, sender)
        email_message.date = received_at

    return email_message


async def _create_invoice_if_needed(db, account: EmailAccount, email_message: EmailMessage, body_text: str, received_at: datetime):
    if email_message.category not in {"Accounts Payable", "Receipt"}:
        return

    amount = _extract_amount(f"{email_message.subject} {body_text} {email_message.snippet}")
    vendor_name = email_message.sender.split("<")[0].strip().replace('"', '') or email_message.sender or "Unknown Vendor"
    due_date = received_at + timedelta(days=15)

    result = await db.execute(
        select(InvoiceRecord).where(
            InvoiceRecord.tenant_id == account.tenant_id,
            InvoiceRecord.vendor_name == vendor_name,
            InvoiceRecord.invoice_number == email_message.external_message_id,
        )
    )
    invoice = result.scalars().first()

    if invoice is None:
        invoice = InvoiceRecord(
            tenant_id=account.tenant_id,
            vendor_name=vendor_name,
            invoice_number=email_message.external_message_id,
            issue_date=received_at,
            due_date=due_date,
            total_amount=amount,
            status=InvoiceStatus.PENDING.value,
            confidence_score=0.65 if amount == 0 else 0.82,
            raw_document_url=None,
        )
        db.add(invoice)
    else:
        invoice.vendor_name = vendor_name
        invoice.issue_date = received_at
        invoice.due_date = due_date
        if amount > 0:
            invoice.total_amount = amount


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
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"].lower(): h["value"] for h in message.get("payload", {}).get("headers", [])}
        subject = _decode_header_value(headers.get("subject"))
        sender = _decode_header_value(headers.get("from"))
        date_header = headers.get("date")
        received_at = datetime.utcnow()
        if date_header:
            try:
                received_at = parsedate_to_datetime(date_header).replace(tzinfo=None)
            except Exception:
                pass

        snippet = _extract_snippet(message.get("snippet", ""))
        email_message = await _store_email_record(
            db,
            account,
            external_message_id=message.get("id"),
            subject=subject or "No Subject",
            sender=sender or account.email_address,
            snippet=snippet,
            body_text=snippet,
            received_at=received_at,
        )
        await _create_invoice_if_needed(db, account, email_message, snippet, received_at)


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

        headers = {
            "Authorization": f"Bearer {token_payload.get('access_token', account.access_token)}",
            "Accept": "application/json",
        }
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$top=25&$orderby=receivedDateTime desc",
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
            email_message = await _store_email_record(
                db,
                account,
                external_message_id=message.get("id"),
                subject=subject,
                sender=sender,
                snippet=snippet,
                body_text=snippet,
                received_at=received_at,
            )
            await _create_invoice_if_needed(db, account, email_message, snippet, received_at)


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
    recent_ids = email_ids[-15:] if len(email_ids) > 15 else email_ids

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

            body_text = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
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
            await _create_invoice_if_needed(db, account, email_message, body_text, received_at)

    mail.close()
    mail.logout()


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


@celery_app.task
def sync_email_account_task(account_id: str):
    """
    Synchronizes a linked email account and stores inbox messages locally.
    """
    asyncio.run(_sync_logic(account_id))
