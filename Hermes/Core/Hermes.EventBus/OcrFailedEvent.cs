using System;

namespace Hermes.EventBus;

public record OcrFailedEvent(
    Guid DocumentId,
    Guid TenantId,
    string ErrorMessage,
    DateTime FailedAt
);
