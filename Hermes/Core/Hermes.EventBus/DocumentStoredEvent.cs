using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record DocumentStoredEvent(
    string MessageId,
    Guid DocumentId,
    Guid TenantId,
    string OriginalFileName,
    string S3Key,
    long SizeInBytes,
    string MimeType,
    string StorageProvider
) : IntegrationEvent;
