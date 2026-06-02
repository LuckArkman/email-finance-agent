using System.Threading.Tasks;
using Hermes.EventBus.Events;
using MassTransit;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging;

namespace Hermes.Notifications.Consumers;

public class InvoiceReconciledConsumer : IConsumer<InvoiceReconciledEvent>
{
    private readonly IHubContext<NotificationHub> _hubContext;
    private readonly ILogger<InvoiceReconciledConsumer> _logger;

    public InvoiceReconciledConsumer(IHubContext<NotificationHub> hubContext, ILogger<InvoiceReconciledConsumer> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<InvoiceReconciledEvent> context)
    {
        var message = context.Message;
        _logger.LogInformation($"Broadcasting InvoiceReconciledEvent to Tenant {message.TenantId}");

        // Broadcasts specifically to the Tenant Group
        await _hubContext.Clients.Group(message.TenantId.ToString())
            .SendAsync("InvoiceReconciled", message);
    }
}
