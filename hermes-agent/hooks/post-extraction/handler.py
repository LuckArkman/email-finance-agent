"""
post-extraction/handler.py
Hook de auditoria e telemetria — dispara em eventos do ciclo de vida
do Hermes Agent e envia metadados para o Hermes .NET Gateway.
"""
import os
import json
import logging
from datetime import datetime, timezone

try:
    import httpx
    _httpx_available = True
except ImportError:
    _httpx_available = False

logger = logging.getLogger("hermes.hook.post-extraction")

# Eventos relevantes para o pipeline de faturas
_FINANCE_TOOLS = {"vision_analyze", "web_extract", "read_file", "execute_code"}


async def handle(event_type: str, context: dict, **kwargs):
    """
    Handler principal do hook. Recebe todos os eventos declarados no HOOK.yaml
    e filtra os relevantes para auditoria financeira.
    """
    gateway_url = os.environ.get("HERMES_DOTNET_GATEWAY_URL", "").rstrip("/")
    api_key = os.environ.get("HERMES_DOTNET_API_KEY", "")

    if not gateway_url or not api_key:
        logger.warning("[post-extraction] HERMES_DOTNET_GATEWAY_URL ou HERMES_DOTNET_API_KEY não configurados.")
        return

    # ----------------------------------------------------------------
    # Evento: gateway:startup — Verificar conectividade com o .NET
    # ----------------------------------------------------------------
    if event_type == "gateway:startup":
        await _ping_dotnet(gateway_url, api_key)
        return

    # ----------------------------------------------------------------
    # Evento: on_session_end — Registar resumo da sessão
    # ----------------------------------------------------------------
    if event_type == "on_session_end":
        session_id = context.get("session_id", "unknown")
        platform = context.get("platform", "email")
        await _send_audit(gateway_url, api_key, {
            "event": "session_ended",
            "session_id": session_id,
            "platform": platform,
            "timestamp": _now()
        })
        return

    # ----------------------------------------------------------------
    # Evento: post_tool_call — Auditar ferramentas de extração
    # ----------------------------------------------------------------
    if event_type == "post_tool_call":
        tool_name = context.get("tool_name", "")
        if tool_name not in _FINANCE_TOOLS:
            return  # Ignorar ferramentas não financeiras

        audit_payload = {
            "event": "extraction_tool_called",
            "tool": tool_name,
            "session_id": context.get("session_id", "unknown"),
            "duration_ms": context.get("duration_ms"),
            "success": context.get("success", True),
            "error": context.get("error"),
            "timestamp": _now()
        }
        await _send_audit(gateway_url, api_key, audit_payload)


async def _ping_dotnet(gateway_url: str, api_key: str):
    """Verifica se o Hermes.Gateway .NET está acessível ao arrancar."""
    if not _httpx_available:
        logger.warning("[post-extraction] httpx não instalado — skip ping.")
        return
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{gateway_url}/health/live",
                headers={"X-Api-Key": api_key}
            )
            if resp.status_code == 200:
                logger.info("[post-extraction] ✅ Hermes.Gateway .NET acessível em %s", gateway_url)
            else:
                logger.warning("[post-extraction] ⚠️ Gateway respondeu HTTP %d", resp.status_code)
    except Exception as exc:
        logger.error("[post-extraction] ❌ Não foi possível contactar o Gateway: %s", exc)


async def _send_audit(gateway_url: str, api_key: str, payload: dict):
    """Envia payload de auditoria para o endpoint .NET."""
    if not _httpx_available:
        logger.debug("[post-extraction] httpx ausente — audit payload: %s", json.dumps(payload))
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{gateway_url}/api/hermes/agent/audit",
                json=payload,
                headers={
                    "X-Api-Key": api_key,
                    "Content-Type": "application/json"
                }
            )
    except Exception as exc:
        logger.warning("[post-extraction] Falha ao enviar auditoria: %s", exc)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
