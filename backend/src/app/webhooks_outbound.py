import httpx
import hmac
import hashlib
import json
import logging
from typing import Any, Dict
from app.config import BaseAPIConfig

logger = logging.getLogger("uvicorn")

class WebhookOutboundService:
    """
    Service for sending event notifications to external systems (Zapier, Make, etc.).
    Supports HMAC signing for outbound security.
    """
    
    @staticmethod
    async def emit_trigger_workflow(event_name: str, payload: Dict[str, Any], target_url: str, secret: str = None):
        """
        Sends an HTTP POST call to the external ERP/Automation tool.
        """
        if not target_url:
            logger.warning(f"No target URL defined for event {event_name}. Skipping outbound webhook.")
            return

        json_data = {
            "event": event_name,
            "data": payload,
            "timestamp": json.dumps(json.loads(json.dumps(payload)), default=str) # Simplified timestamping
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "LuckArkman-Finance-Agent/1.0"
        }

        # If a secret is provided, sign the payload
        if secret:
            signature = hmac.new(
                secret.encode(),
                json.dumps(json_data).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-LuckArkman-Signature"] = signature

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(target_url, json=json_data, headers=headers, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Outbound Webhook {event_name} sent successfully to {target_url}")
                return True
        except Exception as e:
            logger.error(f"Failed to send outbound webhook {event_name}: {str(e)}")
            return False
