import httpx
from app.config import BaseAPIConfig

class WhatsAppMessagingService:
    """
    Handles outbound communication with users via Meta Cloud API.
    Used for order confirmations, extraction updates, and alerts.
    """
    
    @staticmethod
    async def send_text_message(to: str, text: str):
        settings = BaseAPIConfig.get_settings()
        token = settings.whatsapp_access_token
        phone_id = settings.whatsapp_phone_number_id
        
        if not token or not phone_id:
            print("WhatsApp Messaging not configured. Skipping confirmation.")
            return

        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                print(f"WhatsApp notification sent to {to}")
            except Exception as e:
                print(f"Failed to send WhatsApp message to {to}: {e}")
