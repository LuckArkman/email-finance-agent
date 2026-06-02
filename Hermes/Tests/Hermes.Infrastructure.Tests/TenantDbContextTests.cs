using System;
using System.Linq;
using System.Threading.Tasks;
using Hermes.Domain.Tenancy;
using Hermes.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Moq;
using Xunit;

namespace Hermes.Infrastructure.Tests;

public class TenantDbContextTests
{
    [Fact]
    public async Task DbContext_Should_Filter_By_TenantId()
    {
        // Arrange
        var tenantIdA = Guid.NewGuid();
        var tenantIdB = Guid.NewGuid();
        
        var mockProviderA = new Mock<ITenantProvider>();
        mockProviderA.Setup(x => x.GetCurrentTenant()).Returns(new TenantContext { TenantId = tenantIdA });
        
        var mockProviderB = new Mock<ITenantProvider>();
        mockProviderB.Setup(x => x.GetCurrentTenant()).Returns(new TenantContext { TenantId = tenantIdB });

        var options = new DbContextOptionsBuilder<HermesDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;

        // Populate with Tenant A context
        using (var contextA = new TestDbContext(options, mockProviderA.Object))
        {
            contextA.TestEntities.Add(new TestEntity { Name = "Tenant A Data" });
            await contextA.SaveChangesAsync();
        }

        // Populate with Tenant B context
        using (var contextB = new TestDbContext(options, mockProviderB.Object))
        {
            contextB.TestEntities.Add(new TestEntity { Name = "Tenant B Data" });
            await contextB.SaveChangesAsync();
        }

        // Act - Read with Tenant A context
        using (var contextARead = new TestDbContext(options, mockProviderA.Object))
        {
            var results = await contextARead.TestEntities.ToListAsync();
            
            // Assert
            Assert.Single(results);
            Assert.Equal("Tenant A Data", results.First().Name);
            Assert.Equal(tenantIdA, results.First().TenantId);
        }
    }
}
