using System.Threading.Tasks;
using Hermes.EventBus.Events;
using MassTransit;
using Microsoft.Extensions.Logging;

namespace Hermes.Reconciliation;

public class ReceiptReadyConsumer : IConsumer<ReceiptReceivedEvent>
{
    private readonly ReconciliationDbContext _dbContext;
    private readonly ReconciliationEngine _engine;
    private readonly ILogger<ReceiptReadyConsumer> _logger;

    public ReceiptReadyConsumer(
        ReconciliationDbContext dbContext, 
        ReconciliationEngine engine, 
        ILogger<ReceiptReadyConsumer> logger)
    {
        _dbContext = dbContext;
        _engine = engine;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<ReceiptReceivedEvent> context)
    {
        var evt = context.Message;
        
        _logger.LogInformation($"Received ReceiptReceivedEvent for Receipt {evt.ReceiptId}");

        var receipt = new ReconcilableReceipt
        {
            ReceiptId = evt.ReceiptId,
            TenantId = evt.TenantId,
            Iban = evt.Iban,
            Nif = evt.Nif,
            Amount = evt.Amount,
            PaymentDate = evt.PaymentDate,
            IsReconciled = false
        };

        _dbContext.Receipts.Add(receipt);
        await _dbContext.SaveChangesAsync();

        // Acionar o motor imediatamente para tentar casar com faturas pendentes
        await _engine.ProcessReceiptAsync(receipt);
    }
}
