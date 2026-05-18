from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserRegister(UserBase):
    password: str
    tenant_name: str

class UserResponse(UserBase):
    id: str
    tenant_id: str
    is_active: bool

    class Config:
        from_attributes = True

class EmailAccountBase(BaseModel):
    provider: str
    email_address: str

class EmailAccountCreate(EmailAccountBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class EmailAccountResponse(EmailAccountBase):
    id: str
    tenant_id: str
    is_active: bool
    last_synced_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SimpleEmailDTO(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    category: str # Extracted or predicted category
    snippet: str

class ReviewItemResponse(BaseModel):
    id: str
    invoice_id: str
    tenant_id: str
    status: str
    confidence_score: float
    reason: Optional[str] = None
    created_at: datetime
    
    # Nested invoice info if needed
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: str
    tenant_id: str
    invoice_id: Optional[str] = None
    description: Optional[str] = None
    amount: float
    payment_date: datetime
    is_reconciled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AISuggestion(BaseModel):
    id: str
    transaction_id: str
    invoice_id: str
    confidence: float
    vendor_name: str
    document_name: str
    amount: float

class ReviewResolveRequest(BaseModel):
    action: str # approve, reject
    notes: Optional[str] = None
