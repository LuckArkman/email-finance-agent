using Microsoft.EntityFrameworkCore;

namespace Hermes.ReviewQueue;

public class ReviewDbContext : DbContext
{
    public ReviewDbContext(DbContextOptions<ReviewDbContext> options) : base(options)
    {
    }

    public DbSet<PendingReview> PendingReviews { get; set; }
    public DbSet<AuditLog> AuditLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<PendingReview>()
            .HasIndex(p => p.DocumentId)
            .IsUnique();
            
        modelBuilder.Entity<PendingReview>()
            .HasIndex(p => p.IsResolved);
    }
}
