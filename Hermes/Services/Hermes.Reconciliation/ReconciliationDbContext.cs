using Microsoft.EntityFrameworkCore;

namespace Hermes.Reconciliation;

public class ReconciliationDbContext : DbContext
{
    public ReconciliationDbContext(DbContextOptions<ReconciliationDbContext> options) : base(options)
    {
    }

    public DbSet<ReconcilableInvoice> Invoices { get; set; }
    public DbSet<ReconcilableReceipt> Receipts { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        modelBuilder.Entity<ReconcilableInvoice>()
            .HasIndex(i => new { i.Nif, i.IsReconciled });

        modelBuilder.Entity<ReconcilableReceipt>()
            .HasIndex(r => new { r.Nif, r.IsReconciled });
    }
}
