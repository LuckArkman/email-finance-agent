using System;
using System.Linq;
using System.Threading.Tasks;
using Hermes.EventBus.Events;
using Hermes.Gateway.Models;
using MassTransit;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Controllers;

/// <summary>
/// Endpoint dedicado a receber faturas extraídas pelo Hermes Agent (Nous Research).
/// Valida a chave de API do agente e publica o evento no barramento MassTransit
/// para processamento assíncrono pelo pipeline .NET 9.
/// </summary>
[ApiController]
[Route("api/hermes/invoices")]
public class InvoiceIngestController : ControllerBase
{
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly ILogger<InvoiceIngestController> _logger;

    public InvoiceIngestController(
        IPublishEndpoint publishEndpoint,
        ILogger<InvoiceIngestController> logger)
    {
        _publishEndpoint = publishEndpoint;
        _logger = logger;
    }

    /// <summary>
    /// POST /api/hermes/invoices/ingest
    /// Chamado pelo Hermes Agent após extração bem-sucedida de uma fatura.
    /// </summary>
    [HttpPost("ingest")]
    public async Task<IActionResult> Ingest(
        [FromBody] InvoiceIngestPayload payload,
        [FromHeader(Name = "X-Api-Key")] string? apiKey)
    {
        // 1. Validar chave do Hermes Agent
        var expectedKey = Environment.GetEnvironmentVariable("HERMES_AGENT_API_KEY");
        if (string.IsNullOrWhiteSpace(apiKey) || apiKey != expectedKey)
        {
            _logger.LogWarning("[InvoiceIngest] Tentativa de acesso com chave inválida. Source: {Source}", payload?.SourceEmail);
            return Unauthorized(new { error = "Invalid or missing X-Api-Key header." });
        }

        // 2. Validar campos obrigatórios mínimos
        if (string.IsNullOrWhiteSpace(payload?.InvoiceNumber))
        {
            _logger.LogWarning("[InvoiceIngest] Payload sem InvoiceNumber recebido de {Source}", payload?.SourceEmail);
            return BadRequest(new { error = "InvoiceNumber is required." });
        }

        var trackingId = Guid.NewGuid();

        _logger.LogInformation(
            "[InvoiceIngest] Fatura recebida do Hermes Agent. " +
            "Invoice: {InvoiceNumber} | Supplier: {Supplier} | Total: {Total} {Currency} | " +
            "ValidationStatus: {Status} | TrackingId: {TrackingId}",
            payload.InvoiceNumber,
            payload.SupplierName,
            payload.TotalAmount,
            payload.Currency,
            payload.ValidationStatus,
            trackingId);

        // 3. Publicar no MassTransit para processamento assíncrono
        await _publishEndpoint.Publish(new InvoiceReceivedFromAgentEvent(
            EventId: trackingId,
            InvoiceNumber: payload.InvoiceNumber,
            SupplierName: payload.SupplierName,
            SupplierTaxId: payload.SupplierTaxId,
            TotalAmount: payload.TotalAmount,
            Currency: payload.Currency,
            InvoiceDate: payload.InvoiceDate,
            DueDate: payload.DueDate,
            LineItems: payload.LineItems
                .Select(li => new AgentLineItem(li.Description, li.Quantity, li.UnitPrice, li.Total))
                .ToList(),
            ValidationStatus: payload.ValidationStatus,
            ValidationNotes: payload.ValidationNotes,
            SourceEmail: payload.SourceEmail,
            ReceivedAt: DateTime.UtcNow
        ));

        return Accepted(new
        {
            status = "accepted",
            trackingId = trackingId.ToString(),
            invoiceNumber = payload.InvoiceNumber,
            message = "Invoice received and queued for reconciliation."
        });
    }

    /// <summary>
    /// POST /api/hermes/agent/audit
    /// Endpoint de auditoria — recebe telemetria do Hook post-extraction.
    /// </summary>
    [HttpPost("/api/hermes/agent/audit")]
    public IActionResult Audit(
        [FromBody] object auditPayload,
        [FromHeader(Name = "X-Api-Key")] string? apiKey)
    {
        var expectedKey = Environment.GetEnvironmentVariable("HERMES_AGENT_API_KEY");
        if (string.IsNullOrWhiteSpace(apiKey) || apiKey != expectedKey)
            return Unauthorized();

        _logger.LogDebug("[AgentAudit] {Payload}", auditPayload?.ToString());
        return Ok();
    }
}
