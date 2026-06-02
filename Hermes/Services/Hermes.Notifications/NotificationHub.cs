using System;
using System.Collections.Generic;
using System.Security.Claims;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Logging;
using Hermes.Notifications.Services;

namespace Hermes.Notifications;

[Authorize]
public class NotificationHub : Hub
{
    private readonly ILogger<NotificationHub> _logger;
    private readonly IAgentStreamService _agentService;

    public NotificationHub(ILogger<NotificationHub> logger, IAgentStreamService agentService)
    {
        _logger = logger;
        _agentService = agentService;
    }

    public IAsyncEnumerable<string> StreamChat(IEnumerable<ChatMessageDto> messages, [EnumeratorCancellation] CancellationToken cancellationToken)
    {
        _logger.LogInformation($"Client {Context.ConnectionId} requested StreamChat.");
        return _agentService.StreamChatAsync(messages, cancellationToken);
    }

    public override async Task OnConnectedAsync()
    {
        var tenantId = Context.User?.FindFirst("TenantId")?.Value;

        if (string.IsNullOrEmpty(tenantId))
        {
            _logger.LogWarning($"User {Context.ConnectionId} connected without TenantId claim. Closing connection.");
            Context.Abort();
            return;
        }

        // Segregação de Tenants! Todos os sockets do Tenant ficam no mesmo grupo isolado.
        await Groups.AddToGroupAsync(Context.ConnectionId, tenantId);

        _logger.LogInformation($"Client {Context.ConnectionId} authenticated and added to Tenant Group: {tenantId}");
        
        await base.OnConnectedAsync();
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        var tenantId = Context.User?.FindFirst("TenantId")?.Value;

        if (!string.IsNullOrEmpty(tenantId))
        {
            await Groups.RemoveFromGroupAsync(Context.ConnectionId, tenantId);
            _logger.LogInformation($"Client {Context.ConnectionId} disconnected from Tenant Group: {tenantId}");
        }

        await base.OnDisconnectedAsync(exception);
    }
}
