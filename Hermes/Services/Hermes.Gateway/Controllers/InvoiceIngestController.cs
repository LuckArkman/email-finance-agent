using System;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Hermes.Domain.Financial;
using Hermes.EventBus.Events;
using Hermes.Gateway.Models;
using Hermes.Infrastructure.Data;
using MassTransit;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Controllers;

/// <summary>
/// Receives invoices extracted by the Hermes Agent and:
/// 1. Validates the agent API key
/// 2. Persists the invoice in PostgreSQL with auto-classification
/// 3. Publishes the event to MassTransit for async processing
/// 4. Triggers vectorization for RAG search
/// </summary>
[ApiController]
[Route("api/hermes/invoices")]
public class InvoiceIngestController : ControllerBase
{
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly HermesDbContext _db;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<InvoiceIngestController> _logger;

    public InvoiceIngestController(
        IPublishEndpoint publishEndpoint,
        HermesDbContext db,
        IHttpClientFactory httpClientFactory,
        ILogger<InvoiceIngestController> logger)
    {
        _publishEndpoint = publishEndpoint;
        _db = db;
        _httpClientFactory = httpClientFactory;
        _logger = logger;
    }

    /// <summary>
    /// POST /api/hermes/invoices/ingest
    /// Called by the Hermes Agent after successful invoice extraction.
    /// Persists to DB, classifies status, and triggers vectorization.
    /// </summary>
    [HttpPost("ingest")]
    public async Task<IActionResult> Ingest(
        [FromBody] InvoiceIngestPayload payload,
        [FromHeader(Name = "X-Api-Key")] string? apiKey)
    {
        // 1. Validate agent API key
        var expectedKey = Environment.GetEnvironmentVariable("HERMES_AGENT_API_KEY");
        if (string.IsNullOrWhiteSpace(apiKey) || apiKey != expectedKey)
        {
            _logger.LogWarning("[InvoiceIngest] Invalid API key. Source: {Source}", payload?.SourceEmail);
            return Unauthorized(new { error = "Invalid or missing X-Api-Key header." });
        }

        // 2. Validate required fields
        if (string.IsNullOrWhiteSpace(payload?.InvoiceNumber))
            return BadRequest(new { error = "InvoiceNumber is required." });

        var trackingId = Guid.NewGuid();

        // 3. Classify status based on DueDate
        var now = DateTime.UtcNow;
        var status = InvoiceStatus.Pending;
        if (payload.DueDate.HasValue && payload.DueDate.Value < DateOnly.FromDateTime(now))
            status = InvoiceStatus.Overdue;

        // Low confidence score triggers ReviewRequired
        var confidence = payload.ConfidenceScore ?? 1.0;
        if (confidence < 0.70 && status == InvoiceStatus.Pending)
            status = InvoiceStatus.ReviewRequired;

        // 4. Find or create Vendor
        var vendorName = payload.SupplierName ?? "Fornecedor Desconhecido";
        var vendor = await _db.Vendors.FirstOrDefaultAsync(v => v.Name == vendorName)
                  ?? new Vendor { Name = vendorName, TaxId = payload.SupplierTaxId ?? string.Empty, Address = string.Empty, ContactEmail = string.Empty };

        if (vendor.Id == Guid.Empty)
        {
            _db.Vendors.Add(vendor);
            await _db.SaveChangesAsync(); // Get vendor ID
        }

        // 5. Calculate financial fields
        var totalAmount = payload.TotalAmount;
        var ivaRate    = payload.TaxRate ?? 0.23m;
        var netAmount  = totalAmount / (1 + ivaRate);
        var ivaAmount  = totalAmount - netAmount;

        // 6. Persist invoice
        var invoice = new Invoice
        {
            Id             = trackingId,
            InvoiceNumber  = payload.InvoiceNumber,
            IssueDate      = payload.InvoiceDate?.ToDateTime(TimeOnly.MinValue) ?? now,
            DueDate        = payload.DueDate?.ToDateTime(TimeOnly.MinValue),
            TotalAmount    = totalAmount,
            NetAmount      = netAmount,
            IvaRate        = ivaRate,
            IvaAmount      = ivaAmount,
            Currency       = payload.Currency ?? "EUR",
            Status         = status,
            ConfidenceScore = confidence,
            VendorId       = vendor.Id,
            VendorName     = vendorName,
            VendorTaxId    = payload.SupplierTaxId,
            PaymentReference = payload.PaymentReference,
            SourceEmail    = payload.SourceEmail,
            SourceType     = payload.SourceType ?? "email",
            Filename       = payload.Filename,
            Category       = "accounts_payable",
            IsVectorized   = false,
            CreatedAt      = now
        };

        _db.Invoices.Add(invoice);
        await _db.SaveChangesAsync();

        _logger.LogInformation(
            "[InvoiceIngest] Invoice persisted. Number: {Number} | Status: {Status} | TrackingId: {Id}",
            payload.InvoiceNumber, status, trackingId);

        // 7. Publish to MassTransit for async downstream processing
        await _publishEndpoint.Publish(new InvoiceReceivedFromAgentEvent(
            EventId: trackingId,
            InvoiceNumber: payload.InvoiceNumber,
            SupplierName: vendorName,
            SupplierTaxId: payload.SupplierTaxId,
            TotalAmount: totalAmount,
            Currency: invoice.Currency,
            InvoiceDate: DateOnly.FromDateTime(invoice.IssueDate),
            DueDate: payload.DueDate,
            LineItems: (payload.LineItems ?? Enumerable.Empty<InvoiceLineItem>())
                .Select(li => new AgentLineItem(li.Description, li.Quantity, li.UnitPrice, li.Total))
                .ToList(),
            ValidationStatus: payload.ValidationStatus,
            ValidationNotes: payload.ValidationNotes,
            SourceEmail: payload.SourceEmail,
            ReceivedAt: now
        ));

        // 8. Trigger vectorization (fire-and-forget — non-blocking)
        _ = VectorizeInvoiceAsync(invoice, payload);

        return Accepted(new
        {
            status     = "accepted",
            trackingId = trackingId.ToString(),
            invoiceNumber = payload.InvoiceNumber,
            invoiceStatus = status.ToString().ToLower(),
            message    = "Invoice received, persisted and queued for vectorization."
        });
    }

