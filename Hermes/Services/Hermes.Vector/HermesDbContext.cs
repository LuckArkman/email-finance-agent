using Microsoft.EntityFrameworkCore;

namespace Hermes.Vector;

public class HermesDbContext : DbContext
{
    public HermesDbContext(DbContextOptions<HermesDbContext> options) : base(options)
    {
    }

    public DbSet<InvoiceEntity> Invoices { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Ativação crucial da extensão pgvector no PostgreSQL!
        modelBuilder.HasPostgresExtension("vector");

        modelBuilder.Entity<InvoiceEntity>()
            .HasIndex(i => i.TenantId);

        modelBuilder.Entity<InvoiceEntity>()
            .HasIndex(i => i.DocumentId)
            .IsUnique();
    }
}
