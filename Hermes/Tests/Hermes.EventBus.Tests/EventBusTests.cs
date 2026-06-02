using System.Threading.Tasks;
using Hermes.EventBus.Events;
using Moq;
using Xunit;

namespace Hermes.EventBus.Tests;

public class EventBusTests
{
    [Fact]
    public async Task PublishAsync_Should_Call_EventBus_Successfully()
    {
        // Arrange
        var mockEventBus = new Mock<IEventBus>();
        var systemStartedEvent = new SystemStartedEvent { Message = "Test" };

        mockEventBus.Setup(x => x.PublishAsync(systemStartedEvent))
                    .Returns(Task.CompletedTask)
                    .Verifiable();

        // Act
        await mockEventBus.Object.PublishAsync(systemStartedEvent);

        // Assert
        mockEventBus.Verify(x => x.PublishAsync(It.IsAny<SystemStartedEvent>()), Times.Once);
    }
}
