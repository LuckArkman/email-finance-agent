using System.Threading.Tasks;
using Hermes.EventBus;
using MassTransit;
using Microsoft.Extensions.Logging;

namespace Hermes.Reconciliation;

public class InvoiceReadyConsumer : 
    IConsumer<ExtractionCompletedEvent>, 
    IConsumer<InvoiceManuallyReviewedEvent>
{
    private readonly ReconciliationDbContext _dbContext;
    private readonly ILogger<InvoiceReadyConsumer> _logger;

    public InvoiceReadyConsumer(ReconciliationDbContext dbContext, ILogger<InvoiceReadyConsumer> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<ExtractionCompletedEvent> context)
    {
        var evt = context.Message;
        
        // Se a fatura requer revisão, não a conciliamos ainda. 
        // Esperamos pelo InvoiceManuallyReviewedEvent.
        if (evt.RequiresReview) return;

        await AddInvoiceAsync(
            evt.DocumentId, 
            evt.TenantId, 
            evt.VendorName, 
            evt.Nif, 
            evt.TotalAmount, 
            evt.InvoiceDate);
    }

    public async Task Consume(ConsumeContext<InvoiceManuallyReviewedEvent> context)
    {
        var evt = context.Message;
        
        await AddInvoiceAsync(
            evt.DocumentId, 
            evt.TenantId, 
            evt.VendorName, 
            evt.Nif, 
            evt.TotalAmount, 
            evt.InvoiceDate);
    }

    private async Task AddInvoiceAsync(
        System.Guid docId, 
        System.Guid tenantId, 
        string vendorName, 
        string nif, 
        decimal totalAmount, 
        System.DateTime? invoiceDate)
    {
        _logger.LogInformation($"Adding ReconcilableInvoice for Document {docId}");

        var invoice = new ReconcilableInvoice
        {
            DocumentId = docId,
            TenantId = tenantId,
            VendorName = vendorName,
            Nif = nif,
            TotalAmount = totalAmount,
            InvoiceDate = invoiceDate,
            IsReconciled = false
        };

        _dbContext.Invoices.Add(invoice);
        await _dbContext.SaveChangesAsync();
    }
}
