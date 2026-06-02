using System.Threading.Tasks;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public interface IEventBus
{
    Task PublishAsync<T>(T @event) where T : IntegrationEvent;
}
