using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Pgvector;

namespace Hermes.Vector;

public class InvoiceEntity
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    public Guid TenantId { get; set; }

    [Required]
    public Guid DocumentId { get; set; }

    [MaxLength(255)]
    public string Vendor { get; set; } = string.Empty;

    [MaxLength(50)]
    public string Nif { get; set; } = string.Empty;

    public DateTime? InvoiceDate { get; set; }

    [Column(TypeName = "decimal(18, 2)")]
    public decimal TotalAmount { get; set; }

    // RAG Semantic Search Embedding Field
    [Column(TypeName = "vector(768)")] // nomic-embed-text dimensions
    public Pgvector.Vector? Embedding { get; set; }

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
