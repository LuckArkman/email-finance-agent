using System;
using System.Threading.Tasks;
using Hermes.Domain.Common;
using Hermes.Domain.Tenancy;
using Hermes.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace Hermes.Infrastructure.Tests;

public class TestEntity : BaseEntity
{
    public string Name { get; set; } = string.Empty;
}

public class TestDbContext : HermesDbContext
{
    public TestDbContext(DbContextOptions<HermesDbContext> options, ITenantProvider tenantProvider) : base(options, tenantProvider) { }
    public DbSet<TestEntity> TestEntities { get; set; }
}

public class HermesDbContextTests
{
    [Fact]
    public async Task SaveChangesAsync_Should_Set_UpdatedAt()
    {
        // Arrange
        var mockProvider = new Moq.Mock<ITenantProvider>();
        mockProvider.Setup(x => x.GetCurrentTenant()).Returns(new TenantContext { TenantId = Guid.NewGuid() });

        var options = new DbContextOptionsBuilder<HermesDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        using var context = new TestDbContext(options, mockProvider.Object);
        var entity = new TestEntity { Name = "Test" };

        // Act
        context.TestEntities.Add(entity);
        await context.SaveChangesAsync();

        // Delay to ensure the time difference is measurable (UpdatedAt)
        await Task.Delay(10);
        
        entity.Name = "Updated Name";
        await context.SaveChangesAsync();

        // Assert
        Assert.NotNull(entity.UpdatedAt);
        Assert.True(entity.UpdatedAt > entity.CreatedAt);
    }
}
