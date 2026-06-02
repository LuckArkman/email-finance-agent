using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record InvoiceCreatedEvent(Guid InvoiceId, string InvoiceNumber, Guid VendorId, decimal TotalAmount, string Currency) : IntegrationEvent;
