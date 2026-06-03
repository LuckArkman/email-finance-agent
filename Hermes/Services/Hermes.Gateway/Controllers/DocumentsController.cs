using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Hermes.Domain.Financial;
using Hermes.Infrastructure.Data;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Hermes.Gateway.Controllers;

/// <summary>
/// Digital document repository. Exposes all stored documents (PDFs, images)
/// for the Arquivo Digital view. Also handles manual uploads.
/// </summary>
[ApiController]
[Route("api/hermes/documents")]
public class DocumentsController : ControllerBase
{
    private readonly HermesDbContext _db;
    private readonly ILogger<DocumentsController> _logger;

    public DocumentsController(HermesDbContext db, ILogger<DocumentsController> logger)
    {
        _db = db;
        _logger = logger;
    }

    // GET /api/hermes/documents
    // Lists all documents in the digital repository
    [HttpGet]
    public async Task<IActionResult> GetDocuments(
        [FromQuery] string? source = null,
        [FromQuery] int limit = 50,
        [FromQuery] int offset = 0)
    {
        // We use Invoices that have a Filename as the document source of truth
        var query = _db.Invoices.AsQueryable();

        // Only show invoices that have an actual document
        query = query.Where(i => i.Filename != null && i.Filename != string.Empty);

        if (!string.IsNullOrWhiteSpace(source))
            query = query.Where(i => i.SourceType == source);

        var total = await query.CountAsync();
        var docs = await query
            .OrderByDescending(i => i.CreatedAt)
            .Skip(offset)
            .Take(limit)
            .ToListAsync();

        return Ok(new
        {
            total,
            data = docs.Select(d => new
            {
                id              = d.Id,
                filename        = d.Filename,
                source          = d.SourceType ?? "upload",
                source_email    = d.SourceEmail,
                mime_type       = InferMimeType(d.Filename ?? ""),
                raw_document_url = d.RawDocumentUrl,
                invoice_id      = d.Id,
                vendor_name     = d.VendorName ?? "Desconhecido",
                total_amount    = d.TotalAmount,
                status          = d.Status.ToString().ToLower(),
                created_at      = d.CreatedAt
            })
        });
    }

    // GET /api/hermes/documents/queue
    // Documents pending OCR processing (Draft or ReviewRequired status)
    [HttpGet("queue")]
    public async Task<IActionResult> GetQueue()
    {
        var pendingDocs = await _db.Invoices
            .Where(i => i.Status == InvoiceStatus.Draft || i.Status == InvoiceStatus.ReviewRequired)
            .OrderByDescending(i => i.CreatedAt)
            .Take(20)
            .ToListAsync();

        return Ok(pendingDocs.Select(d => new
        {
            id          = d.Id,
            filename    = d.Filename ?? d.VendorName ?? "Documento sem nome",
            vendor_name = d.VendorName,
            status      = d.Status == InvoiceStatus.Draft ? "pending" : "review_required",
            source      = d.SourceType ?? "upload",
            created_at  = d.CreatedAt
        }));
    }

    // POST /api/hermes/documents/upload
    // Manual file upload - creates a Draft invoice record
    [HttpPost("upload")]
    [RequestSizeLimit(50_000_000)] // 50 MB
    public async Task<IActionResult> Upload([FromForm] IFormFile file)
    {
        if (file == null || file.Length == 0)
            return BadRequest(new { detail = "No file provided." });

        var allowedTypes = new[] { "application/pdf", "image/jpeg", "image/png", "image/tiff", "image/webp" };
        if (!allowedTypes.Contains(file.ContentType.ToLower()))
            return BadRequest(new { detail = $"File type '{file.ContentType}' not supported. Use PDF, JPG, PNG, TIFF or WEBP." });

        // For now, store metadata only (no actual S3/MinIO storage configured)
        // The filename serves as the document identifier
        var invoiceRecord = new Invoice
        {
            InvoiceNumber  = $"UPLOAD-{DateTime.UtcNow:yyyyMMddHHmmss}",
            IssueDate      = DateTime.UtcNow,
            Status         = InvoiceStatus.Draft,
            Filename       = file.FileName,
            SourceType     = "upload",
            Currency       = "EUR",
            ConfidenceScore = 0,
            CreatedAt      = DateTime.UtcNow
        };

        _db.Invoices.Add(invoiceRecord);
        await _db.SaveChangesAsync();

        _logger.LogInformation("Document uploaded: {Filename} ({Size} bytes)", file.FileName, file.Length);

        return Ok(new
        {
            message    = "Document uploaded successfully. Queued for OCR processing.",
            id         = invoiceRecord.Id,
            filename   = file.FileName,
            status     = "pending"
        });
    }

    // GET /api/hermes/documents/{id}
    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id)
    {
        var doc = await _db.Invoices.FindAsync(id);
        if (doc == null) return NotFound();

        return Ok(new
        {
            id              = doc.Id,
            filename        = doc.Filename,
            source          = doc.SourceType,
            source_email    = doc.SourceEmail,
            raw_document_url = doc.RawDocumentUrl,
            vendor_name     = doc.VendorName,
            total_amount    = doc.TotalAmount,
            status          = doc.Status.ToString().ToLower(),
            created_at      = doc.CreatedAt
        });
    }

    private static string InferMimeType(string filename) =>
        Path.GetExtension(filename).ToLower() switch
        {
            ".pdf"  => "application/pdf",
            ".jpg" or ".jpeg" => "image/jpeg",
            ".png"  => "image/png",
            ".tiff" => "image/tiff",
            _       => "application/octet-stream"
        };
}
