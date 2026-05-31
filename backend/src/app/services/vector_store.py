"""
VectorStoreService — ChromaDB Integration
==========================================
Provides semantic indexing and search for financial documents extracted
from emails (both body-text LLM extraction and OCR attachment extraction).

Architecture:
- Vector DB: ChromaDB (HTTP client → Docker service efa_chromadb)
- Embeddings: Ollama nomic-embed-text (768-dim) via HTTP API
- Isolation: one ChromaDB collection per tenant
- Fallback: if Ollama/ChromaDB unavailable, log warning and continue gracefully

Usage:
    # In Celery tasks (sync context):
    VectorStoreService.index_invoice_sync(invoice, raw_text, tenant_id)

    # In async context (FastAPI / email_tasks):
    await VectorStoreService.index_invoice(invoice, raw_text, tenant_id)

    # Semantic search:
    results = await VectorStoreService.search(query, tenant_id, n_results=10)
"""

import json
import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ─── ChromaDB collection name ─────────────────────────────────────────────────

def _collection_name(tenant_id: str) -> str:
    """Produces a ChromaDB-safe collection name scoped to the tenant."""
    return f"efa_{tenant_id.replace('-', '_')[:36]}"


# ─── Embedding generation ─────────────────────────────────────────────────────

def _build_document_text(invoice: Any, raw_text: str) -> str:
    """
    Builds the rich textual representation that will be embedded.
    Combines structured metadata with the original raw content so that
    semantic queries can match on either dimension.
    """
    due_str = ""
    if invoice.due_date:
        try:
            due_str = invoice.due_date.strftime("%Y-%m-%d")
        except Exception:
            due_str = str(invoice.due_date)

    lines = [
        f"Fornecedor: {invoice.vendor_name or 'Desconhecido'}",
        f"Tipo de documento: {invoice.document_type or 'accounts_payable'}",
        f"Estado: {invoice.status or 'pending'}",
        f"Valor líquido: €{invoice.net_amount or 0:.2f}",
        f"IVA ({(invoice.iva_rate or 0.23) * 100:.0f}%): €{invoice.iva_amount or 0:.2f}",
        f"Valor total: €{invoice.total_amount or 0:.2f}",
        f"Moeda: {invoice.currency or 'EUR'}",
        f"Vencimento: {due_str or 'não definido'}",
        f"Referência: {invoice.payment_reference or invoice.invoice_number or 'N/A'}",
        f"Origem: {invoice.source or 'email'}",
    ]
    if raw_text and raw_text.strip():
        # Truncate to 2000 chars to keep embedding efficient
        lines.append(f"\nConteúdo extraído:\n{raw_text.strip()[:2000]}")

    return "\n".join(lines)