    /// <summary>POST /api/hermes/agent/audit - Telemetry endpoint.</summary>
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

    // ─────────────────────────────────────────────────────────────
    // Vectorization (fire-and-forget)
    // ─────────────────────────────────────────────────────────────
    private async Task VectorizeInvoiceAsync(Invoice invoice, InvoiceIngestPayload payload)
    {
        try
        {
            // Build text representation for embedding
            var textToEmbed = new StringBuilder();
            textToEmbed.AppendLine($"Fatura: {invoice.InvoiceNumber}");
            textToEmbed.AppendLine($"Fornecedor: {invoice.VendorName}");
            textToEmbed.AppendLine($"Total: {invoice.TotalAmount} {invoice.Currency}");
            textToEmbed.AppendLine($"Data de emissao: {invoice.IssueDate:yyyy-MM-dd}");
            if (invoice.DueDate.HasValue)
                textToEmbed.AppendLine($"Vencimento: {invoice.DueDate.Value:yyyy-MM-dd}");
            textToEmbed.AppendLine($"Status: {invoice.Status}");
            if (!string.IsNullOrEmpty(payload.SourceEmail))
                textToEmbed.AppendLine($"Email origem: {payload.SourceEmail}");

            foreach (var li in payload.LineItems ?? Enumerable.Empty<InvoiceLineItem>())
                textToEmbed.AppendLine($"- {li.Description}: {li.Quantity}x {li.UnitPrice} = {li.Total}");

            // POST to the vector service
            var vectorServiceUrl = Environment.GetEnvironmentVariable("VECTOR_SERVICE_URL") ?? "http://hermes-vector:8001";
            var client = _httpClientFactory.CreateClient();
            client.Timeout = TimeSpan.FromSeconds(15);

            var vectorPayload = new
            {
                id       = invoice.Id.ToString(),
                text     = textToEmbed.ToString(),
                metadata = new
                {
                    invoice_id    = invoice.Id,
                    invoice_number = invoice.InvoiceNumber,
                    vendor_name   = invoice.VendorName,
                    total_amount  = invoice.TotalAmount,
                    due_date      = invoice.DueDate?.ToString("yyyy-MM-dd"),
                    status        = invoice.Status.ToString().ToLower(),
                    source_type   = invoice.SourceType,
                    source_email  = invoice.SourceEmail
                }
            };

            var response = await client.PostAsJsonAsync($"{vectorServiceUrl}/api/vectors/store", vectorPayload);

            if (response.IsSuccessStatusCode)
            {
                // Update IsVectorized flag
                invoice.IsVectorized = true;
                invoice.VectorId = invoice.Id.ToString();
                _db.Invoices.Update(invoice);
                await _db.SaveChangesAsync();
                _logger.LogInformation("[Vectorization] Invoice {Id} vectorized successfully", invoice.Id);
            }
            else
            {
                _logger.LogWarning("[Vectorization] Vector service returned {Status} for invoice {Id}", response.StatusCode, invoice.Id);
            }
        }
        catch (Exception ex)
        {
            // Non-fatal — invoice is already persisted
            _logger.LogWarning(ex, "[Vectorization] Failed to vectorize invoice {Id}. Will retry on next processing.", invoice.Id);
        }
    }
}
