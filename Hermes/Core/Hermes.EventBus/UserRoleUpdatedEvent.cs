using System;
using Hermes.EventBus.Events;

namespace Hermes.EventBus;

public record UserRoleUpdatedEvent(Guid UserId, Guid RoleId) : IntegrationEvent;
