import contextvars
from typing import Optional, Any
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# Global async-safe context variable for Multi-Tenant Data Isolation
_tenant_id_ctx_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("tenant_id", default=None)

class TenantSecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that resets and isolates the multi-tenancy context for every incoming request.
    Crucial to avoid cross-tenant data leaks in async architectures.
    """
    async def dispatch(self, request: Request, call_next):
        # Reset current context
        token = _tenant_id_ctx_var.set(None)
        try:
            response = await call_next(request)
            return response
        finally:
            _tenant_id_ctx_var.reset(token)

def set_current_tenant(tenant_id: str) -> None:
    """
    Called after successful Authentication to lock the user's process 
    to their company's Tenant ID.
    """
    _tenant_id_ctx_var.set(tenant_id)

def get_current_tenant() -> str:
    """
    Safely retrieves the tenant ID from the current async thread context.
    """
    tenant_id = _tenant_id_ctx_var.get()
    if not tenant_id:
        raise ValueError("Access Denied: Tenant Context is empty. User might not be authenticated properly.")
    return tenant_id

def filter_by_tenant(model_class: Any, query: Any) -> Any:
    """
    Applies Application-Level RLS (Row Level Security).
    Automatically wraps SQLAlchemy queries ensuring users cannot fetch foreign rows.
    """
    tenant_id = get_current_tenant()
    if not hasattr(model_class, 'tenant_id'):
        raise AttributeError(f"Model {model_class.__name__} does not support multi-tenancy (Missing tenant_id column).")
        
    return query.where(model_class.tenant_id == tenant_id)
