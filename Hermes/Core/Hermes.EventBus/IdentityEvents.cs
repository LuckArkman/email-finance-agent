using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record UserLoggedInEvent(Guid UserId, string Email) : IntegrationEvent;

public record UserRegisteredEvent(Guid UserId, string Email, string FirstName) : IntegrationEvent;
