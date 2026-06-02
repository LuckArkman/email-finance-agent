using System;
using System.Collections.Generic;

namespace Hermes.EventBus.Events;

/// <summary>
/// Evento publicado no MassTransit quando o Hermes Agent entrega
/// uma fatura extraída para processamento pelo pipeline .NET.
/// </summary>
public record InvoiceReceivedFromAgentEvent(
    Guid EventId,
    string InvoiceNumber,
    string? SupplierName,
    string? SupplierTaxId,
    decimal TotalAmount,
    string Currency,
    DateOnly? InvoiceDate,
    DateOnly? DueDate,
    List<AgentLineItem> LineItems,
    string ValidationStatus,
    string? ValidationNotes,
    string SourceEmail,
    DateTime ReceivedAt
) : IntegrationEvent;

public record AgentLineItem(
    string Description,
    decimal Quantity,
    decimal UnitPrice,
    decimal Total
);
