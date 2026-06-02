using System;
using System.Collections.Generic;

namespace Hermes.Gateway.Models;

/// <summary>
/// Payload recebido do Hermes Agent (Nous Research) após extração de fatura.
/// Mapeado diretamente a partir do JSON produzido pela Skill invoice-extraction.
/// </summary>
public record InvoiceIngestPayload(
    string? SupplierName,
    string? SupplierTaxId,
    string? SupplierAddress,
    string InvoiceNumber,
    DateOnly? InvoiceDate,
    DateOnly? DueDate,
    string? PurchaseOrderRef,
    List<InvoiceLineItem> LineItems,
    decimal Subtotal,
    decimal TaxRate,
    decimal TaxAmount,
    decimal TotalAmount,
    string Currency,
    string? PaymentMethod,
    string? BankIban,
    string? Notes,
    string SourceEmail,
    DateTime ExtractionTimestamp,
    string ValidationStatus,
    string? ValidationNotes
);

public record InvoiceLineItem(
    string Description,
    decimal Quantity,
    decimal UnitPrice,
    decimal Total
);
