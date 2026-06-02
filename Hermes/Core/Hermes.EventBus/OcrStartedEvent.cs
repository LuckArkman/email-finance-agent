using System;

namespace Hermes.EventBus;

public record OcrStartedEvent(
    Guid DocumentId,
    Guid TenantId,
    DateTime StartedAt
);