async def _get_embedding_async(text: str, ollama_url: str) -> list[float] | None:
    """Calls Ollama's /api/embeddings endpoint asynchronously."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ollama_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
            )
            response.raise_for_status()
            return response.json().get("embedding")
    except Exception as e:
        logger.warning(f"[VectorStore] Embedding generation failed (Ollama): {e}")
        return None


def _get_embedding_sync(text: str, ollama_url: str) -> list[float] | None:
    """Calls Ollama's /api/embeddings endpoint synchronously (for Celery tasks)."""
    try:
        response = httpx.post(
            f"{ollama_url}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json().get("embedding")
    except Exception as e:
        logger.warning(f"[VectorStore] Embedding generation failed (Ollama sync): {e}")
        return None


# ─── ChromaDB helpers ─────────────────────────────────────────────────────────

def _get_chroma_client(chromadb_url: str):
    """Returns a ChromaDB HTTP client. Imported lazily to avoid startup errors."""
    try:
        import chromadb
        # Parse host and port from URL (e.g. http://chromadb:8000)
        url = chromadb_url.rstrip("/")
        if "://" in url:
            url = url.split("://", 1)[1]
        host, _, port_str = url.partition(":")
        port = int(port_str) if port_str else 8000
        return chromadb.HttpClient(host=host, port=port)
    except Exception as e:
        logger.warning(f"[VectorStore] ChromaDB client init failed: {e}")
        return None


def _get_or_create_collection(client, tenant_id: str):
    """Gets or creates a per-tenant ChromaDB collection with cosine similarity."""
    try:
        return client.get_or_create_collection(
            name=_collection_name(tenant_id),
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as e:
        logger.warning(f"[VectorStore] Could not get/create collection for {tenant_id}: {e}")
        return None


def _build_metadata(invoice: Any) -> dict:
    """Extracts filterable metadata fields from an InvoiceRecord."""
    due_str = ""
    if invoice.due_date:
        try:
            due_str = invoice.due_date.strftime("%Y-%m-%d")
        except Exception:
            due_str = str(invoice.due_date)

    return {
        "invoice_id": str(invoice.id),
        "tenant_id": str(invoice.tenant_id),
        "vendor_name": str(invoice.vendor_name or ""),
        "document_type": str(invoice.document_type or "accounts_payable"),
        "status": str(invoice.status or "pending"),
        "total_amount": float(invoice.total_amount or 0.0),
        "net_amount": float(invoice.net_amount or 0.0),
        "iva_amount": float(invoice.iva_amount or 0.0),
        "currency": str(invoice.currency or "EUR"),
        "due_date": due_str,
        "source": str(invoice.source or "email"),
        "has_attachment": invoice.raw_document_url is not None,
        "indexed_at": datetime.utcnow().isoformat(),
    }


# ─── Public Service Interface ─────────────────────────────────────────────────

class VectorStoreService:
    """
    Singleton-style service for ChromaDB vector operations.
    All methods are safe to call — they never raise exceptions that would break
    the calling pipeline. Failures are logged as warnings and skipped.
    """

    @staticmethod
    def _get_urls() -> tuple[str, str]:
        from app.config import BaseAPIConfig
        settings = BaseAPIConfig.get_settings()
        return settings.chromadb_url, settings.ollama_base_url

    # ── Async index (for email_tasks.py) ──────────────────────────────────────

    @staticmethod
    async def index_invoice(invoice: Any, raw_text: str, tenant_id: str) -> bool:
        """
        Async: Generates embedding and upserts the invoice document into ChromaDB.
        Returns True on success, False on any failure.
        """
        chromadb_url, ollama_url = VectorStoreService._get_urls()
        doc_text = _build_document_text(invoice, raw_text)

        embedding = await _get_embedding_async(doc_text, ollama_url)
        if embedding is None:
            return False

        client = _get_chroma_client(chromadb_url)
        if client is None:
            return False

        collection = _get_or_create_collection(client, tenant_id)
        if collection is None:
            return False

        try:
            metadata = _build_metadata(invoice)
            collection.upsert(
                ids=[str(invoice.id)],
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[metadata],
            )
            logger.info(f"[VectorStore] Indexed invoice {invoice.id} for tenant {tenant_id}")
            return True
        except Exception as e:
            logger.warning(f"[VectorStore] Upsert failed for invoice {invoice.id}: {e}")
            return False

    # ── Sync index (for Celery ocr_tasks.py) ──────────────────────────────────

    @staticmethod
    def index_invoice_sync(invoice: Any, raw_text: str, tenant_id: str) -> bool:
        """
        Sync: Same as index_invoice but for synchronous Celery task contexts.
        """
        chromadb_url, ollama_url = VectorStoreService._get_urls()
        doc_text = _build_document_text(invoice, raw_text)

        embedding = _get_embedding_sync(doc_text, ollama_url)
        if embedding is None:
            return False

        client = _get_chroma_client(chromadb_url)
        if client is None:
            return False

        collection = _get_or_create_collection(client, tenant_id)
        if collection is None:
            return False

        try:
            metadata = _build_metadata(invoice)
            collection.upsert(
                ids=[str(invoice.id)],
                embeddings=[embedding],
                documents=[doc_text],
                metadatas=[metadata],
            )
            logger.info(f"[VectorStore] Indexed invoice {invoice.id} for tenant {tenant_id} (sync)")
            return True
        except Exception as e:
            logger.warning(f"[VectorStore] Sync upsert failed for invoice {invoice.id}: {e}")
            return False

    # ── Semantic search ───────────────────────────────────────────────────────

    @staticmethod
    async def search(
        query: str,
        tenant_id: str,
        n_results: int = 10,
        filters: dict | None = None,
    ) -> list[dict]:
        """
        Performs semantic similarity search on the tenant's ChromaDB collection.

        Args:
            query: Natural language search query (e.g. "faturas de eletricidade")
            tenant_id: Tenant scope
            n_results: Maximum number of results to return
            filters: Optional ChromaDB metadata filter dict (e.g. {"status": "pending"})

        Returns:
            List of result dicts with: invoice_id, score, metadata, snippet
        """
        chromadb_url, ollama_url = VectorStoreService._get_urls()

        embedding = await _get_embedding_async(query, ollama_url)
        if embedding is None:
            return []

        client = _get_chroma_client(chromadb_url)
        if client is None:
            return []

        collection = _get_or_create_collection(client, tenant_id)
        if collection is None:
            return []

        try:
            query_kwargs: dict = {
                "query_embeddings": [embedding],
                "n_results": min(n_results, max(collection.count(), 1)),
                "include": ["documents", "metadatas", "distances"],
            }
            if filters:
                query_kwargs["where"] = filters

            results = collection.query(**query_kwargs)

            output = []
            ids = results.get("ids", [[]])[0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            for doc_id, doc_text, meta, dist in zip(ids, docs, metas, dists):
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity score [0, 1]
                similarity = round(1 - (dist / 2), 4)
                output.append({
                    "invoice_id": meta.get("invoice_id", doc_id),
                    "score": similarity,
                    "vendor_name": meta.get("vendor_name", ""),
                    "document_type": meta.get("document_type", ""),
                    "status": meta.get("status", ""),
                    "total_amount": meta.get("total_amount", 0.0),
                    "due_date": meta.get("due_date", ""),
                    "source": meta.get("source", ""),
                    "snippet": doc_text[:300] if doc_text else "",
                    "metadata": meta,
                })

            # Sort by similarity descending
            output.sort(key=lambda x: x["score"], reverse=True)
            return output

        except Exception as e:
            logger.warning(f"[VectorStore] Search failed for tenant {tenant_id}: {e}")
            return []

    # ── Delete ────────────────────────────────────────────────────────────────

    @staticmethod
    def delete_invoice_sync(invoice_id: str, tenant_id: str) -> bool:
        """Removes a document from the vector index (sync)."""
        chromadb_url, _ = VectorStoreService._get_urls()
        client = _get_chroma_client(chromadb_url)
        if client is None:
            return False
        collection = _get_or_create_collection(client, tenant_id)
        if collection is None:
            return False
        try:
            collection.delete(ids=[invoice_id])
            return True
        except Exception as e:
            logger.warning(f"[VectorStore] Delete failed for {invoice_id}: {e}")
            return False

    # ── Reindex batch ─────────────────────────────────────────────────────────

    @staticmethod
    async def reindex_all(invoices: list, tenant_id: str) -> dict:
        """
        Reindexes a list of InvoiceRecord objects for the given tenant.
        Returns a summary dict: {"indexed": N, "failed": N}
        """
        indexed = 0
        failed = 0
        for invoice in invoices:
            # Use whatever text we can — no raw OCR available for historical records
            raw_text = f"{invoice.vendor_name or ''} {invoice.invoice_number or ''} {invoice.payment_reference or ''}"
            success = await VectorStoreService.index_invoice(invoice, raw_text, tenant_id)
            if success:
                indexed += 1
            else:
                failed += 1
        return {"indexed": indexed, "failed": failed, "total": len(invoices)}

    # ── Health check ──────────────────────────────────────────────────────────

    @staticmethod
    def health_check() -> dict:
        """Returns ChromaDB connection status and collection counts."""
        chromadb_url, ollama_url = VectorStoreService._get_urls()
        result: dict = {"chromadb_url": chromadb_url, "ollama_url": ollama_url, "status": "error"}
        try:
            client = _get_chroma_client(chromadb_url)
            if client:
                collections = client.list_collections()
                result["status"] = "ok"
                result["collections"] = [c.name for c in collections]
                result["collection_count"] = len(collections)
        except Exception as e:
            result["error"] = str(e)
        return result
