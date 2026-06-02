using System;

namespace Hermes.EventBus.Events;

public record ReceiptReceivedEvent(
    Guid ReceiptId,
    Guid TenantId,
    string Iban,
    string Nif,
    DateTime PaymentDate,
    decimal Amount
) : IntegrationEvent;
