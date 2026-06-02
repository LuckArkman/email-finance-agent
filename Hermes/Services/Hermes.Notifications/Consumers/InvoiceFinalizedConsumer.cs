using System.Threading.Tasks;
using Hermes.EventBus.Events;
using Hermes.Notifications.Services;
using MassTransit;

namespace Hermes.Notifications.Consumers;

public class InvoiceFinalizedConsumer : IConsumer<InvoiceReconciledEvent>
{
    private readonly WebhookOutboundDispatcher _webhookDispatcher;

    public InvoiceFinalizedConsumer(WebhookOutboundDispatcher webhookDispatcher)
    {
        _webhookDispatcher = webhookDispatcher;
    }

    public async Task Consume(ConsumeContext<InvoiceReconciledEvent> context)
    {
        var evt = context.Message;
        
        // Simular o envio do Payload para o parceiro ERP B2B
        var payload = new 
        {
            InvoiceId = evt.InvoiceDocumentId,
            TenantId = evt.TenantId,
            ExtractedData = new { Amount = evt.ReconciledAmount },
            Status = "FINALIZED"
        };

        // Dispara o Webhook. O Polly gere retries se o SAP estiver offline.
        await _webhookDispatcher.DispatchInvoiceAsync(evt.InvoiceDocumentId, evt.TenantId.ToString(), payload);
    }
}
