using System;

namespace Hermes.EventBus.Events;

public record VectorIndexedEvent(
    Guid DocumentId,
    Guid TenantId,
    Guid InvoiceEntityId,
    int VectorDimensions,
    DateTime IndexedAt
) : IntegrationEvent;
