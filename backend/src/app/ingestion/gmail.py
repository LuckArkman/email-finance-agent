import os
import io
import asyncio
from typing import List, Dict, Any, Callable, Awaitable
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.cloud import pubsub_v1
import base64

class GmailAPIClient:
    def __init__(self, credentials_path: str, scopes: List[str]):
        """
        Manage GCP Credentials (Service Account or User Auth).
        Defaulting mostly to Service Account for background tasks,
        but can adapt to user OAuth if needed.
        """
        self.credentials_path = credentials_path
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.readonly']
        self.creds = None
        self.service = None

    def build_gmail_service(self, delegate_email: str = None):
        """Builds and returns the Gmail resource service instance."""
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Flow focusing on Service Account logic for daemon processes
                if os.path.exists(self.credentials_path):
                    self.creds = Credentials.from_service_account_file(
                        self.credentials_path, scopes=self.scopes
                    )
                    # For Service Accounts, impersonate a regular user in workspace
                    if delegate_email:
                        self.creds = self.creds.with_subject(delegate_email)
                else:
                    print("Google Credentials file not found!")
                    return None

        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Gmail service successfully built.")
        return self.service

    async def list_messages(self, user_id: str = 'me', max_results: int = 20, query: str = "is:unread has:attachment") -> List[Dict[str, Any]]:
        """Uso do google-api-python-client para listar IDs de emails com filtros."""
        if not self.service:
            print("Service not initialized. Call build_gmail_service first.")
            return []

        try:
            # Note: The raw python client is mostly synchronous, 
            # in a highly async app we would ideally run this inside a ThreadPool or use an async wrap.
            loop = asyncio.get_event_loop()
            request = self.service.users().messages().list(userId=user_id, maxResults=max_results, q=query)
            response = await loop.run_in_executor(None, request.execute)
            
            messages = response.get('messages', [])
            return messages
        except Exception as error:
            print(f"An error occurred listing messages: {error}")
            return []

    async def download_message_raw(self, message_id: str, user_id: str = 'me') -> Dict[str, Any]:
        """Downloads the full raw base64 content of a message."""
        if not self.service:
            return {}
        try:
            loop = asyncio.get_event_loop()
            request = self.service.users().messages().get(userId=user_id, id=message_id, format='raw')
            message = await loop.run_in_executor(None, request.execute)
            
            raw_email_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8', errors='replace')
            return {"id": message['id'], "raw": raw_email_str}
        except Exception as error:
            print(f"An error occurred fetching message {message_id}: {error}")
            return {}


class GooglePubSubListener:
    """
    Integração com Google Pub/Sub para push notifications de chegada de emails.
    O Gmail notifica um topico do GCP -> que entrega para nosso backend instaneamente.
    """
    def __init__(self, project_id: str, subscription_id: str):
        self.project_id = project_id
        self.subscription_id = subscription_id
        self.subscriber = None
        self.subscription_path = None

    def start_listening(self, callback_func: Callable[[pubsub_v1.subscriber.message.Message], None]) -> None:
        """Starts a background thread to listen for new incoming messages on Pub/Sub."""
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_id)
        
        print(f"Listening for Gmail Push Notifications on {self.subscription_path}...")
        
        # Starts the async streaming pull in background child threads.
        future = self.subscriber.subscribe(self.subscription_path, callback=callback_func)
        try:
            # We would typically join or await future.result() in a dedicated worker.
            pass
        except Exception as exc:
            print(f"Pub/Sub exception: {exc}")
            future.cancel()

