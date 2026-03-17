import datetime
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

from app.config import BaseAPIConfig

client: Optional[AsyncIOMotorClient] = None

class AsyncMongoManager:
    @staticmethod
    def get_client() -> AsyncIOMotorClient:
        if client is None:
            raise Exception("Mongo Client is not initialized.")
        return client

    @staticmethod
    def get_db():
        settings = BaseAPIConfig.get_settings()
        return AsyncMongoManager.get_client()[settings.mongo_db_name]


async def init_mongo_client():
    global client
    settings = BaseAPIConfig.get_settings()
    client = AsyncIOMotorClient(settings.mongo_url)

async def close_mongo_client():
    global client
    if client is not None:
        client.close()

# Schemas Extracted from requirements
class RawEmailModel(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(datetime.datetime.utcnow().timestamp()))
    message_id: str
    subject: str
    sender: str
    recipient: str
    date: datetime.datetime
    raw_body: str
    attachments_metadata: list[Dict[str, Any]] = []
    processed: bool = False

class AIResultPayload(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(datetime.datetime.utcnow().timestamp()))
    invoice_id: str
    raw_ocr_text: str
    extracted_json: Dict[str, Any]
    model_used: str
    confidence_metrics: Dict[str, float]

async def insert_raw_email_document(data: RawEmailModel):
    db = AsyncMongoManager.get_db()
    collection = db["raw_emails"]
    # We dump model excluding unset properties, and map alias to DB friendly keys if needed
    result = await collection.insert_one(data.model_dump(by_alias=True))
    return result
