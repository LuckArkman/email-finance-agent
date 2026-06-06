using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Hermes.Gateway.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Controllers;

/// <summary>
/// Proxy Controller — expõe as capacidades do Hermes Agent ao frontend React.
/// O React nunca fala diretamente com o agente; todas as chamadas passam por este controller.
///
/// Base URL: /api/hermes/agent
/// </summary>
[ApiController]
[Route("api/hermes/agent")]
public class AgentProxyController : ControllerBase
{
    private readonly HermesAgentClient _agentClient;
    private readonly ILogger<AgentProxyController> _logger;

    public AgentProxyController(HermesAgentClient agentClient, ILogger<AgentProxyController> logger)
    {
        _agentClient = agentClient;
        _logger = logger;
    }

    // ---------------------------------------------------------------
    // GET /api/hermes/agent/status
    // Retorna o estado atual do Hermes Agent (versão, modelo, sessões)
    // ---------------------------------------------------------------
    [HttpGet("status")]
    public async Task<IActionResult> GetStatus()
    {
        var status = await _agentClient.GetStatusAsync();
        if (status is null)
        {
            return Ok(new
            {
                online = false,
                version = "N/A",
                model = "N/A",
                activeSessions = 0,
                message = "Hermes Agent offline ou inacessível."
            });
        }

        return Ok(new
        {
            online = status.GatewayRunning,
            version = status.Version,
            model = status.Model,
            provider = status.Provider,
            activeSessions = status.ActiveSessions
        });
    }

    // ---------------------------------------------------------------
    // GET /api/hermes/agent/sessions
    // Lista sessões recentes do agente (útil para histórico no frontend)
    // ---------------------------------------------------------------
    [HttpGet("sessions")]
    public async Task<IActionResult> GetSessions()
    {
        var sessions = await _agentClient.GetSessionsAsync();
        return Ok(new { sessions = sessions ?? new List<AgentSession>() });
    }

    // ---------------------------------------------------------------
    // POST /api/hermes/agent/chat
    // Chat com o Hermes Agent — o frontend envia mensagens e recebe resposta
    // Body: { messages: [{ role, content }] }
    // ---------------------------------------------------------------
    [HttpPost("chat")]
    public async Task<IActionResult> Chat([FromBody] ChatRequest request)
    {
        if (request.Messages == null || request.Messages.Count == 0)
            return BadRequest(new { error = "Messages array is required." });

        // Injetar o System Prompt para garantir que o Agente tem Persona e sabe usar o RAG
        var systemPrompt = @"You are Hermes Agent, a highly capable autonomous financial AI for enterprise environments. 
Your core directive is to assist with invoice reconciliation, data extraction, and general financial inquiries.
CRITICAL: When asked to check pending invoices, find an invoice, or look for specific billing information, ALWAYS use the 'search_knowledge_base' tool first to consult the Vector Database.
You also have access to 'get_pending_invoices', 'get_supplier_history', and 'ingest_invoice'.
Respond strictly in European Portuguese (Português de Portugal).";

        if (request.Messages[0].Role != "system")
        {
            request.Messages.Insert(0, new ChatMessage("system", systemPrompt));
        }

        _logger.LogInformation("[AgentProxy] Chat request — {Count} mensagens", request.Messages.Count);

        var reply = await _agentClient.ChatAsync(request.Messages);

        if (reply is null)
            return StatusCode(503, new { error = "Hermes Agent não respondeu. Tente novamente." });

        return Ok(new { reply });
    }

    // ---------------------------------------------------------------
    // POST /api/hermes/agent/process-document
    // Aciona o Hermes Agent para processar um documento manualmente
    // (ex: PDF enviado via upload no frontend)
    // Body: { documentPath, sourceEmail }
    // ---------------------------------------------------------------
    [HttpPost("process-document")]
    public async Task<IActionResult> ProcessDocument([FromBody] ProcessDocumentRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.SourceEmail))
            return BadRequest(new { error = "sourceEmail é obrigatório." });

        _logger.LogInformation("[AgentProxy] Processar documento: {Path} de {Email}",
            request.DocumentPath, request.SourceEmail);

        var result = await _agentClient.TriggerDocumentProcessingAsync(
            request.DocumentPath ?? "uploaded-document",
            request.SourceEmail);

        return Ok(new
        {
            status = "triggered",
            agentResponse = result,
            message = "Hermes Agent notificado para processar o documento."
        });
    }
}

// DTOs de entrada
public record ChatRequest(List<ChatMessage> Messages);
public record ProcessDocumentRequest(string? DocumentPath, string SourceEmail);
