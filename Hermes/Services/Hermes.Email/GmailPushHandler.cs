using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;

namespace Hermes.Email;

public static class GmailPushHandler
{
    public static void MapGmailWebhooks(this Microsoft.AspNetCore.Routing.IEndpointRouteBuilder routes)
    {
        routes.MapPost("/api/webhooks/gmail", async (HttpContext context, ILogger<Program> logger) =>
        {
            // O payload do Google Pub/Sub Push envia a mensagem embrulhada
            // Pode conter { "message": { "data": "base64...", "messageId": "123" }, "subscription": "..." }
            
            using var reader = new StreamReader(context.Request.Body);
            var body = await reader.ReadToEndAsync();
            
            logger.LogInformation("Received Google Pub/Sub Push Notification.");

            // Aqui deveríamos extrair a 'emailAddress' e 'historyId' da message.data codificada em Base64.
            // Para simplificar, quando recebemos o push, mandamos processar:
            // var factory = context.RequestServices.GetRequiredService<GmailServiceFactory>();
            // await factory.ProcessUnreadEmailsAsync("target@email.com", context.RequestAborted);
            
            // O Pub/Sub exige sempre que retorne 200 OK ou 201/202 ou 102
            return Results.Ok();
        });
    }
}
