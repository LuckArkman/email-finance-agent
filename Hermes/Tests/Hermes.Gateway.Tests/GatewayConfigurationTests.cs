using System.Net;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace Hermes.Gateway.Tests;

public class GatewayConfigurationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public GatewayConfigurationTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Gateway_Should_Return_Security_Headers()
    {
        // Arrange
        var client = _factory.CreateClient();

        // Act
        // We'll call a random route to see if security headers are appended by the middleware
        var response = await client.GetAsync("/any-route");

        // Assert
        Assert.True(response.Headers.Contains("X-XSS-Protection"));
        Assert.True(response.Headers.Contains("X-Content-Type-Options"));
        
        var xssHeader = response.Headers.GetValues("X-XSS-Protection").FirstOrDefault();
        var contentOptionsHeader = response.Headers.GetValues("X-Content-Type-Options").FirstOrDefault();
        
        Assert.Equal("1; mode=block", xssHeader);
        Assert.Equal("nosniff", contentOptionsHeader);
    }
}
