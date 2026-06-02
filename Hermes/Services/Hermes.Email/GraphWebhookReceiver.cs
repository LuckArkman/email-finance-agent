using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Mvc;

namespace Hermes.Email;

public static class GraphWebhookReceiver
{
    public static void MapGraphWebhooks(this Microsoft.AspNetCore.Routing.IEndpointRouteBuilder routes)
    {
        routes.MapPost("/api/webhooks/graph", async (
            HttpContext context,
            [FromQuery] string? validationToken,
            ILogger<Program> logger) =>
        {
            // 1. Handshake de validação do Microsoft Graph
            if (!string.IsNullOrEmpty(validationToken))
            {
                logger.LogInformation($"Received validation token: {validationToken}");
                return Results.Text(validationToken, "text/plain");
            }

            // 2. Receção das notificações de novos e-mails (Push)
            // Aqui parseamos a notificação para saber que email foi recebido
            // Para simplificar, quando recebemos uma notificação, podemos fazer trigger 
            // de um background job (ex: GraphApiClient.ProcessUnreadEmailsAsync).
            
            logger.LogInformation("Received Microsoft Graph Webhook Push Notification.");

            // Retornamos 202 Accepted o mais rapidamente possível ao Graph
            return Results.Accepted();
        });
    }
}
