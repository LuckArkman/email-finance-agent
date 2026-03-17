import os
import msal
import httpx
from typing import Dict, Any, Optional

class OAuthTokenHandler:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str, authority: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = authority or f"https://login.microsoftonline.com/{tenant_id}"
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )

    async def acquire_token_silent(self, scopes: list[str], account: Optional[dict] = None) -> Optional[str]:
        """Attempts to acquire a token silently from MSAL cache."""
        result = self.app.acquire_token_silent(scopes, account=account)
        if result and "access_token" in result:
            return result["access_token"]
        return None

    async def refresh_access_token(self, scopes: list[str]) -> Optional[str]:
        """Acquires a new token using client credentials if silent fails (for daemon/service app)."""
        result = self.app.acquire_token_for_client(scopes=scopes)
        if "access_token" in result:
            return result["access_token"]
        print(f"Error acquiring token: {result.get('error')}")
        print(f"Error description: {result.get('error_description')}")
        return None


class MSGraphClient:
    def __init__(self, token_handler: OAuthTokenHandler):
        self.token_handler = token_handler
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.scopes = ["https://graph.microsoft.com/.default"]

    async def _get_headers(self) -> dict:
        token = await self.token_handler.acquire_token_silent(self.scopes)
        if not token:
            token = await self.token_handler.refresh_access_token(self.scopes)
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

    async def get_recent_messages(self, user_id: str, top: int = 10) -> list[dict]:
        """Requisições GET para o endpoint /me/messages (or /users/{id}/messages)"""
        headers = await self._get_headers()
        url = f"{self.base_url}/users/{user_id}/messages?$top={top}&$filter=isRead eq false"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("value", [])


class GraphWebhookManager:
    def __init__(self, graph_client: MSGraphClient):
        self.graph_client = graph_client

    async def subscribe_to_inbox(self, user_id: str, notification_url: str, expiration_date_time: str) -> Dict[str, Any]:
        """Criação de Webhooks (Subscriptions) no Graph API para notificações em tempo real."""
        headers = await self.graph_client._get_headers()
        url = f"{self.graph_client.base_url}/subscriptions"
        
        payload = {
            "changeType": "created",
            "notificationUrl": notification_url,
            "resource": f"users/{user_id}/mailFolders('Inbox')/messages",
            "expirationDateTime": expiration_date_time,
            "clientState": "secretClientValue" # Usually a validation secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
