using System;
using System.Collections.Generic;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record InvoiceItemData(
    string Description,
    int Quantity,
    decimal Price
);

public record ExtractionCompletedEvent(
    Guid DocumentId,
    Guid TenantId,
    string VendorName,
    string Nif,
    DateTime? InvoiceDate,
    decimal TotalAmount,
    List<InvoiceItemData> Items,
    DateTime CompletedAt,
    bool RequiresReview
) : IntegrationEvent;
