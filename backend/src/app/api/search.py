"""
Semantic Search API
====================
Provides natural-language search over indexed financial documents using
ChromaDB vector similarity (cosine distance on nomic-embed-text embeddings).

Endpoints:
    GET  /api/v1/search          — Semantic search across tenant's documents
    GET  /api/v1/search/health   — ChromaDB connectivity check
    POST /api/v1/search/reindex  — Re-vectorize all existing InvoiceRecords (admin)
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import InvoiceRecord, User
from app.security import SecurityDependencies
from app.tenant import get_current_tenant
from app.services.vector_store import VectorStoreService

router = APIRouter(prefix="/api/v1/search", tags=["Semantic Search"])


@router.get("")
async def semantic_search(
    q: str = Query(..., description="Natural language search query"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum results"),
    status: str | None = Query(default=None, description="Filter by invoice status"),
    document_type: str | None = Query(default=None, description="Filter by document type"),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """
    Performs semantic similarity search over indexed financial documents.

    Supports natural language queries like:
    - "faturas de telecomunicações em atraso"
    - "comprovativo de pagamento EDP"
    - "faturas com vencimento em junho"

    Results are ranked by semantic similarity score (1.0 = perfect match).
    """
    tenant_id = get_current_tenant()

    # Build optional ChromaDB metadata filter
    filters: dict | None = None
    if status or document_type:
        conditions = {}
        if status:
            conditions["status"] = status
        if document_type:
            conditions["document_type"] = document_type
        # ChromaDB requires $and for multiple conditions
        if len(conditions) > 1:
            filters = {"$and": [{k: {"$eq": v}} for k, v in conditions.items()]}
        else:
            k, v = next(iter(conditions.items()))
            filters = {k: {"$eq": v}}

    results = await VectorStoreService.search(
        query=q,
        tenant_id=tenant_id,
        n_results=limit,
        filters=filters,
    )

    return {
        "query": q,
        "tenant_id": tenant_id,
        "total_results": len(results),
        "results": results,
    }


@router.get("/health")
async def vector_store_health(
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """
    Checks ChromaDB connectivity and returns collection statistics
    for the authenticated tenant.
    """
    health = VectorStoreService.health_check()
    if health.get("status") != "ok":
        raise HTTPException(
            status_code=503,
            detail=f"ChromaDB unavailable: {health.get('error', 'unknown error')}",
        )
    return health


@router.post("/reindex")
async def reindex_all_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user),
):
    """
    Re-vectorizes ALL existing InvoiceRecords for this tenant into ChromaDB.

    Use this to backfill the vector index with historical data that was
    created before vector indexing was enabled.

    This operation may take several minutes for large datasets.
    """
    tenant_id = get_current_tenant()

    stmt = select(InvoiceRecord).where(InvoiceRecord.tenant_id == tenant_id)
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    if not invoices:
        return {"message": "No invoices found for this tenant.", "indexed": 0, "failed": 0}

    summary = await VectorStoreService.reindex_all(list(invoices), tenant_id)
    return {
        "message": f"Reindexing complete for tenant {tenant_id}.",
        **summary,
    }
