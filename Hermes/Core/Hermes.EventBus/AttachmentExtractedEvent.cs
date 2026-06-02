using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record AttachmentExtractedEvent(
    string MessageId,
    string FileName,
    string MimeType,
    long SizeInBytes,
    string StoragePath
) : IntegrationEvent;
