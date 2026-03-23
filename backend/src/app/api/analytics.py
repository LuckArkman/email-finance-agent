import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract

import redis.asyncio as redis
from app.database import get_db
from app.models import InvoiceRecord, User, ReviewQueueModel
from app.security import SecurityDependencies
from app.tenant import get_current_tenant, filter_by_tenant
from app.config import BaseAPIConfig

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

# Configs - Use the service name defined in docker-compose
redis_pool = redis.ConnectionPool.from_url("redis://redis:6379/0", decode_responses=True)
redis_client = redis.Redis(connection_pool=redis_pool)


class AnalyticsService:
    """
    Engine para relatórios pesados e gráficos. Usa grupamento via banco 
    e Cache Inteligente via REDIS para alcançar 0ms.
    """
    
    @staticmethod
    async def get_cashflow_summary(db: AsyncSession, tenant_id: str, year: int) -> List[Dict[str, Any]]:
        """
        Views em PostgreSQL + Queries de grupamento (GROUP BY Month).
        """
        cache_key = f"analytics:cashflow:{tenant_id}:{year}"
        
        # 1. Tenta recuperar do REDIS primeiro (Velocidade Pura - 0ms)
        try:
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                 return json.loads(cached_data)
        except redis.RedisError as e:
            print(f"Redis Cache skip: {e}")
            
        # 2. Cache Miss: Vai no BD, Processa agrupamentos pesados no PostgreSQL
        query = select(
            extract('month', InvoiceRecord.issue_date).label('month'),
            func.sum(InvoiceRecord.total_amount).label('total_spent')
        ).where(
            InvoiceRecord.tenant_id == tenant_id,
            extract('year', InvoiceRecord.issue_date) == year
        ).group_by(
            extract('month', InvoiceRecord.issue_date)
        ).order_by(
            extract('month', InvoiceRecord.issue_date)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        # Converte o resultado
        chart_data = [{"month": int(r.month), "total_spent": float(r.total_spent)} for r in rows if r.month]
        
        # Preenche meses vazios pra gerar um gráfico amigável de 12 meses
        formatted_data = []
        for m in range(1, 13):
            month_val = next((item["total_spent"] for item in chart_data if item["month"] == m), 0.0)
            formatted_data.append({"month": m, "total_spent": month_val})
            
        # 3. Armazena no Redis para os próximos hits (Expira em 1 hora)
        try:
            await redis_client.setex(cache_key, 3600, json.dumps(formatted_data))
        except redis.RedisError:
            pass # Ignora se REDIS estiver indisponível no Docker
            
        return formatted_data

    @staticmethod
    async def get_spend_by_vendor_chart(db: AsyncSession, tenant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Gera um Top N Fornecedores listado por quem mais exigiu dinheiro (Soma das faturas).
        """
        query = select(
            InvoiceRecord.vendor_name,
            func.sum(InvoiceRecord.total_amount).label('total_spent')
        ).where(
            InvoiceRecord.tenant_id == tenant_id,
            InvoiceRecord.vendor_name != None
        ).group_by(
            InvoiceRecord.vendor_name
        ).order_by(
            desc(func.sum(InvoiceRecord.total_amount))
        ).limit(limit)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [{"vendor": r.vendor_name, "total_spent": float(r.total_spent)} for r in rows]

from sqlalchemy import desc

@router.get("/cashflow")
async def get_analytics_cashflow(
    year: int = datetime.utcnow().year,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Endpoint de sumarização de faturas mes-a-mes. 
    Usado ativamente por painéis de fluxo de caixa em Vue/React.
    """
    tenant_id = get_current_tenant()
    data = await AnalyticsService.get_cashflow_summary(db, tenant_id, year)
    
    return {
        "year": year,
        "cashflow_series": data
    }
    
@router.get("/vendors/top")
async def get_analytics_vendors(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Gráfico "Where is my money going?" - Top fornecedores pelo qual o usuário tem maiores despesas.
    """
    tenant_id = get_current_tenant()
    data = await AnalyticsService.get_spend_by_vendor_chart(db, tenant_id, limit)
    
    return {
        "top_vendors": data
    }

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(SecurityDependencies.get_current_user)
):
    """
    Returns high-level KPIS for the dashboard metric cards.
    """
    tenant_id = get_current_tenant()
    
    # 1. Total spent
    total_query = select(func.sum(InvoiceRecord.total_amount)).where(InvoiceRecord.tenant_id == tenant_id)
    total_result = await db.execute(total_query)
    total_spent = total_result.scalar() or 0.0
    
    # 2. Count processed
    count_query = select(func.count(InvoiceRecord.id)).where(InvoiceRecord.tenant_id == tenant_id)
    count_result = await db.execute(count_query)
    count_invoices = count_result.scalar() or 0
    
    # 3. Avg confidence index
    avg_score_query = select(func.avg(InvoiceRecord.confidence_score)).where(InvoiceRecord.tenant_id == tenant_id)
    avg_score_result = await db.execute(avg_score_query)
    avg_score = (avg_score_result.scalar() or 0.0) * 100
    
    # 4. Count pending human review
    pending_query = select(func.count(ReviewQueueModel.id)).where(ReviewQueueModel.tenant_id == tenant_id, ReviewQueueModel.status == "pending_review")
    pending_result = await db.execute(pending_query)
    pending_count = pending_result.scalar() or 0
    
    return {
        "total_spent": total_spent,
        "processed_count": count_invoices,
        "pending_review": pending_count,
        "avg_confidence": round(avg_score, 1)
    }
