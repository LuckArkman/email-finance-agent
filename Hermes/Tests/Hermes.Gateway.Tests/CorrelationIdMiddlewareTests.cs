using System.Net;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;
using System.Linq;
using System.Threading.Tasks;

namespace Hermes.Gateway.Tests;

public class CorrelationIdMiddlewareTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public CorrelationIdMiddlewareTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory;
    }

    [Fact]
    public async Task Middleware_Should_Inject_CorrelationId_In_Response()
    {
        var client = _factory.CreateClient();
        var response = await client.GetAsync("/api/hermes/test-correlation");

        Assert.True(response.Headers.Contains("X-Correlation-ID"));
        var correlationId = response.Headers.GetValues("X-Correlation-ID").FirstOrDefault();
        Assert.False(string.IsNullOrEmpty(correlationId));
    }
}
