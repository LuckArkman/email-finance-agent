using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record TenantCreatedEvent : IntegrationEvent
{
    public Guid TenantId { get; init; }
    public string TenantName { get; init; } = string.Empty;

    public TenantCreatedEvent(Guid tenantId, string tenantName)
    {
        TenantId = tenantId;
        TenantName = tenantName;
    }
}
