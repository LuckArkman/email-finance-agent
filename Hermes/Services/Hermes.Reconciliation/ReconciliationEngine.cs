using System;
using System.Linq;
using System.Threading.Tasks;
using Hermes.EventBus.Events;
using MassTransit;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Hermes.Reconciliation;

public class ReconciliationEngine
{
    private readonly ReconciliationDbContext _dbContext;
    private readonly ToleranceMatcher _matcher;
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly ILogger<ReconciliationEngine> _logger;

    public ReconciliationEngine(
        ReconciliationDbContext dbContext,
        ToleranceMatcher matcher,
        IPublishEndpoint publishEndpoint,
        ILogger<ReconciliationEngine> logger)
    {
        _dbContext = dbContext;
        _matcher = matcher;
        _publishEndpoint = publishEndpoint;
        _logger = logger;
    }

    public async Task ProcessReceiptAsync(ReconcilableReceipt receipt)
    {
        _logger.LogInformation($"Starting reconciliation for Receipt {receipt.ReceiptId} (Amount: {receipt.Amount})");

        var pendingInvoices = await _dbContext.Invoices
            .Where(i => i.TenantId == receipt.TenantId && !i.IsReconciled && i.Nif == receipt.Nif)
            .ToListAsync();

        foreach (var invoice in pendingInvoices)
        {
            if (_matcher.IsMatch(invoice, receipt))
            {
                _logger.LogInformation($"Match Found! Invoice {invoice.DocumentId} matches Receipt {receipt.ReceiptId}");

                // Atualizar estado
                invoice.IsReconciled = true;
                invoice.ReconciledWithReceiptId = receipt.ReceiptId;

                receipt.IsReconciled = true;
                receipt.ReconciledWithInvoiceId = invoice.DocumentId;

                await _dbContext.SaveChangesAsync();

                // Publicar evento
                var evt = new InvoiceReconciledEvent(
                    invoice.DocumentId,
                    receipt.ReceiptId,
                    invoice.TenantId,
                    DateTime.UtcNow,
                    invoice.TotalAmount
                );

                await _publishEndpoint.Publish(evt);
                return; // Match encontrado, não procura mais para este recibo.
            }
        }

        _logger.LogWarning($"No matching invoice found for Receipt {receipt.ReceiptId}. Kept pending.");
    }
}
