using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Hermes.Domain.Financial;
using Hermes.Infrastructure.Data;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Controllers;

/// <summary>
/// Exposes invoice data to the frontend. Handles CRUD, status transitions,
/// calendar grouping for the Agenda view, and payment receipt matching.
/// </summary>
[ApiController]
[Route("api/hermes/invoices")]
public class InvoicesController : ControllerBase
{
    private readonly HermesDbContext _db;
    private readonly ILogger<InvoicesController> _logger;

    public InvoicesController(HermesDbContext db, ILogger<InvoicesController> logger)
    {
        _db = db;
        _logger = logger;
    }

    // GET /api/hermes/invoices
    // Query params: status (string), statusFilter (string), limit (int), offset (int), source (string)
    [HttpGet]
    public async Task<IActionResult> GetInvoices(
        [FromQuery] string? status = null,
        [FromQuery] string? statusFilter = null,
        [FromQuery] string? source = null,
        [FromQuery] int limit = 50,
        [FromQuery] int offset = 0)
    {
        // Auto-update overdue status before returning
        await UpdateOverdueStatusesAsync();

        var query = _db.Invoices.Include(i => i.Vendor).AsQueryable();

        // Accept both ?status= and ?statusFilter= for compatibility
        var statusStr = status ?? statusFilter;
        if (!string.IsNullOrWhiteSpace(statusStr))
        {
            if (Enum.TryParse<InvoiceStatus>(statusStr, ignoreCase: true, out var parsedStatus))
                query = query.Where(i => i.Status == parsedStatus);
        }

        if (!string.IsNullOrWhiteSpace(source))
            query = query.Where(i => i.SourceType == source);

        var total = await query.CountAsync();
        var invoices = await query
            .OrderByDescending(i => i.CreatedAt)
            .Skip(offset)
            .Take(limit)
            .ToListAsync();

        return Ok(new
        {
            total,
            data = invoices.Select(MapToDto)
        });
    }

    // GET /api/hermes/invoices/calendar?year=2026&month=6
    // Returns invoices grouped by due_date for the Agenda view
    [HttpGet("calendar")]
    public async Task<IActionResult> GetCalendar([FromQuery] int year, [FromQuery] int month)
    {
        if (year == 0) year = DateTime.UtcNow.Year;
        if (month == 0) month = DateTime.UtcNow.Month;

        await UpdateOverdueStatusesAsync();

        var startDate = new DateTime(year, month, 1, 0, 0, 0, DateTimeKind.Utc);
        var endDate = startDate.AddMonths(1);

        var invoices = await _db.Invoices
            .Where(i => i.DueDate >= startDate && i.DueDate < endDate)
            .OrderBy(i => i.DueDate)
            .ToListAsync();

        // Group by date string YYYY-MM-DD
        var grouped = invoices
            .GroupBy(i => i.DueDate!.Value.ToString("yyyy-MM-dd"))
            .ToDictionary(
                g => g.Key,
                g => g.Select(MapToDto).ToList()
            );

        return Ok(grouped);
    }

