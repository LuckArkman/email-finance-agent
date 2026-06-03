using System;
using System.Collections.Generic;
using Hermes.Domain.Common;

namespace Hermes.Domain.Financial;

public class Invoice : BaseEntity
{
    public string   InvoiceNumber      { get; set; } = string.Empty;
    public DateTime IssueDate          { get; set; }
    public DateTime? DueDate           { get; set; }

    // Valores financeiros
    public decimal  TotalAmount        { get; set; }
    public decimal  NetAmount          { get; set; }   // Valor sem IVA
    public decimal  IvaRate            { get; set; }   // Ex: 0.23 para 23%
    public decimal  IvaAmount          { get; set; }   // Valor do IVA
    public string   Currency           { get; set; } = "EUR";

    // Status e classificação
    public InvoiceStatus Status        { get; set; } = InvoiceStatus.Draft;
    public double   ConfidenceScore    { get; set; } = 1.0;  // Score OCR 0.0-1.0
    public string?  Category           { get; set; }  // Categoria do documento

    // Fornecedor (desnormalizado para queries rápidas)
    public string?  VendorName         { get; set; }  // Nome directo sem JOIN
    public string?  VendorTaxId        { get; set; }  // NIF do fornecedor

    // Pagamento
    public string?  PaymentReference   { get; set; }  // Referência MB/IBAN
    public string?  PaymentEvidenceUrl { get; set; }  // URL comprovante de pagamento
    public DateTime? PaidAt            { get; set; }  // Data do pagamento

    // Origem
    public string?  SourceEmail        { get; set; }  // Email de origem
    public string?  SourceType         { get; set; }  // "email" | "whatsapp" | "upload"
    public string?  Filename           { get; set; }  // Nome do ficheiro original
    public string?  RawDocumentUrl     { get; set; }  // URL do documento original

    // Vectorização
    public bool     IsVectorized       { get; set; } = false;  // Já foi para o banco vectorial
    public string?  VectorId           { get; set; }  // ID no banco vectorial (Qdrant)

    public Guid VendorId               { get; set; }
    public Vendor? Vendor              { get; set; }
    public ICollection<InvoiceItem> Items { get; set; } = new List<InvoiceItem>();
}
