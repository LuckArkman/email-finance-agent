using Hermes.EventBus.Events;

namespace Hermes.EventBus.Events;

public record SystemStartedEvent : IntegrationEvent
{
    public string Message { get; init; } = "Hermes System Started";
}
