using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record EmailReceivedEvent(
    string MessageId,
    string FromAddress,
    string Subject,
    DateTimeOffset Date,
    bool HasAttachments,
    string StoragePath
) : IntegrationEvent;
