using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record OcrCompletedEvent(
    Guid DocumentId,
    Guid TenantId,
    string RawText,
    float MeanConfidence,
    DateTime CompletedAt
) : IntegrationEvent;
