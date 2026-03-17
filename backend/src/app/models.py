from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Integer, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import BaseModel

class TenantStatus(enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class InvoiceStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    REVIEW_REQUIRED = "review_required"

def generate_uuid() -> str:
    return str(uuid4())

class Tenant(BaseModel):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    status = Column(String, default=TenantStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="tenant")
    invoices = relationship("InvoiceRecord", back_populates="tenant")

class User(BaseModel):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")

class InvoiceRecord(BaseModel):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    vendor_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    issue_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String, default="BRL")
    
    status = Column(String, default=InvoiceStatus.PENDING.value)
    confidence_score = Column(Float, default=0.0)
    raw_document_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="invoices")
    payments = relationship("Transaction", back_populates="invoice")

class Transaction(BaseModel):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)
    
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    reference_id = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    invoice = relationship("InvoiceRecord", back_populates="payments")

class ReviewQueueModel(BaseModel):
    """
    Queue to isolate documents correctly parsed but waiting on human approval
    due to low Confidence Score.
    """
    __tablename__ = "review_queue"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True) # Analyst reviewing it
    status = Column(String, default="pending_review") # pending_review, approved, rejected
    confidence_score = Column(Float, default=0.0)
    
    reason = Column(Text, nullable=True) # e.g. "Low OCR confidence on Total Amount"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
class WebhookConfig(BaseModel):
    """
    Configuration for outbound webhooks per tenant (Zapier, Make, etc.).
    """
    __tablename__ = "webhook_configs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), unique=True, nullable=False)
    
    target_url = Column(String, nullable=True)
    secret_key = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant")
