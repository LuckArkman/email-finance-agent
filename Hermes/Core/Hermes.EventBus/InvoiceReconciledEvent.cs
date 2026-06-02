using System;

namespace Hermes.EventBus.Events;

public record InvoiceReconciledEvent(
    Guid InvoiceDocumentId,
    Guid ReceiptId,
    Guid TenantId,
    DateTime ReconciledAt,
    decimal ReconciledAmount
) : IntegrationEvent;
