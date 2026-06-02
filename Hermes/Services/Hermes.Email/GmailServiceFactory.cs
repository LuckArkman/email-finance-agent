using System;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Gmail.v1;
using Google.Apis.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Hermes.Email;

public class GmailServiceFactory
{
    private readonly ILogger<GmailServiceFactory> _logger;
    private readonly IConfiguration _configuration;

    public GmailServiceFactory(ILogger<GmailServiceFactory> logger, IConfiguration configuration)
    {
        _logger = logger;
        _configuration = configuration;
    }

    public GmailService CreateService(string userEmail)
    {
        var credentialsPath = _configuration["Google:CredentialsFilePath"];
        if (string.IsNullOrEmpty(credentialsPath) || !File.Exists(credentialsPath))
        {
            _logger.LogWarning("Google Credentials File Path not configured or missing.");
            throw new FileNotFoundException("Google credentials file not found.");
        }

        // Domain-wide Delegation: a Service Account atua em nome do utilizador 'userEmail'
        var credential = GoogleCredential.FromFile(credentialsPath)
            .CreateScoped(GmailService.Scope.GmailModify)
            .CreateWithUser(userEmail);

        return new GmailService(new BaseClientService.Initializer
        {
            HttpClientInitializer = credential,
            ApplicationName = "Hermes.Email"
        });
    }

    public async Task ProcessUnreadEmailsAsync(string targetUserEmail, CancellationToken cancellationToken)
    {
        try
        {
            var service = CreateService(targetUserEmail);

            // Procurar mensagens "unread" que tenham anexo
            var request = service.Users.Messages.List(targetUserEmail);
            request.Q = "is:unread has:attachment";

            var response = await request.ExecuteAsync(cancellationToken);
            if (response.Messages == null || !response.Messages.Any())
            {
                return;
            }

            foreach (var messageItem in response.Messages)
            {
                var msgRequest = service.Users.Messages.Get(targetUserEmail, messageItem.Id);
                var fullMessage = await msgRequest.ExecuteAsync(cancellationToken);

                _logger.LogInformation($"Processing Gmail Message ID: {fullMessage.Id}");

                // Extração dos Attachments (simplificada)
                if (fullMessage.Payload?.Parts != null)
                {
                    foreach (var part in fullMessage.Payload.Parts.Where(p => !string.IsNullOrEmpty(p.Filename)))
                    {
                        var attachId = part.Body?.AttachmentId;
                        if (!string.IsNullOrEmpty(attachId))
                        {
                            var attachRequest = service.Users.Messages.Attachments.Get(targetUserEmail, fullMessage.Id, attachId);
                            var attachment = await attachRequest.ExecuteAsync(cancellationToken);

                            if (!string.IsNullOrEmpty(attachment.Data))
                            {
                                var tempPath = Path.Combine(Path.GetTempPath(), $"{fullMessage.Id}_{part.Filename}");
                                // Gmail attachment data is URL-safe Base64
                                var base64 = attachment.Data.Replace('-', '+').Replace('_', '/');
                                await File.WriteAllBytesAsync(tempPath, Convert.FromBase64String(base64), cancellationToken);
                            }
                        }
                    }
                }

                // TODO: Publicar no EventBus (Publish(new EmailReceivedEvent(...)))

                // Marcar como lido removendo a label UNREAD
                var mods = new Google.Apis.Gmail.v1.Data.ModifyMessageRequest
                {
                    RemoveLabelIds = new[] { "UNREAD" }
                };
                await service.Users.Messages.Modify(mods, targetUserEmail, fullMessage.Id).ExecuteAsync(cancellationToken);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing Gmail accounts");
        }
    }
}