    // GET /api/hermes/invoices/summary?year=2026&month=6
    // Monthly KPI summary for Agenda sidebar
    [HttpGet("summary")]
    public async Task<IActionResult> GetSummary([FromQuery] int year, [FromQuery] int month)
    {
        if (year == 0) year = DateTime.UtcNow.Year;
        if (month == 0) month = DateTime.UtcNow.Month;

        await UpdateOverdueStatusesAsync();

        var startDate = new DateTime(year, month, 1, 0, 0, 0, DateTimeKind.Utc);
        var endDate = startDate.AddMonths(1);

        var monthInvoices = await _db.Invoices
            .Where(i => i.DueDate >= startDate && i.DueDate < endDate)
            .ToListAsync();

        var allPending = await _db.Invoices
            .Where(i => i.Status == InvoiceStatus.Pending)
            .ToListAsync();

        var upcomingMonths = await _db.Invoices
            .Where(i => i.DueDate >= endDate && i.DueDate < endDate.AddMonths(3)
                     && i.Status == InvoiceStatus.Pending)
            .OrderBy(i => i.DueDate)
            .Take(10)
            .ToListAsync();

        return Ok(new
        {
            totalPending = allPending.Sum(i => i.TotalAmount),
            totalReconciliation = monthInvoices
                .Where(i => i.Status == InvoiceStatus.Reconciliation)
                .Sum(i => i.TotalAmount),
            totalMonth = monthInvoices.Sum(i => i.TotalAmount),
            totalPaid = monthInvoices
                .Where(i => i.Status == InvoiceStatus.Paid)
                .Sum(i => i.TotalAmount),
            totalOverdue = monthInvoices
                .Where(i => i.Status == InvoiceStatus.Overdue)
                .Sum(i => i.TotalAmount),
            countPending = monthInvoices.Count(i => i.Status == InvoiceStatus.Pending),
            countPaid = monthInvoices.Count(i => i.Status == InvoiceStatus.Paid),
            countOverdue = monthInvoices.Count(i => i.Status == InvoiceStatus.Overdue),
            countReconciliation = monthInvoices.Count(i => i.Status == InvoiceStatus.Reconciliation),
            upcomingPayments = upcomingMonths.Select(MapToDto)
        });
    }

    // GET /api/hermes/invoices/kpis
    // Global KPIs for Dashboard
    [HttpGet("kpis")]
    public async Task<IActionResult> GetKpis()
    {
        await UpdateOverdueStatusesAsync();

        var all = await _db.Invoices.ToListAsync();

        return Ok(new
        {
            totalPending = all.Where(i => i.Status == InvoiceStatus.Pending).Sum(i => i.TotalAmount),
            totalPaid = all.Where(i => i.Status == InvoiceStatus.Paid).Sum(i => i.TotalAmount),
            totalOverdue = all.Where(i => i.Status == InvoiceStatus.Overdue).Sum(i => i.TotalAmount),
            totalReconciliation = all.Where(i => i.Status == InvoiceStatus.Reconciliation).Sum(i => i.TotalAmount),
            countPending = all.Count(i => i.Status == InvoiceStatus.Pending),
            countPaid = all.Count(i => i.Status == InvoiceStatus.Paid),
            countOverdue = all.Count(i => i.Status == InvoiceStatus.Overdue),
            countReconciliation = all.Count(i => i.Status == InvoiceStatus.Reconciliation),
            countTotal = all.Count
        });
    }

