using System.Net.Http;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Moq;
using Xunit;
using Hermes.EventBus;

namespace Hermes.Tests.Integration;

public class IntegrationTestFixture : IClassFixture<WebApplicationFactory<Hermes.Notifications.Program>>
{
    private readonly WebApplicationFactory<Hermes.Notifications.Program> _factory;

    public IntegrationTestFixture(WebApplicationFactory<Hermes.Notifications.Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Substituir o EventBus real por um Mock para evitar dependência do RabbitMQ local
                var mockEventBus = new Mock<IEventBus>();
                services.AddSingleton(mockEventBus.Object);
            });
        });
    }

    [Fact]
    public void Notification_Hub_Should_Initialize_Without_Errors()
    {
        // Act
        var client = _factory.CreateClient();

        // Assert
        Assert.NotNull(client);
    }
}
