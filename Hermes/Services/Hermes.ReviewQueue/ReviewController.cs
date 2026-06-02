using System;
using System.Linq;
using System.Threading.Tasks;
using Hermes.EventBus;
using MassTransit;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Hermes.ReviewQueue;

[ApiController]
[Route("api/hermes/[controller]")]
public class ReviewController : ControllerBase
{
    private readonly ReviewDbContext _dbContext;
    private readonly AuditLogService _auditLogService;
    private readonly IPublishEndpoint _publishEndpoint;

    public ReviewController(ReviewDbContext dbContext, AuditLogService auditLogService, IPublishEndpoint publishEndpoint)
    {
        _dbContext = dbContext;
        _auditLogService = auditLogService;
        _publishEndpoint = publishEndpoint;
    }

    [HttpGet]
    public async Task<IActionResult> GetPendingReviews()
    {
        var pending = await _dbContext.PendingReviews
            .Where(p => !p.IsResolved)
            .OrderBy(p => p.CreatedAt)
            .ToListAsync();

        return Ok(pending);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> ResolveReview(Guid id, [FromBody] InvoiceManuallyReviewedEvent payload)
    {
        var pending = await _dbContext.PendingReviews.FirstOrDefaultAsync(p => p.Id == id);

        if (pending == null) return NotFound("Review not found.");
        if (pending.IsResolved) return BadRequest("Review is already resolved.");

        // Atualizar estado
        pending.IsResolved = true;
        pending.ResolvedAt = DateTime.UtcNow;
        pending.ResolvedBy = payload.ReviewedBy ?? "SystemUser";

        // Auditoria
        await _auditLogService.LogActionAsync(
            pending.Id, 
            "Manual Override", 
            $"User {pending.ResolvedBy} confirmed Total Amount: {payload.TotalAmount}", 
            pending.ResolvedBy
        );

        await _dbContext.SaveChangesAsync();

        // Emitir Evento para o RAG Vector indexing e integração ERP consumirem
        await _publishEndpoint.Publish(payload);

        return Ok(new { message = "Review resolved successfully", documentId = payload.DocumentId });
    }
}