    // GET /api/hermes/invoices/{id}
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        var invoice = await _db.Invoices.Include(i => i.Items).Include(i => i.Vendor)
            .FirstOrDefaultAsync(i => i.Id == id);
        if (invoice == null) return NotFound();
        return Ok(MapToDto(invoice));
    }

    // POST /api/hermes/invoices/{id}/mark-paid
    [HttpPost("{id:guid}/mark-paid")]
    public async Task<IActionResult> MarkPaid(Guid id, [FromBody] MarkPaidRequest? req)
    {
        var invoice = await _db.Invoices.FindAsync(id);
        if (invoice == null) return NotFound();

        invoice.Status = InvoiceStatus.Paid;
        invoice.PaidAt = DateTime.UtcNow;
        if (!string.IsNullOrEmpty(req?.PaymentEvidenceUrl))
            invoice.PaymentEvidenceUrl = req.PaymentEvidenceUrl;
        invoice.UpdatedAt = DateTime.UtcNow;

        await _db.SaveChangesAsync();
        _logger.LogInformation("Invoice {Id} marked as Paid", id);
        return Ok(new { message = "Invoice marked as paid.", status = "paid" });
    }

    // POST /api/hermes/invoices/{id}/reconcile
    [HttpPost("{id:guid}/reconcile")]
    public async Task<IActionResult> MoveToReconciliation(Guid id)
    {
        var invoice = await _db.Invoices.FindAsync(id);
        if (invoice == null) return NotFound();

        invoice.Status = InvoiceStatus.Reconciliation;
        invoice.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();
        return Ok(new { message = "Invoice moved to reconciliation.", status = "reconciliation" });
    }

    // POST /api/hermes/invoices/{id}/match-receipt
    // Matches a payment receipt to this invoice and marks as paid
    [HttpPost("{id:guid}/match-receipt")]
    public async Task<IActionResult> MatchReceipt(Guid id, [FromBody] MatchReceiptRequest req)
    {
        var invoice = await _db.Invoices.FindAsync(id);
        if (invoice == null) return NotFound();

        invoice.Status = InvoiceStatus.Paid;
        invoice.PaidAt = req.PaymentDate ?? DateTime.UtcNow;
        invoice.PaymentEvidenceUrl = req.EvidenceUrl;
        invoice.PaymentReference = req.PaymentReference ?? invoice.PaymentReference;
        invoice.UpdatedAt = DateTime.UtcNow;
        await _db.SaveChangesAsync();

        _logger.LogInformation("Receipt matched to invoice {Id}. Reference: {Ref}", id, req.PaymentReference);
        return Ok(new { message = "Receipt matched. Invoice status updated to paid.", invoiceId = id });
    }

    // ─────────────────────────────────────────────────────────────
    // Private helpers
    // ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Auto-updates Pending invoices past their DueDate to Overdue status.
    /// Called on every read to keep data consistent without a background job.
    /// </summary>
    private async Task UpdateOverdueStatusesAsync()
    {
        var now = DateTime.UtcNow;
        var overdueInvoices = await _db.Invoices
            .Where(i => i.Status == InvoiceStatus.Pending
                     && i.DueDate.HasValue
                     && i.DueDate.Value < now)
            .ToListAsync();

        if (overdueInvoices.Any())
        {
            foreach (var inv in overdueInvoices)
            {
                inv.Status = InvoiceStatus.Overdue;
                inv.UpdatedAt = now;
            }
            await _db.SaveChangesAsync();
            _logger.LogInformation("Auto-updated {Count} invoices to Overdue status", overdueInvoices.Count);
        }
    }

    private static object MapToDto(Invoice i) => new
    {
        id             = i.Id,
        invoice_number = i.InvoiceNumber,
        vendor_name    = i.VendorName ?? i.Vendor?.Name ?? "Desconhecido",
        vendor_tax_id  = i.VendorTaxId,
        issue_date     = i.IssueDate.ToString("yyyy-MM-dd"),
        due_date       = i.DueDate?.ToString("yyyy-MM-dd"),
        net_amount     = i.NetAmount,
        iva_rate       = i.IvaRate,
        iva_amount     = i.IvaAmount,
        total_amount   = i.TotalAmount,
        currency       = i.Currency,
        status         = i.Status.ToString().ToLower() switch
        {
            "pending"        => "pending",
            "paid"           => "paid",
            "overdue"        => "overdue",
            "reconciliation" => "reconciliation",
            "reviewrequired" => "review_required",
            "cancelled"      => "cancelled",
            _                => "draft"
        },
        confidence_score   = i.ConfidenceScore,
        category           = i.Category ?? "accounts_payable",
        source             = i.SourceType ?? "upload",
        filename           = i.Filename,
        raw_document_url   = i.RawDocumentUrl,
        payment_reference  = i.PaymentReference,
        payment_evidence_url = i.PaymentEvidenceUrl,
        paid_at            = i.PaidAt?.ToString("yyyy-MM-dd"),
        source_email       = i.SourceEmail,
        is_vectorized      = i.IsVectorized,
        created_at         = i.CreatedAt,
        updated_at         = i.UpdatedAt
    };
}

public record MarkPaidRequest(string? PaymentEvidenceUrl);
public record MatchReceiptRequest(
    string? PaymentReference,
    string? EvidenceUrl,
    DateTime? PaymentDate,
    decimal? PaidAmount
);
