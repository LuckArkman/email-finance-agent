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

class DocumentSource(enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    MANUAL = "manual"

class DocumentType(enum.Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    OTHER = "other"

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
    email_accounts = relationship("EmailAccount", back_populates="tenant")

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
    source = Column(String, default=DocumentSource.EMAIL.value)
    document_type = Column(String, default=DocumentType.INVOICE.value)
    
    confidence_score = Column(Float, default=0.0)
    raw_document_url = Column(String, nullable=True)
    
    # Matching/Reconciliation
    linked_to_id = Column(String, ForeignKey("invoices.id"), nullable=True)
    
    # Granular Financials
    iban = Column(String, nullable=True)
    swift = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="invoices")
    payments = relationship("Transaction", back_populates="invoice")
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")

class LineItem(BaseModel):
    __tablename__ = "invoice_line_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    
    invoice = relationship("InvoiceRecord", back_populates="line_items")

class AuditLog(BaseModel):
    """
    Immutable audit trail for every action performed within the tenant context.
    Essential for financial compliance and fraud detection.
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # System actions might have null user
    
    action = Column(String, nullable=False) # e.g. "INVOICE_EDIT", "DOC_UPLOAD", "AUTH_LOGIN"
    resource_type = Column(String, nullable=False) # "invoice", "user", "tenant"
    resource_id = Column(String, nullable=True)
    
    details = Column(Text, nullable=True) # JSON blob or description of changes
    ip_address = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailAccount(BaseModel):
    """
    Linked email accounts (Gmail, MS Outlook, Generic IMAP) for the tenant.
    """
    __tablename__ = "email_accounts"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    
    provider = Column(String, nullable=False) # gmail, outlook, imap
    email_address = Column(String, nullable=False)
    
    # Store access tokens or credentials securely (mocked for this version)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="email_accounts")
    emails = relationship("EmailMessage", back_populates="account")

class EmailMessage(BaseModel):
    """
    Persistence for synced email headers before/after extraction.
    """
    __tablename__ = "email_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    account_id = Column(String, ForeignKey("email_accounts.id"), nullable=False)
    external_message_id = Column(String, nullable=True, index=True)
    
    subject = Column(String, nullable=True)
    sender = Column(String, nullable=True)
    snippet = Column(Text, nullable=True)
    category = Column(String, default="Non-Financial") # Accounts Payable, Receipt, etc.
    date = Column(DateTime, default=datetime.utcnow)
    
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("EmailAccount", back_populates="emails")

class Transaction(BaseModel):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)
    
    description = Column(String, nullable=True) # e.g. "PAG. EDP COMERCIAL SA"
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    reference_id = Column(String, nullable=True)
    
    is_reconciled = Column(Boolean, default=False)
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
