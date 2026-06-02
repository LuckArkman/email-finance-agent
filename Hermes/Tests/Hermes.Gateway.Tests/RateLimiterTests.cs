using System.Net;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace Hermes.Gateway.Tests;

public class RateLimiterTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public RateLimiterTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task RateLimiter_Should_Return_429_When_Limit_Exceeded()
    {
        // Arrange
        var client = _factory.CreateClient();
        HttpStatusCode lastStatusCode = HttpStatusCode.OK;

        // Act - The limit is 100 requests per minute
        for (int i = 0; i < 105; i++)
        {
            var response = await client.GetAsync("/api/hermes/test-rate-limit");
            lastStatusCode = response.StatusCode;
            
            if (lastStatusCode == HttpStatusCode.TooManyRequests)
            {
                break;
            }
        }

        // Assert
        Assert.Equal(HttpStatusCode.TooManyRequests, lastStatusCode);
    }
}
