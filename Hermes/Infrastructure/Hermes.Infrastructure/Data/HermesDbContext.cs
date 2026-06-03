using System;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using Hermes.Domain.Common;
using Hermes.Domain.Email;
using Hermes.Domain.Identity;
using Hermes.Domain.Financial;
using Hermes.Domain.Tenancy;
using Microsoft.EntityFrameworkCore;

namespace Hermes.Infrastructure.Data;

public class HermesDbContext : DbContext
{
    private readonly ITenantProvider _tenantProvider;

    public HermesDbContext(DbContextOptions<HermesDbContext> options, ITenantProvider tenantProvider) : base(options)
    {
        _tenantProvider = tenantProvider;
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Role> Roles { get; set; }
    public DbSet<UserRole> UserRoles { get; set; }
    public DbSet<RolePermission> RolePermissions { get; set; }

    // Email
    public DbSet<LinkedEmailAccount> LinkedEmailAccounts { get; set; }

    // Financial
    public DbSet<Vendor> Vendors { get; set; }
    public DbSet<Invoice> Invoices { get; set; }
    public DbSet<InvoiceItem> InvoiceItems { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());
        
        var tenantId = _tenantProvider.GetCurrentTenant().TenantId;

        // Iterate through all entity types that inherit from BaseEntity
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(BaseEntity).IsAssignableFrom(entityType.ClrType))
            {
                // Configuração base de chaves
                modelBuilder.Entity(entityType.ClrType).HasKey(nameof(BaseEntity.Id));

                // Global Query Filter para Multi-Tenancy
                // Precisamos criar a expression tree (e => e.TenantId == tenantId) dinamicamente.
                // Mas, o EF Core avalia a property do service de modo dinâmico se a usarmos com property access
                var method = typeof(HermesDbContext).GetMethod(nameof(ConfigureGlobalFilters), System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    ?.MakeGenericMethod(entityType.ClrType);
                
                method?.Invoke(this, new object[] { modelBuilder });
            }
        }
    }

    private void ConfigureGlobalFilters<TEntity>(ModelBuilder modelBuilder) where TEntity : BaseEntity
    {
        modelBuilder.Entity<TEntity>().HasQueryFilter(e => e.TenantId == _tenantProvider.GetCurrentTenant().TenantId);
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        var currentTenantId = _tenantProvider.GetCurrentTenant().TenantId;

        foreach (var entry in ChangeTracker.Entries<BaseEntity>())
        {
            if (entry.State == EntityState.Added)
            {
                if (entry.Entity.TenantId == Guid.Empty)
                {
                    entry.Entity.TenantId = currentTenantId;
                }
            }

            if (entry.State == EntityState.Modified)
            {
                entry.Entity.UpdatedAt = DateTime.UtcNow;
            }
        }
        return base.SaveChangesAsync(cancellationToken);
    }
}
