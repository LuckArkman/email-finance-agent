using System;
using System.ComponentModel.DataAnnotations;

namespace Hermes.Reconciliation;

public class ReconcilableInvoice
{
    [Key]
    public Guid DocumentId { get; set; }
    
    public Guid TenantId { get; set; }
    public string VendorName { get; set; } = string.Empty;
    public string Nif { get; set; } = string.Empty;
    public decimal TotalAmount { get; set; }
    public DateTime? InvoiceDate { get; set; }
    
    public bool IsReconciled { get; set; }
    public Guid? ReconciledWithReceiptId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class ReconcilableReceipt
{
    [Key]
    public Guid ReceiptId { get; set; }
    
    public Guid TenantId { get; set; }
    public string Iban { get; set; } = string.Empty;
    public string Nif { get; set; } = string.Empty; // Pagador ou Recebedor
    public decimal Amount { get; set; }
    public DateTime PaymentDate { get; set; }
    
    public bool IsReconciled { get; set; }
    public Guid? ReconciledWithInvoiceId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
