from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Query
from app.config import BaseAPIConfig
from app.tasks.ocr_tasks import enqueue_ocr_job
import httpx
import os
import uuid

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp Ingestion"])

# Helper to provide environment settings
get_settings = BaseAPIConfig.get_settings

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Standard Meta Webhook verification (GET).
    Checks if the hub.verify_token matches ours.
    """
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        print("WhatsApp Webhook verified successfully.")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_whatsapp_notification(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming WhatsApp messages (POST).
    Offloads media downloading to background to ensure instant ACK to Meta.
    """
    data = await request.json()
    
    try:
        # Check standard Meta Cloud API payload structure
        entry = data.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "event_acknowledged"}
            
        msg = messages[0]
        msg_type = msg.get("type")
        sender_phone = msg.get("from") # Used as fallback tenant_id
        
        if msg_type in ["image", "document"]:
            media_id = msg.get(msg_type, {}).get("id")
            filename = msg.get(msg_type, {}).get("filename", f"wa_{media_id}")
            
            # Dispatch background download and processing
            background_tasks.add_task(
                download_and_process_whatsapp_media, 
                media_id, 
                filename, 
                sender_phone
            )
            
        return {"status": "processed"}
        
    except (IndexError, KeyError) as e:
        print(f"Malformated WhatsApp Webhook: {e}")
        return {"status": "error", "message": "payload mismatch"}

async def download_and_process_whatsapp_media(media_id: str, filename: str, sender: str):
    """
    Performs the 2-step media download from Meta Graph API.
    1. Resolve URL from ID
    2. Download Binary
    """
    settings = get_settings()
    token = settings.whatsapp_access_token
    if not token:
        print("Warning: WHATSAPP_ACCESS_TOKEN not set. Cannot download media.")
        return

    # 1. Fetch URL from Graph API
    url = f"https://graph.facebook.com/v19.0/{media_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            media_info = resp.json()
            download_url = media_info.get("url")
            
            if not download_url:
                print(f"Could not retrieve download URL for media {media_id}")
                return
            
            # 2. Download the binary
            file_resp = await client.get(download_url, headers=headers)
            file_resp.raise_for_status()
            
            # Save to shared volume /tmp/uploads
            upload_dir = "/tmp/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Use unique name to avoid collision
            unique_filename = f"wa_{uuid.uuid4().hex[:8]}_{filename}"
            full_path = f"{upload_dir}/{unique_filename}"
            
            with open(full_path, "wb") as f:
                f.write(file_resp.content)
            
            print(f"WhatsApp Media saved to: {full_path}. Dispatching to AI Brain...")
            
            # 3. Trigger OCR and Llama 3 Extraction
            from app.tasks.ocr_tasks import enqueue_ocr_job
            enqueue_ocr_job.delay(
                document_url=full_path, 
                invoice_id=f"WA-{media_id}", # Generating virtual ID
                tenant_id=sender # Using phone number as tenant identifier
            )
            
        except Exception as e:
            print(f"Error downloading WhatsApp media {media_id}: {e}")
