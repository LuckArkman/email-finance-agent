using System.Threading.Tasks;
using Hermes.EventBus.Events;
using MassTransit;

namespace Hermes.EventBus.RabbitMQ;

public class RabbitMqEventBus : IEventBus
{
    private readonly IPublishEndpoint _publishEndpoint;

    public RabbitMqEventBus(IPublishEndpoint publishEndpoint)
    {
        _publishEndpoint = publishEndpoint;
    }

    public async Task PublishAsync<T>(T @event) where T : IntegrationEvent
    {
        await _publishEndpoint.Publish(@event);
    }
}
