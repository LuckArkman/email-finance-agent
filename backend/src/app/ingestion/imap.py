import asyncio
import email
from email.message import Message
from email.header import decode_header
from typing import List, Optional
import aioimaplib
from pydantic import BaseModel
from datetime import datetime

class EmailMessageDTO(BaseModel):
    subject: str
    sender: str
    recipient: str
    date: str
    raw_body: str
    message_id: str

class IMAPConnectionManager:
    def __init__(self, host: str, user: str, password: str, port: int = 993):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.client: Optional[aioimaplib.IMAP4_SSL] = None

    async def login_imap(self) -> bool:
        """Connects to the IMAP server and logs in."""
        try:
            self.client = aioimaplib.IMAP4_SSL(host=self.host, port=self.port)
            await self.client.wait_hello_from_server()
            response = await self.client.login(self.user, self.password)
            if response.result == 'OK':
                print(f"Successfully connected to IMAP: {self.user}")
                return True
            else:
                print(f"Failed to log in: {response.lines}")
        except Exception as e:
            print(f"IMAP login error: {e}")
        return False

    async def fetch_unseen_emails(self) -> List[EmailMessageDTO]:
        """Fetches all unseen emails in the INBOX."""
        emails_dto = []
        if not self.client:
            return emails_dto
            
        await self.client.select('INBOX')
        status, response = await self.client.search('UNSEEN')
        if status == 'OK' and response[0]:
            email_ids = response[0].split()
            for eid in email_ids:
                status, data = await self.client.fetch(eid, '(RFC822)')
                if status == 'OK':
                    # Parse the raw email bytes
                    raw_email = data[1]
                    email_msg = email.message_from_bytes(raw_email)
                    dto = self.parse_email_headers(email_msg)
                    emails_dto.append(dto)
        return emails_dto

    def parse_email_headers(self, msg: Message) -> EmailMessageDTO:
        """Extracts and decodes headers and plain text body into a DTO."""
        def decode_field(field_value: str) -> str:
            if not field_value:
                return ""
            decoded_parts = decode_header(field_value)
            parts = []
            for text, charset in decoded_parts:
                if isinstance(text, bytes):
                    parts.append(text.decode(charset or 'utf-8', errors='replace'))
                else:
                    parts.append(text)
            return "".join(parts)

        subject = decode_field(msg.get("Subject", ""))
        sender = decode_field(msg.get("From", ""))
        recipient = decode_field(msg.get("To", ""))
        message_id = msg.get("Message-ID", "")
        date = msg.get("Date", "")
        
        # Get raw body text
        raw_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        raw_body += part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                raw_body = msg.get_payload(decode=True).decode()
            except:
                pass
                
        return EmailMessageDTO(
            subject=subject,
            sender=sender,
            recipient=recipient,
            date=date,
            raw_body=raw_body,
            message_id=message_id
        )

    async def start_idle_loop(self):
        """Starts an IDLE connection to wait for new emails."""
        if not self.client:
            return
            
        print("Entering IMAP IDLE mode...")
        await self.client.select('INBOX')
        
        while True:
            try:
                # Use IDLE
                response = await self.client.idle_start()
                # Wait for response logic goes here... This is a naive busy wait or specialized wait
                # depending on the aioimaplib capabilities.
                # await self.client.wait_server_push()
                await asyncio.sleep(60) # We wake up every 60 seconds or on push
                self.client.idle_done()
                
                # Fetch new ones
                new_emails = await self.client.fetch_unseen_emails()
                for em in new_emails:
                    print(f"New incoming invoice email: {em.subject}")
                    
            except Exception as e:
                print(f"IDLE exception: {e}")
                await asyncio.sleep(10)

