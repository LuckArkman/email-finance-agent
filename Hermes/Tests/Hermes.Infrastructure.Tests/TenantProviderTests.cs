using System;
using Hermes.Infrastructure.Tenancy;
using Microsoft.AspNetCore.Http;
using Moq;
using Xunit;

namespace Hermes.Infrastructure.Tests;

public class TenantProviderTests
{
    [Fact]
    public void GetCurrentTenant_Should_Return_TenantId_From_Header()
    {
        // Arrange
        var tenantId = Guid.NewGuid();
        var mockHttpContextAccessor = new Mock<IHttpContextAccessor>();
        var mockHttpContext = new Mock<HttpContext>();
        var mockRequest = new Mock<HttpRequest>();
        var headers = new HeaderDictionary { { "X-Tenant-ID", tenantId.ToString() } };
        
        mockRequest.Setup(r => r.Headers).Returns(headers);
        mockHttpContext.Setup(c => c.Request).Returns(mockRequest.Object);
        mockHttpContextAccessor.Setup(x => x.HttpContext).Returns(mockHttpContext.Object);

        var provider = new HttpTenantProvider(mockHttpContextAccessor.Object);

        // Act
        var result = provider.GetCurrentTenant();

        // Assert
        Assert.Equal(tenantId, result.TenantId);
    }

    [Fact]
    public void GetCurrentTenant_Should_Return_Empty_If_No_Header()
    {
        // Arrange
        var mockHttpContextAccessor = new Mock<IHttpContextAccessor>();
        var mockHttpContext = new Mock<HttpContext>();
        var mockRequest = new Mock<HttpRequest>();
        var headers = new HeaderDictionary();
        
        mockRequest.Setup(r => r.Headers).Returns(headers);
        mockHttpContext.Setup(c => c.Request).Returns(mockRequest.Object);
        mockHttpContextAccessor.Setup(x => x.HttpContext).Returns(mockHttpContext.Object);

        var provider = new HttpTenantProvider(mockHttpContextAccessor.Object);

        // Act
        var result = provider.GetCurrentTenant();

        // Assert
        Assert.Equal(Guid.Empty, result.TenantId);
    }
}
