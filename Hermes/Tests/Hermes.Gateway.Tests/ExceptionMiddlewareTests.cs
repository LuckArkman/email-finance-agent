using System.Net;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Gateway.Tests;

public class ExceptionMiddlewareTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public ExceptionMiddlewareTests(WebApplicationFactory<Program> factory)
    {
        // To test the exception middleware properly without breaking other tests,
        // we can override the factory to map an endpoint that throws an exception.
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.Configure(app =>
            {
                // Notice we inject the middleware we are building directly to test its behavior
                app.UseMiddleware<Hermes.Gateway.Middlewares.ExceptionMiddleware>();
                app.Run(context =>
                {
                    if (context.Request.Path == "/throw")
                    {
                        throw new System.Exception("Simulated exception for testing");
                    }
                    return Task.CompletedTask;
                });
            });
        });
    }

    [Fact]
    public async Task ExceptionMiddleware_Should_Catch_Exception_And_Return_500()
    {
        var client = _factory.CreateClient();
        
        var response = await client.GetAsync("/throw");
        
        Assert.Equal(HttpStatusCode.InternalServerError, response.StatusCode);
        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("Internal Server Error", content);
    }
}
