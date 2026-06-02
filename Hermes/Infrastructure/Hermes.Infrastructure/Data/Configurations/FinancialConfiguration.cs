using Hermes.Domain.Financial;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Hermes.Infrastructure.Data.Configurations;

public class FinancialConfiguration : IEntityTypeConfiguration<Invoice>, IEntityTypeConfiguration<InvoiceItem>, IEntityTypeConfiguration<Vendor>
{
    public void Configure(EntityTypeBuilder<Invoice> builder)
    {
        builder.HasKey(i => i.Id);
        
        builder.Property(i => i.InvoiceNumber).HasMaxLength(100).IsRequired();
        builder.Property(i => i.TotalAmount).HasPrecision(18, 2);
        builder.Property(i => i.Currency).HasMaxLength(10);
        
        // Enum to String Conversion
        builder.Property(i => i.Status)
            .HasConversion<string>()
            .HasMaxLength(50);

        // Relationships
        builder.HasOne(i => i.Vendor)
            .WithMany(v => v.Invoices)
            .HasForeignKey(i => i.VendorId)
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasMany(i => i.Items)
            .WithOne(item => item.Invoice)
            .HasForeignKey(item => item.InvoiceId)
            .OnDelete(DeleteBehavior.Cascade);
    }

    public void Configure(EntityTypeBuilder<InvoiceItem> builder)
    {
        builder.HasKey(i => i.Id);
        
        builder.Property(i => i.Description).HasMaxLength(500).IsRequired();
        builder.Property(i => i.Quantity).HasPrecision(18, 4);
        builder.Property(i => i.UnitPrice).HasPrecision(18, 2);
        builder.Property(i => i.LineTotal).HasPrecision(18, 2);
    }

    public void Configure(EntityTypeBuilder<Vendor> builder)
    {
        builder.HasKey(v => v.Id);
        
        builder.Property(v => v.Name).HasMaxLength(200).IsRequired();
        builder.Property(v => v.TaxId).HasMaxLength(50);
        builder.Property(v => v.Address).HasMaxLength(1000);
        builder.Property(v => v.ContactEmail).HasMaxLength(255);
    }
}
