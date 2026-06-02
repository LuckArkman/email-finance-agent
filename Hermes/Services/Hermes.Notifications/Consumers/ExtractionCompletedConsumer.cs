using System.Threading.Tasks;
using Hermes.EventBus;
using MassTransit;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging;

namespace Hermes.Notifications.Consumers;

public class ExtractionCompletedConsumer : IConsumer<ExtractionCompletedEvent>
{
    private readonly IHubContext<NotificationHub> _hubContext;
    private readonly ILogger<ExtractionCompletedConsumer> _logger;

    public ExtractionCompletedConsumer(IHubContext<NotificationHub> hubContext, ILogger<ExtractionCompletedConsumer> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<ExtractionCompletedEvent> context)
    {
        var message = context.Message;
        _logger.LogInformation($"Broadcasting ExtractionCompletedEvent to Tenant {message.TenantId}");

        // Broadcasts specifically to the Tenant Group
        await _hubContext.Clients.Group(message.TenantId.ToString())
            .SendAsync("ExtractionCompleted", message);
    }
}
