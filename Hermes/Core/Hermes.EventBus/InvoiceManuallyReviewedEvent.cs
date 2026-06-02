using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record InvoiceManuallyReviewedEvent(
    Guid DocumentId,
    Guid TenantId,
    string VendorName,
    string Nif,
    DateTime? InvoiceDate,
    decimal TotalAmount,
    System.Collections.Generic.List<Hermes.EventBus.InvoiceItemData> Items,
    string ReviewedBy,
    DateTime ReviewedAt
) : IntegrationEvent;
